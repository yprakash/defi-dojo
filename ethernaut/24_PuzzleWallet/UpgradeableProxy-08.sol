// SPDX-License-Identifier: MIT
// https://github.com/OpenZeppelin/ethernaut/blob/master/contracts/src/helpers/UpgradeableProxy-08.sol

pragma solidity ^0.8.0;

import "./Proxy.sol";

contract UpgradeableProxy is Proxy {
    constructor(address _logic, bytes memory _data) {
        assert(_IMPLEMENTATION_SLOT == bytes32(uint256(keccak256("eip1967.proxy.implementation")) - 1));
        _setImplementation(_logic);
        if (_data.length > 0) {
            (bool success,) = _logic.delegatecall(_data);
            require(success);
        }
    }

    bytes32 private constant _IMPLEMENTATION_SLOT = 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc;

    function _implementation() internal view override returns (address impl) {
        bytes32 slot = _IMPLEMENTATION_SLOT;
        assembly {
            impl := sload(slot)
        }
    }

    function _upgradeTo(address newImplementation) internal {
        _setImplementation(newImplementation);
    }

    function _setImplementation(address newImplementation) private {
        // require(Address.isContract(newImplementation), "UpgradeableProxy: new implementation is not a contract");

        bytes32 slot = _IMPLEMENTATION_SLOT;
        assembly {
            sstore(slot, newImplementation)
        }
    }
}