## 🧩 Level 14: Gatekeeper Two
### 🔒 Goal
Become the `entrant` by passing three tricky gates, each designed to block naive contract interaction.

---
### 🔍 Contract Summary

```solidity
function enter(bytes8 _gateKey) public gateOne gateTwo gateThree(_gateKey) returns (bool);
```
Three gate modifiers block this function:

🔐 Gate One
- Ensures you're calling from a contract, not an EOA.
- ✅ Solution: Call from an attacker contract.

🔐 Gate Two
- extcodesize(caller()) is 0 during constructor execution of a contract.
- ✅ Solution: Call enter() from the constructor of your attacker contract.

🔐 Gate Three
- Use XOR to derive the _gateKey
---
### 🚀 Exploit Strategy
1. Write GatekeeperTwoAttacker contract.
2. Inside the constructor:
- Compute gateKey using XOR method.
- Call gatekeeper.enter(gateKey);
3. Deploy the attacker from your wallet.
---
### 🧠 Real-World Takeaways
#### 🔬 extcodesize() as a Defensive Tool
The extcodesize() opcode reveals the code size at a given address. It returns 0 during a contract's constructor, which has these real-world implications:
- Anti-Bot Protection: DApps check if msg.sender has no code — filtering bots that interact immediately after deployment.
- Flash Loan / MEV Defense: Prevent temporary contracts from manipulating state within one atomic transaction.
- Whitelist Enforcement: Primitive EOA detection (not foolproof) — by rejecting contracts.
- Constructor-only Initialization: Used in upgradable proxies to restrict critical logic to the constructor.
