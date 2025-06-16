## 🔁 Level 10 — Re-entrancy: The Recursive Trap

### 🔒 Challenge Description
The contract in this level manages Ether balances and allows users to deposit and withdraw their funds. However, it contains a critical flaw in the `withdraw()` function that makes it vulnerable to a **re-entrancy attack**.

An attacker can exploit this to **drain all funds from the contract**, even if they only deposited a small amount.

---
### 💥 Vulnerability

The contract transfers Ether using `.call()` **before** updating the user’s balance. This violates the [Checks-Effects-Interactions pattern](https://fravoll.github.io/solidity-patterns/checks_effects_interactions.html).

A malicious contract can:
1. Call `withdraw()`
2. Receive Ether → trigger fallback
3. Call `withdraw()` again (before balance is updated)
4. Repeat recursively
---
### 🧠 Learning Objectives

- Understand how re-entrancy works
- Learn why **state updates must happen before external calls**
- See how **attack contracts recursively drain funds**
- Practice exploiting with **web3.py** and **Foundry**
---
### 🧯 Mitigation

To fix this, the contract should:
- **Update state before** making external calls
- Or use **pull-based withdrawal patterns** (`withdraw()` must be initiated by user, not pushed by the contract)
- Or consider using **reentrancy guards** like `nonReentrant` from [OpenZeppelin’s ReentrancyGuard](https://docs.openzeppelin.com/contracts/4.x/api/security#ReentrancyGuard)
---
### ✅ Success Condition
The challenge is solved when:
- The vulnerable contract’s Ether balance is reduced to **zero**
- The attacker's contract balance has increased by the **total funds held**
---
