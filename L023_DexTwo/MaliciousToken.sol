// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./ERC20.sol";

contract MaliciousToken is ERC20 {
    constructor(uint256 initialSupply) ERC20("MaliciousToken", "MAL") {
        _mint(msg.sender, initialSupply);
    }
}