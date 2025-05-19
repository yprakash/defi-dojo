## Ethernaut Level 12 — Privacy

**Category:** Storage, Data Extraction  
**Objective:** Unlock the contract by discovering the hidden key.
---
### 🧠 Level Summary
The `Privacy` contract stores a locked boolean and some data in private storage variables. Your goal is to call `unlock(bytes16 _key)` with the correct key to unlock the contract.

---
### 🔍 Vulnerability
Solidity’s `private` keyword only restricts access **at the contract level**, not on-chain. All variables are stored publicly on-chain and can be read using tools like:
- Web3.py or web3.js
- Hardhat/Foundry
- Etherscan's `storageAt`
---
### 🛠️ Exploit Strategy
1. Read storage slot `5` directly (where the key is stored).
2. Truncate it from `bytes32` to `bytes16`.
3. Call the `unlock()` function with the truncated value.
---
### 🧩 Key Takeaways
- private ≠ hidden on-chain
- All contract state can be read via getStorageAt
- Type casting in Solidity follows left-alignment (bytes16(bytes32) takes the first 16 bytes)
