from brownie import network, accounts, MockV3Aggregator, config

LOCAL_BLOCKCHAIN_NETWORKS = ["mainnet-fork", "development"]


def get_accounts(index=None, id=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_NETWORKS:
        return accounts[0]
    if id:
        return accounts.load(id)
    config["wallets"]["from-key"]


DECIMALS = 8
PRICE = 200000000000


def get_contract():
    print(f"The active network is {network.show_active()}")
    if network.show_active() in LOCAL_BLOCKCHAIN_NETWORKS:
        if len(MockV3Aggregator) <= 0:
            mockV3Aggregator = MockV3Aggregator.deploy(
                DECIMALS, PRICE, {"from": get_accounts()}
            )
            return mockV3Aggregator.address
    else:
        return config["networks"][network.show_active()]["eth-usd-price-feed"]
