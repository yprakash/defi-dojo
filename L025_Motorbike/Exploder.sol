// SPDX-License-Identifier: MIT

pragma solidity <0.7.0;

contract Exploder {
    function explode() external {
        selfdestruct(msg.sender);
    }
}
