# 🛸 Level 19: Alien Codex (Solidity 0.5.0)

**Category:** Storage Manipulation / Underflows / Insecure Inheritance  
**Difficulty:** Hard  
**Goal:** Claim ownership of the contract using a storage manipulation exploit.
---

## 🧩 Challenge Overview

This challenge demonstrates how **deep understanding of Solidity storage layout** and EVM internals can be used to overwrite privileged state variables — even without any obvious bugs in the contract logic.

The target contract uses a dynamic array (`codex`) to store data and assumes its size and indexing are secure. However, due to an outdated Solidity compiler and careless use of array underflows, an attacker can exploit the layout to overwrite the contract's owner address.

Key restrictions:
- Solidity version is **0.5.0**, meaning:
  - Dynamic arrays allow `.length--`
  - Storage packing and layout are less safe
- We don’t have access to newer tooling or OpenZeppelin upgrades
- The challenge forces us to understand **how Solidity lays out state variables in storage**

---
## 🔍 Step-by-Step Strategy
### 1. **Trigger the `contacted` modifier**

```solidity
function make_contact() public {
    contact = true;
}
```
Calling make_contact() flips a boolean and lets us interact with codex.

But here's the twist: both owner (inherited) and contact are stored in slot 0.

In Solidity 0.5.0:
- address owner takes 20 bytes
- bool contact takes 1 byte
- Solidity packs them together into slot 0

So:
- contact modifies the high-order byte
- owner sits in the lower 20 bytes of the same slot

Calling make_contact() sets contact = true, but corrupts owner. This breaks access control — and sets the stage for overwriting the entire slot.

---
### 2. Exploit underflow in the array length
In Solidity 0.5.0, .length-- is legal. If codex.length was 0, this sets it to: `codex.length = 2^256 - 1`  
Now we can write to any storage slot using codex[index] = value.

---
### 3. Understand how arrays are stored
In Solidity:
- Slot 1 holds codex.length
- The array data is stored at:
```
keccak256(1) → base_slot
```
Then:
```
codex[0] → slot = base_slot
codex[1] → slot = base_slot + 1
...
```
This layout allows us to reverse-engineer the index needed to overwrite slot 0.

---
## 🧠 Reverse Engineering the Index (to overwrite owner)
```text
Storage Slots Overview (simplified to 100 slots)

Slot     Content
─────    ──────────────────────────────
0        owner (20 bytes) + contact (1 byte)
1        codex.length
...
50       codex[0]
51       codex[1]
...

We want to overwrite slot 0 via codex[index]

So:
codex[index] → writes to slot: keccak256(1) + index

To target slot 0:
keccak256(1) + index ≡ 0 mod 2^256
⇒ index = 2^256 - keccak256(1)

🧮 Python:
base_slot = int.from_bytes(w3.keccak(b'\x01'.rjust(32, b'\x00')), 'big')
index = (2**256 - base_slot)

codex[index] = padded_attacker_address
→ directly overwrites slot 0 (i.e., owner)
```
---
## 🧠 Takeaways
| Concept                  | Insight                                                     |
| ------------------------ | ----------------------------------------------------------- |
| Solidity Storage Layout  | Variables may share slots — especially `bool` and `address` |
| Array Layout             | Data stored at `keccak256(slot)`                            |
| Underflow Exploit        | Dynamic arrays in 0.5.0 can underflow and enable OOB writes |
| Arbitrary Storage Writes | Index math lets you write to any slot, including `owner`    |

---
### 🚀 Deployment and Execution Using Python

Please check `solution_aliencodex.py`

---
## 🛡️ Defense Recommendations
- Always use modern compilers. This bug depends on pre-0.6.0 underflow behavior.
- Avoid exposing length-- or low-level array manipulation to untrusted users.
- Use OpenZeppelin's SafeMath or native overflow checks (Solidity >=0.8.0) to prevent arithmetic underflows.
- Treat dynamic array internals as sensitive — prevent user control over storage layout.

---
## ✍️ Author

defi-dojo – A curated collection of real-world smart contract exploit simulations with automated testing and writeups.

Created and maintained with ❤️ by [yprakash](mailto:yprakash.518@gmail.com).