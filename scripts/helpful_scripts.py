from brownie import (
    network,
    accounts,
    MockV3Aggregator,
    config,
    Contract,
    VRFCoordinatorMock,
    LinkToken,
    Contract,
    interface,
)

LOCAL_BLOCKCHAIN_NETWORKS = ["mainnet-fork", "development"]


def get_accounts(index=None, id=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_NETWORKS:
        return accounts[0]
    if id:
        return accounts.load(id)
    return accounts.add(config["wallets"]["from-key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    """
    This function will grab the contract addresses from brownie config if defined, otherwise, it will deploy a mock version fo the contract, and return the mock contract.

        Args: Contract_name(string)

        Returns: brownie.network.contract.ProjectContract : The most recently deployed version of this contract
        MockV3Aggregator[-1] contract
    """
    contract_type = contract_to_mock[contract_name]
    print(f"The active network is {network.show_active()}")
    if network.show_active() in LOCAL_BLOCKCHAIN_NETWORKS:
        if len(MockV3Aggregator) <= 0:
            deploy_mocks()
        contract = contract_type[-1]  # MockV3Aggregator[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )  # MockV3Aggregator._name, contract_address form config, MockV3Aggregator.abi
    return contract


DECIMALS = 8
INITIAL_VALUE = 200000000000


def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    MockV3Aggregator.deploy(decimals, initial_value, {"from": get_accounts()})
    link_token = LinkToken.deploy({"from": get_accounts()})
    VRFCoordinatorMock.deploy(link_token, {"from": get_accounts()})
    print("Mocks deployed")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):
    account = account if account else get_accounts()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Funded contract")
    return tx
