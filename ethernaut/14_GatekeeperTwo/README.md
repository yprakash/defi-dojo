# 🧩 Level 14: Gatekeeper Two
**Difficulty:** Medium  
**Category:** Access Control / Obfuscated Logic
---
### 🧩 Overview

This level demonstrates how complex-looking but poorly-designed access control logic can be bypassed with clever typecasting and contract initialization tricks.

The goal is to become the `entrant` in the `GatekeeperTwo` contract by passing through three tightly-coded "gates". No admin keys or vulnerabilities are exposed — just obscured logic that requires a deep understanding of the EVM, `extcodesize`, and bitwise operations.

---
### 🔓 Vulnerability Explained

The contract enforces three conditions in the `enter()` function:
```solidity
modifier gateOne() {
    require(msg.sender != tx.origin);
    _;
}

modifier gateTwo() {
    uint256 x;
    assembly { x := extcodesize(caller()) }
    require(x == 0);
    _;
}

modifier gateThree(bytes8 _gateKey) {
    require(uint64(bytes8(keccak256(abi.encodePacked(msg.sender)))) ^ uint64(_gateKey) == type(uint64).max);
    _;
}
```
### 🔒 Goal
Become the `entrant` by passing three tricky gates, each designed to block naive contract interaction.
```solidity
function enter(bytes8 _gateKey) public gateOne gateTwo gateThree(_gateKey) returns (bool);
```
Three gate modifiers block this function:

🔐 Gate One

This ensures only contracts (not EOAs) can call enter(). Simple to bypass: just deploy an attacker contract.

🔐 Gate Two

This checks that the caller **has no code**, i.e. `extcodesize(msg.sender) == 0`.

Here’s the twist: when a contract is being constructed, its code isn’t yet stored on-chain. So during its constructor execution, extcodesize(this) returns 0. This allows us to call enter() from the constructor of our attacker contract.

🔐 Gate Three
```solidity
uint64(keccak256(msg.sender)) ^ gateKey == 0xFFFFFFFFFFFFFFFF
```
Solving this means:
```python
gate_key = uint64(keccak256(address)) ^ 0xFFFFFFFFFFFFFFFF
```

This is simple to compute off-chain (or in the constructor) using Python or Solidity bitwise operations.

---
### 🚀 Exploit Strategy
1. Write GatekeeperTwoAttacker contract.
2. Inside the constructor:
- Compute gateKey using XOR method.
- Call gatekeeper.enter(gateKey);
3. Deploy the attacker from your wallet.
---
### 🛡️ How to Defend
- Avoid using `extcodesize()` as a proxy for trust. Contracts under construction can always exploit this logic.
- **Do not design gates that rely on initialization-phase quirks** — these can almost always be bypassed with deployment-time exploits.
- Use **authentication** (roles, signatures, proofs) instead of obscurity.
---
### 📘 Lessons Learned
- `extcodesize(this)` is 0 during contract construction. A classic pitfall for Solidity devs.
- Bitwise tricks can be reversed. Any XOR gate can be brute-forced or computed if the output is known.
- Contracts can call others in their constructor. This opens the door to many initialization-phase exploits — also relevant in proxy patterns.
---
### ✅ Summary
This challenge teaches how code obfuscation is not security. Obscure constraints can be reverse-engineered and bypassed with a clear understanding of Solidity internals and the EVM — especially around contract deployment.

---
## ✍️ Author

defi-dojo – A curated collection of real-world smart contract exploit simulations, automated testing, and in-depth technical writeups.

Created and maintained with ❤️ by [yprakash](mailto:yprakash.518@gmail.com).