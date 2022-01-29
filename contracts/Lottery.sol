//SPDX-License-Identifier: MIT

pragma solidity =0.8.8;

import "@chainlink-brownie-contracts/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin-contracts/contracts/access/Ownable.sol";
import "@chainlink-brownie-contracts/contracts/src/v0.8/VRFConsumerBase.sol";

//import "@hardhat/console.sol";

contract Lottery is Ownable, VRFConsumerBase {
    address payable[] public players;
    uint256 public usdEntryFee;
    AggregatorV3Interface internal ethUsdPriceFeed;
    address payable public recentWinner;
    uint256 public randomness;

    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state;
    uint256 public fee;
    bytes32 public keyHash;

    //event Decimal(uint8 baseDecimals);
    //mapping(bytes32 => address) internal RequestIdToAddress;
    //event RequestIdToAddressEvent(bytes32 indexed requestId, address caller);
    event RequestedRandomness(bytes32 requestId);

    constructor(
        address _priceFeedAddress,
        address _vrf_coordinator,
        address _link_token,
        bytes32 _keyHash,
        uint256 _fee
    ) VRFConsumerBase(_vrf_coordinator, _link_token) {
        lottery_state = LOTTERY_STATE.CLOSED;
        usdEntryFee = 50 * 10**18;
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        fee = _fee;
        keyHash = _keyHash;
    }

    function enter() public payable {
        require(lottery_state == LOTTERY_STATE.OPEN);
        require(msg.value >= getEntranceFee());
        players.push(payable(msg.sender));
        // payable(msg.sender).transfer(msg.value); //update
    }

    //Converting entryFee from USD to Ether
    function getEntranceFee() public view returns (uint256) {
        (, int256 price, , , ) = ethUsdPriceFeed.latestRoundData();
        uint8 baseDecimals = ethUsdPriceFeed.decimals();
        //emit Decimal(baseDecimals);

        //Since this already has 8 decimal places per https://docs.chain.link/docs/ethereum-addresses/
        uint256 adjustedPrice = scalePrice(price, baseDecimals);
        uint256 entryFee = (usdEntryFee * 10**18) / adjustedPrice;
        return entryFee;
    }

    function scalePrice(int256 price, uint8 baseDecimals)
        internal
        view
        returns (uint256)
    {
        return uint256(price) * 10**(18 - baseDecimals);
    }

    function startLottery() public onlyOwner {
        require(
            lottery_state == LOTTERY_STATE.CLOSED,
            "Can't start a new lottery yet!"
        );
        lottery_state = LOTTERY_STATE.OPEN;
    }

    function endLottery() public onlyOwner {
        require(lottery_state == LOTTERY_STATE.OPEN);
        // uint256(
        //     keccak256(
        //         abi.encodePacked(
        //             nonce, //predictable
        //             msg.sender, // predictable
        //             block.difficulty, //Can be manipulated by the miners
        //             block.timestamp //predictable
        //         )
        //     )
        // ) % players.length;

        lottery_state == LOTTERY_STATE.CALCULATING_WINNER;
        bytes32 requestId = requestRandomness(keyHash, fee);
        emit RequestedRandomness(requestId);
    }

    //Chainlink node is calling the VRF Coordinator which is calling the fulfillRandomness function so we are marking these as internal
    //Override means we are overriding the original declaration of this function
    function fulfillRandomness(bytes32 _requestId, uint256 _randomness)
        internal
        override
    {
        require(lottery_state == LOTTERY_STATE.CALCULATING_WINNER);
        require(_randomness > 0, "random-not-found");
        uint256 winnerIndex = _randomness % players.length;
        recentWinner = players[winnerIndex];
        recentWinner.transfer(address(this).balance);

        //Reset
        players = new address payable[](0); //size 0
        lottery_state = LOTTERY_STATE.CLOSED;
        randomness = _randomness;
    }
}
