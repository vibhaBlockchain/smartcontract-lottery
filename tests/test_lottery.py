from brownie import accounts, Lottery, config, network
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_NETWORKS,
    get_accounts,
    get_contract,
)
from web3 import Web3


"""def test_get_entrance_fee():
    account = get_accounts()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed"),
        {"from": account},
    )
    print(
        f" type of lotter and getEntranceFee, {type(lottery)}, {type(lottery.getEntranceFee())}"
    )

    assert int(lottery.getEntranceFee()) > Web3.toWei(0.018, "ether")
    assert lottery.getEntranceFee() < Web3.toWei(0.026, "ether")"""
