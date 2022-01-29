from scripts.helpful_scripts import get_accounts, get_contract, config, fund_with_link
from brownie import Lottery, network
import time


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()


def deploy_lottery():
    print(f"network : {network.show_active()}")
    get_accounts(id="my_firefox")
    # lottery = Lottery.deploy({"from": get_accounts()})
    account = get_accounts()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed"),
        get_contract("vrf_coordinator"),
        get_contract("link_token"),
        config["networks"][network.show_active()]["keyhash"],
        config["networks"][network.show_active()]["fee"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("Deployed lottery!")
    return lottery


def start_lottery():
    account = get_accounts()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(1)
    print("Started lottery!")


def enter_lottery():
    account = get_accounts()
    lottery = Lottery[-1]
    enter_tx = lottery.enter(
        {"from": account, "value": lottery.getEntranceFee() + 100000000}
    )
    enter_tx.wait(1)
    print("You entered a lottery!")


def end_lottery():
    account = get_accounts()
    lottery = Lottery[-1]
    # fund the contract
    # end the contract
    tx = fund_with_link(lottery.address)
    tx.wait(1)
    ending_tx = lottery.endLottery({"from": account})
    ending_tx.wait(1)
    time.sleep(180)
    print(f"{lottery.recentWinner()} is the new winner")
