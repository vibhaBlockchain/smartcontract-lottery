from brownie import network, Lottery, exceptions
from scripts.helpful_scripts import (
    fund_with_link,
    get_accounts,
    get_contract,
    LOCAL_BLOCKCHAIN_NETWORKS,
)
import pytest
from scripts.deploy_lottery import deploy_lottery
from web3 import Web3


def test_get_entrance_fee():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORKS:
        pytest.skip(f"{network.show_active()} Network not in local blockchain networks")
    lottery = deploy_lottery()
    # Act
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()
    # Assert
    assert entrance_fee == expected_entrance_fee


def test_cant_enter_unless_started():
    # Arrage
    if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORKS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_accounts()
    # Act, Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": account, "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():
    # Arrage
    if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORKS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_accounts()
    entrance_fee = lottery.getEntranceFee()
    # Act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": entrance_fee})
    assert lottery.players(0) == account


def test_can_end_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORKS:
        pytest.skip()
    account = get_accounts()
    lottery = deploy_lottery()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee() + 10000000000})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    assert lottery.lottery_state() == 2


def test_can_pick_winner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORKS:
        pytest.skip
    account = get_accounts()
    lottery = deploy_lottery()
    entrance_fee = lottery.getEntranceFee()
    lottery.startLottery({"from": account})
    lottery.enter({"form": account, "value": entrance_fee})
    lottery.enter({"from": get_accounts(index=1), "value": entrance_fee})
    lottery.enter({"from": get_accounts(index=2), "value": entrance_fee})
    fund_with_link(lottery)
    starting_balance_of_account = account.balance()
    balance_of_lottery = lottery.balance()
    tx = lottery.endLottery({"from": account})
    request_id = tx.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, lottery.address, {"form": account}
    )
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance_of_account + balance_of_lottery
