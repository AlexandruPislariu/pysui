#    Copyright Frank V. Castellucci
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#        http://www.apache.org/licenses/LICENSE-2.0
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

# -*- coding: utf-8 -*-

"""Testing basic client capabilities (no transactions)."""

import os
from pysui import SyncGqlClient, handle_result
from pysui.sui.sui_types.address import valid_sui_address
import pysui.sui.sui_pgql.pgql_sync_txn as tx
import pysui.sui.sui_pgql.pgql_query as qn
from tests.test_utils import gas_not_in


def test_split_transfer(sui_client: SyncGqlClient) -> None:
    """Test splitting and transfers."""

    txer = tx.SuiTransaction(client=sui_client)
    scoin = txer.split_coin(coin=txer.gas, amounts=[1000000000])
    txer.transfer_objects(transfers=[scoin], recipient=sui_client.config.active_address)
    res = sui_client.execute_query_node(
        with_node=qn.GetCoins(owner=sui_client.config.active_address)
    )
    coins = res.result_data.data
    assert len(coins) > 3
    scoin = txer.split_coin(coin=coins[0], amounts=[1000000000])
    txer.transfer_objects(transfers=[scoin], recipient=sui_client.config.active_address)
    txer.split_coin_equal(coin=coins[1], split_count=2)
    txer.transfer_sui(recipient=sui_client.config.active_address, from_coin=coins[2])


def test_merge_coin(sui_client: SyncGqlClient) -> None:
    """Test merging coins."""
    txer = tx.SuiTransaction(client=sui_client)
    res = sui_client.execute_query_node(
        with_node=qn.GetCoins(owner=sui_client.config.active_address)
    )
    coins = res.result_data.data
    assert len(coins) > 3
    txer.merge_coins(merge_to=coins[0], merge_from=coins[1:])


def test_move_vec(sui_client: SyncGqlClient) -> None:
    """."""
    txer = tx.SuiTransaction(client=sui_client)
    res = sui_client.execute_query_node(
        with_node=qn.GetCoins(owner=sui_client.config.active_address)
    )
    coins = res.result_data.data
    assert len(coins) > 3
    coin_ids = [x.coin_object_id for x in coins]
    res = txer.make_move_vector(
        items=coin_ids, item_type="0x2::coin::Coin<0x2::sui::SUI"
    )


def test_publish(sui_client: SyncGqlClient) -> None:
    """."""
    txer = tx.SuiTransaction(client=sui_client)
    cwd = os.getcwd() + "/tests/sui-test"
    txer.publish(project_path=cwd)
