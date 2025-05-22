# 🧙‍♂️ Ethernaut Level 18: MagicNumber

## 🧩 Challenge Summary

The `MagicNum` contract expects a solver contract that returns the number `42` when called. But there's a twist: we can't use standard Solidity. Instead, we must deploy a **minimal contract using raw bytecode** — no high-level language, no compiler.

This challenge is a deep dive into **EVM internals**, testing your understanding of **stack operations**, **memory layout**, and **contract deployment** using just opcodes.

---

## ✅ Goal

- Deploy a contract that returns `42` when called.
- Keep the bytecode **as minimal as possible**.
- Use `setSolver()` on the MagicNum contract to register your deployed contract.

---

### 👨‍💻 What We'd Normally Write in Solidity

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Solver {
    function whatIsTheMeaningOfLife() public pure returns (uint256) {
        return 42;
    }
}
```
This works — but it's far too big. The compiled runtime code is ~100+ bytes. We need something much smaller.

---
### 🧠 How Solidity Gets Compiled (Behind the Scenes)
When Solidity compiles the above function, it generates EVM bytecode that does three things:
- Pushes 42 onto the stack
- Stores it in memory
- Returns it as a 32-byte word

Why 32 bytes? Because EVM always operates with 256-bit values (uint256), and expects return values to be padded to 32 bytes.

To mimic this manually, we need to understand the EVM stack and memory model:
- PUSH1 0x2a — pushes 42 onto the stack
- PUSH1 0x00 — where to store it in memory
- MSTORE — stores 42 as a 32-byte word at memory offset 0
- PUSH1 0x20 — number of bytes to return
- PUSH1 0x00 — starting at memory offset 0
- RETURN — returns the memory slice

This gives us the runtime code:
```
602a60005260206000f3
```
### 🧩 Opcode Breakdown

| Opcode  | Meaning                                 |
| ------- | --------------------------------------- |
| `60 2a` | PUSH1 0x2a        → Push 42 onto stack  |
| `60 00` | PUSH1 0x00        → Memory offset 0     |
| `52`    | MSTORE            → Store 42 at mem\[0] |
| `60 20` | PUSH1 0x20        → Return 32 bytes     |
| `60 00` | PUSH1 0x00        → From offset 0       |
| `f3`    | RETURN            → Return the value    |

Only 10 bytes long. But we still need to deploy it.

---
### 🔧 Crafting the Creation Bytecode

To deploy a contract, you don’t directly store runtime code — you store creation code that returns the runtime code. So we need creation bytecode that, when run, returns the above runtime bytecode and stores it as the actual contract code.

Here’s the smallest creation code that does that:
```
69602a60005260206000f3600052600a6016f3
```
### 🧩 Creation Bytecode Breakdown
| Opcode                 | Meaning                                     |
| ---------------------- | ------------------------------------------- |
| `69`                   | PUSH10 (runtime code)                       |
| `602a60005260206000f3` | The runtime code (10 bytes)                 |
| `60 00`                | PUSH1 0x00 → Memory offset 0                |
| `52`                   | MSTORE → Store runtime code at mem\[0]      |
| `60 0a`                | PUSH1 0x0a → Code size = 10 bytes           |
| `60 16`                | PUSH1 0x16 → Offset = 22 (start of runtime) |
| `f3`                   | RETURN → Return the runtime code            |

---
## 🚀 Deployment and Execution Using Python

Please check `solution_magicnum.py`

---
## ✍️ Author

defi-dojo – A curated collection of real-world smart contract exploit simulations with automated testing and writeups.

Created and maintained with ❤️ by [yprakash](mailto:yprakash.518@gmail.com).