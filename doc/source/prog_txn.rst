Programmable Transactions
=========================

General
-------
``pysui`` supports programmable transactions using the SuiTransaction (sync or async) herein referred to as
SuiTransaction or Transaction.

A SuiTransaction supports building adding one or more commands with inputs. When executed, if any indivudal command fails the entire
transaciton is rolled back.

A few powerful advantages of this capability include:

    * A more expresive batch transaction
    * Both `public`` **and** `public entry` functions can be called on a Sui Move contract
    * If one command produces a result (e.g. `split_coin`), that result may be used as an argument to one or more subsequent commands
    * And more...

The ``pysui`` Implementation
----------------------------

The ``pysui`` SuiTransaction's commands are similar to `Sui TS SDK <https://docs.sui.io/devnet/build/prog-trans-ts-sdk>`_ but do have
differences:

    * Encapsulates additional high level commands, such as `stake_coin`, `unstake_coin`, `split_coin_equal` and `publish_upgrade`
    * Transaction methods have a high degree of flexibility in providing different arguments types

Getting Started
################
SuiTransactions encapsulate a SuiClient, transaction sender and/or sponsors for signing, gas objects, inspection and execution
methods as well as the ability to add one or more commands.

For asynchronous transactions, SuiTransactionAsync encapsulates a asynch SuiClient and is in parity with thes
sycnronous counterpart. Basically, most methods on the asynch family are called with ``await``.

All examples that follow use the synchronous SuiClient and SuiTransaction.

Quick example
~~~~~~~~~~~~~
This requires providing an instantiated SuiClient.

.. code-block:: Python

    from pysui import SyncClient, SuiConfig, handle_result
    from pysui.sui.sui_txn import SyncTransaction

    def foo():
        """Demonstrates a simple SuiTransaction ."""

        # Get the Transaction/Transaction Builder
        # By default, this will assume that the 'active-address' is the sender and sole signer of the transaction
        # However; support for MultiSig signers and Sponsoring transactions is also supported

        txn = SyncTransaction(client=SyncClient(SuiConfig.default_config()))

        # Get a few objects to use as command arguments

        coin_to_split = ... # Retrieved somehow
        some_recipient = ... # Retrieve non-active-address somehow

        # Command that first splits a coin for some amount and uses
        # the results to pass to some recipient

        txn.transfer_objects(
            transfers=[txn.split_coin(coin=coin_to_split, amounts=[1000000])],
            recipient=some_recipient,
        )

        # Execute will use active-address to sign, pick a gas coin
        # that satisfies the budget. An inspection is done internally
        # and the budget will automatically adjust to the higher when compared

        tx_result = handle_result(txn.execute(gas_budget="1000000"))
        print(tx_result.to_json(indent=2))

Commands available
##################

Basic commands:
    * move_call
    * transfer_objects, transfer_sui, public_transfer_object
    * split_coin, split_coin_equal, split_coin_and_return
    * make_move_vector
    * publish, publish_upgrade, custom_upgrade
    * stake_coin, unstake_coin

Inspection
##########

You can verify (inspect) a SuiTransaction as you are building out your transactions. See: :py:meth:`pysui.sui.sui_txn.sync_transaction.SuiTransaction.inspect_all`

Gas for Transaction Payment
###########################

Obviously, the transaction must be paid for. This can be either the 'sender' of the transaction or a 'sponsor'. By default,
when creating a new SuiTransaction the 'sender' is the confirugration current active-address and will look for gas objects from
that account. However; you can optionally identify a sponsor in which case that account will be responsible for the gas objects for
payment.

The following shows variations which will determine where ``pysui`` resolves the gas payment.

.. code-block:: Python

    # Imports
    from pysui import SyncClient, SuiConfig, handle_result
    from pysui.sui.sui_txn import SyncTransaction

    # Standard setup for synchronous client and transaction
    cfg = SuiConfig.default_config()
    client = SyncClient(cfg)

    # Will default to 'active-address' as the sender and also who pays for the transaction

    txer = SyncTransaction(client=client)

    # Construct with a different address as the 'sender',
    # the initial_sender will be who pays for the transaction

    txer = SyncTransaction(client=client,initial_sender=SuiAddress("0x......"))

    # Construct default and set different sender on the signers block before execution

    txer = SyncTransaction(client=client)
    txer.signer_block.sender = SuiAddress("0x......")

    # Construct default and set different sponsor on the signers block before execution
    # The sponsor is who pays for the transaction

    txer = SyncTransaction(client=client)
    txer.signer_block.sponsor = SuiAddress("0x......")


