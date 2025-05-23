# 🧪 Ethernaut Level 23: Dex Two – Fake Liquidity, Real Exploit

## 📜 Challenge Summary
In this challenge, we're presented with a modified version of the previous Dex contract. The key difference? The contract is not validating whether the tokens used in the swap operation are the same tokens it was initialized with. This introduces a critical vulnerability that we can exploit.

We're successful if we manage to drain all of at least one token from the DEX. Let’s get into it.

---
### 🧠 What You’re Given
- A DEX with two ERC20 tokens (token1, token2)
- 100 of each token in DEX liquidity
- 10 of each token in your wallet
- You can call swap(from, to, amount) directly
- DEX calculates swap price as:
```solidity
(amount * toTokenBalanceInDex) / fromTokenBalanceInDex
```
⚠️ No check that from and to are only token1 or token2. You can bring your own ERC20.

---
## 🚩 Vulnerability
The DEX blindly accepts any ERC20 token you give it. Since the price is calculated from internal DEX balances, we can:
- Deploy our own ERC20 token (let’s call it MalToken)
- Transfer a small amount of MalToken to the DEX, causing the DEX’s reserve of MalToken to appear nonzero
- Use 1 MalToken to drain all of token1, because the swap formula will calculate a huge return due to imbalance
- Do the same to drain all of token2

This is a token spoofing and price manipulation attack.

---
## 🧠 Key Takeaways
- Trust but verify: Always validate external tokens and inputs.
- Internal price oracles are dangerous when attacker-controlled tokens can skew ratios.
- This is a classic token spoofing + price manipulation exploit.
- The absence of a loop here is intentional: two swaps are enough to drain both tokens because each MalToken swap gives full access to DEX reserves.
---
## ✍️ Author

defi-dojo – A curated collection of real-world smart contract exploit simulations, automated testing, and in-depth technical writeups.

Created and maintained with ❤️ by [yprakash](mailto:yprakash.518@gmail.com).