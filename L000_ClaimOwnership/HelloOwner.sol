// SPDX-License-Identifier: MIT

pragma solidity ^0.8.29;

contract HelloOwner {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function claimOwnership() public {
        owner = msg.sender;
    }

    function isOwner() public view returns (bool) {
        return msg.sender == owner;
    }
}