More details below in the Singer, Singers, etc. section.

Serialize and Deserialize
#########################

A SuiTransaction state can be serialized and deserialized.

This is handy for re-using a well defined transaction with commands and inputs and not
going through building a transaction from scratch each time.

Serialize
~~~~~~~~~

When you serialize a SuiTransaction, the following is contained:

    * Sender and/or Sponsor settings (single or multisig)
    * Transaction builder instrumentation
    * Set of objects in use at the time of serialization
    * All transaction block commands and inputs

The SuiTransaction `serialize` method returns a python byte string. Conversley the `deserialize` method takes
a byte string as input.

The SuiTransaction constructor also has a convenient optional argument `deserialize_from` where you can
provide either a byte string or a base64 str.

Deserialize
~~~~~~~~~~~

Note that when you deserialize (either through constructor or after construction through the `deserialize` method):

    * It resets the sender and/or sponsor to those inbound from deserializing
    * It resets the Transaction builder instrumentation to that inbound from deserializing
    * It resets the set of objects in use to those inbound from deserializing
    * It resets all inputs and commands to those inbound from deserializing


Execution
#########

You can execute the transaction directly:

#. :py:meth:`pysui.sui.sui_txn.sync_transaction.SuiTransaction.execute`

Note that once you execute a transaction you can not longer add commands and re-execute it.

Signing, Signers, etc.
######################

SuiTransactions have a property called `signature_block` that manages the potential signers of a transaction:
    * Sender - This can be an SuiAddress or a SigningMultiSig (wrapper over MultiSig address)
    * Sponsor - This can be an SuiAddress or a SigningMultiSig (wrapper over MultiSig address)

SigningMultiSig
~~~~~~~~~~~~~~~

To use MultiSig in transactions, a decorator class `SigningMultiSig` is used. It consists two parts:
    * MultiSig - As described in previous topic
    * SuiPublicKey - A list of one or more public keys associated to the MultiSig keypairs

The transaction, by default, uses the active-address as the sender/signer. To use a SigningMultiSig you
must set it as sender in transaction creation or prior to execution.

The examples below demonstrate the approaches.

.. code-block:: Python

    def split_init_with_multi_sig():
        """Initiate a transaction with a multisig SigningMultiSig decorator."""
        cfg = SuiConfig.default_config()
        client = SyncClient(cfg)

        # Get a multi-sig
        msig: MultiSig = ...
        # Get subset of MultiSig SuiPublic keys
        msig_pubkeys: list[SuiPublicKey] = ...

        # Construct the transaction with the SigningMultiSig
        txer = SyncTransaction(client=client,initial_sender=SigningMultiSig(msig, msig_pubkeys))

        # Split and transfer
        split_coin = txer.split_coin(coin=txer.gas,amounts=[10000000000])
        txer.transfer_objects(transfers=[split_coin],recipient=msig.as_sui_address)

        # Execute
        result = handle_result(txer.execute(gas_budget="2000000"))

        print(f"Coin split to self {msig.address} success")
        print(result.to_json(indent = 2))

.. code-block:: Python

    def split_with_multi_sig_pre_execution():
        """Transaction sets sender of multisig SigningMultiSig decorator prior to execution."""
        cfg = SuiConfig.default_config()
        client = SyncClient(cfg)

        # Get a multi-sig
        msig: MultiSig = ...
        # Get subset of MultiSig SuiPublic keys
        msig_pubkeys: list[SuiPublicKey] = ...

        # Construct the SigningMultiSig
        sender_msig = SigningMultiSig(msig, msig_pubkeys)

        # Construct the transaction with default sender
        txer = SyncTransaction(client=client)

        # Split and transfer
        split_coin = txer.split_coin(coin=txer.gas,amounts=[10000000000])
        txer.transfer_objects(transfers=[split_coin],recipient=msig.as_sui_address)

        # Set the sender as multisig
        txer.signer_block.sender = sender_msig

        # Execute
        result = handle_result(txer.execute(gas_budget="2000000"))

        print(f"Coin split to self {msig.address} success")
        print(result.to_json(indent = 2))

Sponsored Transaction example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here is an example of a transaction that is sponsored. It, as well, may be set to a SigningMultiSig although
this example uses a simple SuiAddress:

