# 🧩 Ethernaut Level 25: Motorbike
#### Difficulty: 🔥🔥🔥🔥
#### Category: Proxy patterns, delegatecall, Upgradeability, Storage Slots, EVM Internals
## Overview

This level explores how the Universal Upgradeable Proxy Standard (UUPS) works under the hood, and how an insecure upgrade pattern combined with unprotected initialization can permanently destroy the logic contract. The player interacts with a proxy called Motorbike, which delegates all logic to a contract called Engine. The goal is to render the proxy unusable — a condition achieved by exploiting its upgradeability mechanism and executing a selfdestruct operation on the implementation contract.

---
## 📜 Challenge Summary
The `Motorbike` contract is a minimal proxy that forwards calls to the `Engine` contract using `delegatecall`. The Engine follows the UUPS pattern and includes a `function upgradeToAndCall(address newImplementation, bytes memory data)`. This mechanism allows the implementation to upgrade itself and immediately execute additional logic in the same call.

The Engine contract also has an `initialize()` function that sets the `upgrader`. However, since the implementation is deployed independently and not initialized within a constructor (as is typical in proxies), the `initialize()` function is callable by anyone. This exposes a critical vulnerability: anyone can become the upgrader.

The challenge consists of the following steps:
- Extract the implementation address from the proxy's storage using the standardized EIP-1967 storage slot.
- Become the upgrader by calling initialize() on the implementation directly.
- Deploy a malicious contract that contains a selfdestruct() method.
- Use upgradeToAndCall() to upgrade to the malicious contract and call its explode() function, destroying the implementation logic.
- Confirm that the proxy is now unusable, as it delegates to a destroyed contract.
---
### 🔐 What if the upgrader had already been set?
If the Ethernaut setup had already initialized the Engine contract and set the upgrader to a non-attacker address (like 0xdeadbeef...), then **this challenge would be uncrackable by design**.  
Here’s why:
- You wouldn't be able to call initialize(), because it has the initializer modifier, which uses a storage flag to ensure it can be called only once.
- Without being the upgrader, you cannot call upgradeToAndCall(), since it requires msg.sender == upgrader.
- You also cannot replace or bypass the upgrade logic, since the Engine logic is hardcoded in the proxy’s EIP-1967 slot, and you don’t control the proxy either.

Therefore:
> ✅ The entire exploit hinges on the fact that the `Engine` contract has not yet been initialized.

This is an important real-world lesson. In UUPS-style proxies:
- The implementation must be initialized before the proxy is set up, or protected using constructor+salt deployment tricks.
- If it's left uninitialized, any attacker can take over the upgrade path and destroy or rewire the system.
---
## Key Concepts and Techniques
### EIP-1967 and Proxy Storage Slots
EIP-1967 defines standardized storage slots for proxies to avoid collisions with the implementation’s storage. For the implementation address, the slot is:
```arduino
bytes32(uint256(keccak256("eip1967.proxy.implementation")) - 1)
= 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc
```
Reading this slot from the proxy reveals the address of the current implementation.
### UUPS Proxies and Upgrade Safety
Unlike transparent proxies, UUPS proxies embed the upgrade logic inside the implementation itself. This makes the proxy thinner and more efficient but also places greater responsibility on the implementation to control upgrade access.

In this level, the Engine contract allows upgrades via upgradeToAndCall() and initialization via initialize(). If initialize() is not protected with a modifier like initializer, then any user can take control and trigger arbitrary upgrades.

### delegatecall and selfdestruct
The proxy uses delegatecall, meaning the context of execution is preserved — storage and msg.sender refer to the proxy. However, when calling the implementation directly, execution happens in the implementation's own context.

The selfdestruct(address) opcode is a low-level EVM instruction that deletes a contract's bytecode and sends its balance to a recipient. If the Engine is selfdestructed, the proxy will still forward calls to its address — but with no code to execute, rendering the proxy broken.

---
### 🛠️ Python Exploit (web3.py)
Please check `solution_motorbike.py`.

---
## 🧠 Security Lessons
- **Initialization must be protected**. Contracts used as implementations in proxies should ensure that initialize() is callable only once, typically using initializer from OpenZeppelin’s Initializable base.
- **UUPS proxies require careful design**. Because the logic for upgradeability is placed inside the implementation, any lapse in access control is fatal.
- **Never assume constructor safety**. Proxy-compatible implementations cannot rely on constructors to initialize critical variables. This must be done via external initialize() functions — and they must be access-controlled.
- **Storage slot standards prevent collisions**. EIP-1967 offers a standard method for managing proxy state and retrieving implementation addresses safely.
---
## ✍️ Author

defi-dojo – A curated collection of real-world smart contract exploit simulations, automated testing, and in-depth technical writeups.

Created and maintained with ❤️ by [yprakash](mailto:yprakash.518@gmail.com).