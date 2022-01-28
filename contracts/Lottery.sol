//SPDX-License-Identifier: MIT

pragma solidity =0.8.8;

import "@chainlink-brownie-contracts/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin-contracts/contracts/access/Ownable.sol";

//import "@hardhat/console.sol";

contract Lottery is Ownable {
    address payable[] public players;
    uint256 public usdEntryFee;
    AggregatorV3Interface internal ethUsdPriceFeed;

    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state;

    //event Decimal(uint8 baseDecimals);

    constructor(address priceFeedAddress) {
        lottery_state = LOTTERY_STATE.CLOSED;
        usdEntryFee = 50 * 10**18;
        ethUsdPriceFeed = AggregatorV3Interface(priceFeedAddress);
    }

    function enter() public payable {
        require(lottery_state == LOTTERY_STATE.OPEN);
        require(msg.value >= getEntranceFee());
        players.push(payable(msg.sender));
        payable(msg.sender).transfer(msg.value);
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
    }
}