.. code-block:: Python

    from pysui import SyncClient, SuiConfig, handle_result
    from pysui.sui.sui_txn import SyncTransaction

    def sponsored_split():
        """Demonstrates a simple sponsored SuiTransaction ."""

        # Get the Transaction/Transaction Builder
        # By default, this will assume that the 'active-address' is the sole signer of the transaction
        # But we want to sponsor the transaction from another address (who will pay for the transaction)

        txer = SyncTransaction(client=SyncClient(SuiConfig.default_config()))

        # Get a coin for splitting from the active-address and create the command
        coin_to_split = ... # Retrieved somehow
        txer.split_coin_equal(coin=main_coin, split_count=3)

        # But for execution we want the gas to come from a sponsoring address
        # and they sign as well
        some_sponsor = ... # Retrieve another address that will 'pay' for the transaction
        txer.signer_block.sponser = SuiAddress(some_sponsor)

        exec_result = handle_result(txer.execute(gas_budget="1000000"))
        print(exec_result.to_json(indent=2))

Command Inputs and Arguments
############################

Command Inputs
~~~~~~~~~~~~~~

``pysui`` encapsulate the the lower level details inputs to command parameters or move_call arguments. For the most part,
all of the input variations on what 'type' of Pythoon or ``pysui`` type the command will accept can be seen for each Command
method in :py:class:`pysui.sui.sui_txn.sync_transaction.SuiTransaction` reference.

Move Call Arguments
~~~~~~~~~~~~~~~~~~~

However; the `arguments` to a Move Call command **_may_** require special treatment to aid in disambiguating whether it is an object
reference or just a pure value. Here is a snippet of a move call where arguments are wrapped in ``pysui`` types. Below the
example is a coercion table describing the effect of resolving in `move_call` arguments.

.. code-block:: Python

    txer.move_call(
        target="0x0cce956e2b82b3844178b502e3a705dead7d2f766bfbe35626a0bbed06a42e9e::marketplace::buy_and_take",
        arguments=[
            ObjectID("0xb468f361f620ac05de721e487e0bdc9291c073a7d4aa7595862aeeba1d99d79e"),
            ObjectID("0xfd542ebc0f6743962077861cfa5ca9f1f19de8de63c3b09a6d9d0053d0104908"),
            ObjectID("0x97db1bba294cb30ce116cb94117714c64107eabf9a4843b155e90e0ae862ade5"),
            SuiAddress(coin_object_id),
            ObjectID(coin_object_id),
            SuiU64(1350000000),
        ],
        type_arguments=[
            "0x3dcfc5338d8358450b145629c985a9d6cb20f9c0ab6667e328e152cdfd8022cd::suifrens::SuiFren<0x3dcfc5338d8358450b145629c985a9d6cb20f9c0ab6667e328e152cdfd8022cd::capy::Capy>",
            "0x2::sui::SUI",
        ],
    )


+----------------------------------------------------------+-----------------------------+
|     Types                                                |       Converts to           |
+==========================================================+=============================+
| str, SuiString                                           | Passed as vector<u8>        |
+----------------------------------------------------------+-----------------------------+
| int, SuiInteger                                          | Passed as minimal bit value |
+----------------------------------------------------------+-----------------------------+
| bool, bytes, SuiBoolean                                  | Passed as raw value         |
+----------------------------------------------------------+-----------------------------+
| SuiU8, SuiU16, SuiU32, SuiU64, SuiU128, SuiU256          | Passed as value  [#f1]_     |
+----------------------------------------------------------+-----------------------------+
| list, SuiArray [#f2]_                                    | Members passed as values    |
+----------------------------------------------------------+-----------------------------+
| OptionalU8, OptionalU16, OptionalU32,                    |                             |
| OptionalU64, OptionalU128, OptionalU256                  | Passed as Optional<uX>      |
+----------------------------------------------------------+-----------------------------+
| SuiAddress                                               | Passed as move address      |
+----------------------------------------------------------+-----------------------------+
| ObjectID, SuiCoinObject, ObjectRead                      | Passed as reference [#f3]_  |
+----------------------------------------------------------+-----------------------------+
| Result of previous command [#f4]_                        | Command Result index        |
+----------------------------------------------------------+-----------------------------+

.. rubric:: Footnotes

.. [#f1] Explicit unsigned integer bit size types
.. [#f2] Members must be scalars, SuiAddresses or results of previous commands. For Object vectors use :py:meth:`pysui.sui.sui_clients.transaction.SuiTransaction.make_move_vector`
.. [#f3] Will determine if Shared object or not before transaction execution
.. [#f4] Result may be a list, so understanding which commands return a zero, 1 or multiple(list) is important

Command Notes
#############

Publishing
~~~~~~~~~~

Not available if using :py:meth:`pysui.sui.sui_config.SuiConfig.user_config`

Common Results
++++++++++++++

Whether publishing or upgrading a package, knowledge of the published package ID and/or UpgradeCap is likely
useful for the author to know. Here is a simple function that executes the transaction and returns both
the package ID and UpgradeCap id (whether the cap is default or custom):

.. code-block:: Python

    def transaction_run(txb: SyncTransaction):
        """Example of simple executing a SuiTransaction."""
        # Set sender if not done already
        if not txb.signer_block.sender:
            txb.signer_block.sender = txb.client.config.active_address

        # Execute the transaction
        tx_result = txb.execute(gas_budget="100000")
        if tx_result.is_ok():
            if hasattr(tx_result.result_data, "to_json"):
                print(tx_result.result_data.to_json(indent=2))
            else:
                print(tx_result.result_data)
        else:
            print(tx_result.result_string)


    def publish_and_result(txb: SyncTransaction, print_json=True) -> tuple[str, str]:
        """Example of running the publish commands in a SuiTransaction and retrieving important info."""
        # Set the sender if not already sent.
        # Not shown is optionally setting a sponsor as well
        if not txb.signer_block.sender:
            txb.signer_block.sender = txb.client.config.active_address

        # Execute the transaction
        tx_result = txb.execute(gas_budget="100000")
        package_id: str = None
        upgrade_cap_id: str = None

        if tx_result.is_ok():
            if hasattr(tx_result.result_data, "to_json"):
                # Get the result data and iterate through object changes
                tx_response: TxResponse = tx_result.result_data
                for object_change in tx_response.object_changes:
                    match object_change["type"]:
                        # Found our newly published package_id
                        case "published":
                            package_id = object_change["packageId"]
                        case "created":
                            # Found our newly created UpgradeCap
                            if object_change["objectType"].endswith("UpgradeCap"):
                                upgrade_cap_id = object_change["objectId"]
                        case "mutated":
                            # On upgrades, UpgradeCap is mutated
                            if object_change["objectType"].endswith("UpgradeCap"):
                                upgrade_cap_id = object_change["objectId"]
                        case _:
                            pass
                if print_json:
                    print(tx_response.to_json(indent=2))
            else:
                print(f"Non-standard result found {tx_result.result_data}")
        else:
            print(f"Error encoundered {tx_result.result_string}")
        return (package_id, upgrade_cap_id)



Publish Method
++++++++++++++

SuiTransaction provides :py:meth:`pysui.sui.sui_txn.sync_transaction.SuiTransaction.publish`. Note that the
result of the command is the UpgradeCap and it must be transfered to an owner.

.. code-block:: Python

    def publish_package(client: SyncClient = None):
        """Sample straight up publish of move contract returning UpgradeCap to current address."""
        client = client if client else SyncClient(SuiConfig.default_config())

        # Initiate a new transaction
        txer = SyncTransaction(client=client)

        # Create a publish command
        upgrade_cap = txer.publish(project_path="<ABSOLUTE_OR_RELATIVE_PATH_TO_PACKAGE_PROJECT>")

        # Transfer the upgrade cap to my address
        txer.transfer_objects(transfers=[upgrade_cap], recipient=client.config.active_address)

        # Convenience method to sign and execute transaction and fetch useful information
        package_id, cap_id = publish_and_result(txer, False)
        print(f"Package ID: {package_id}")
        print(f"UpgradeCap ID: {cap_id}")

Publish Upgrade Method
++++++++++++++++++++++

SuiTransaction provides :py:meth:`pysui.sui.sui_txn.sync_transaction.SuiTransaction.publish_upgrade`. This will perform
standard authorize, publish and commit steps. See custom upgrade below if you have specialized policies.

Example assumes you've taken necessary steps to prepare the package source for upgrading.

.. code-block:: Python

    def upgrade_package(client: SyncClient = None):
        """Sample batteries included package upgrade."""
        client = client if client else SyncClient(SuiConfig.default_config())

        # Initiate a new transaction
        txer = SyncTransaction(client=client)

        txer.publish_upgrade(
            project_path="<ABSOLUTE_OR_RELATIVE_PATH_TO_PACKAGE_PROJECT>",
            package_id=package_id, # See above Publish example for published package_id
            upgrade_cap=cap_id,    # See above Publish example for created UpgradeCap
        )
        package_id, cap_id = publish_and_result(txer, False)
        print(f"Upgraded Package ID: {package_id}")
        print(f"Versioned UpgradeCap ID: {cap_id}")



Custom Upgrade Method
++++++++++++++++++++++

SuiTransaction provides :py:meth:`pysui.sui.sui_txn.sync_transaction.SuiTransaction.custom_upgrade`. This is a
high order function (HOF) that calls the authors *custom authorization*, then performs the publish and then again
calls an authors *custom commit* function.

In general, custom upgrades involve:

    * Having a custom upgrade policy package separate from the packages governed by it
    * Publishing an initial version of a move package that will be governed by the custom policy package
    * Using the custom policy package, generate an authorized upgrade ticket if governance rules allow
    * Publishing the authorized upgrade and creating a receipt
    * Commiting the upgraded move package using it's upgraded receipt and finalizing using the custom policy controls


The example function below follows the `Sui custom upgrade policies example  <https://docs.sui.io/devnet/build/custom-upgrade-policy/>`_

.. code-block:: Python

    # First publish the policy package
    def publish_policy(client: SyncClient = None):
        """Publish a customized policy and make it's upgrade cap immutable."""
        client = client if client else SyncClient(SuiConfig.default_config())

        txer = SyncTransaction(client=client)

        # Publish policy command
        upgrade_cap = txer.publish(project_path="<ABSOLUTE_OR_RELATIVE_PATH_TO_CUSTOM_POLICY_PACKAGE>")

        # Transfer the upgrade cap to my address
        txer.transfer_objects(transfers=[upgrade_cap], recipient=client.config.active_address)

        policy_package_id, policy_cap_id = publish_and_result(txer, False)
        print(f"Policy Package ID: {policy_package_id}")
        print(f"Policy UpgradeCap ID: {policy_cap_id}")

        # New transaction
        txer = SyncTransaction(client=client)

        # Make cap immutable
        txer.move_call(
            target="0x2::package::make_immutable",
            arguments=[ObjectID(policy_cap_id)],
        )
        transaction_run(txer)

    # Next publish an initial package version
    def publish_example(client: SyncClient = None):
        """Publish the example for which upgrades will have custom governance."""
        client = client if client else SyncClient(SuiConfig.default_config())

        # New transaction
        txer = SyncTransaction(client=client)

        # Publish the example
        ex_upgrade_cap = txer.publish(project_path="~/my_move_contracts/example")

        # Transition the newly created default upgrade cap to our custom policy type
        # Restricting upgrades to Tuesdays (day 1 of week)
        mon_policy_cap = txer.move_call(
            target=policy_cap_id + "::day_of_week::new_policy",
            arguments=[ex_upgrade_cap, SuiU8(1)],
        )
        # Transfer to sender
        txer.transfer_objects(transfers=[mon_policy_cap], recipient=client.config.active_address)

        example_package_id, example_cap_id = publish_and_result(txer, False)
        print(f"Example's Package ID: {example_package_id}")
        print(f"Example's UpgradeCap ID: {example_cap_id}")

    # CUSTOM UPGRADE!!!
    # Assuming the example package has had source changes

    def custom_authorize(txer: SyncTransaction, upgrade_cap: ObjectRead, digest: bcs.Digest) -> bcs.Argument:
        """Call the Custom Policy package to authorize an upgrade and get an upgrade ticket."""
        target = policy_package_id + "::day_of_week::authorize_upgrade"

        # Return the result which is the upgrade ticket
        return txer.move_call(target=target, arguments=[upgrade_cap, SuiU8(0), digest])


    def custom_commit(txer: SyncTransaction, upgrade_cap: ObjectRead, receipt: bcs.Argument) -> bcs.Argument:
        """With the receipt from the package upgrade, commit the upgrade."""
        target = policy_package_id + "::day_of_week::commit_upgrade"
        return txer.move_call(target=target, arguments=[upgrade_cap, receipt])


    def custom_upgrade(client: SyncClient = None):
        """Call SuiTransaction HOF for custom upgrades."""
        client = client if client else SyncClient(SuiConfig.default_config())
        txer = SyncTransaction(client=client)
        txer.custom_upgrade(
            project_path="~/frankc01/example",
            package_id=example_package_id,
            upgrade_cap=example_cap_id,
            authorize_upgrade_fn=custom_authorize,
            commit_upgrade_fn=custom_commit,
        )

        example_package_id, example_cap_id = publish_and_result(txer, False)
        print(f"Example's Upgraded Package ID: {example_package_id}")
        print(f"Example's UpgradeCap ID: {example_cap_id}")
