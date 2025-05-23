# 🧪 Ethernaut Level 22: Dex

> **Category**: Smart Contract Exploitation  
> **Difficulty**: Medium  
> **Objective**: Drain all of *at least one* of the two ERC20 tokens from the DEX contract and exploit its flawed swap logic.
---
## 🔍 Challenge Overview

The DEX contract implements a basic token-swapping mechanism between two tokens. However, its price calculation is insecure and manipulable.
```solidity
function getSwapPrice(address from, address to, uint amount) public view returns (uint) {
    return ((amount * balanceOf(to)) / balanceOf(from));
}
```
The flaw lies in its naïve pricing formula:
- No constant product invariant (x * y = k) like Uniswap
- Prone to manipulation due to integer division
- Allows swaps to skew price ratios dramatically
---
## 🧠 Vulnerability Explained
Let’s say, You have 10 token1 and 10 token2 and DEX has 100 token1 and 100 token2.

If you start swapping back and forth — always giving just enough to take more — the price swings in your favor over time.

Example swap:
```text
swapAmount = amount * to_balance / from_balance
```
With each swap, from_balance increases, to_balance decreases → next swap gets you more.

---
## Strategy
- Approve the Dex to move our tokens
- Abuse the swap pricing logic by draining one token’s liquidity
- Repeatedly swap back and forth between Token1 and Token2
- Each swap gives you slightly more value due to imbalance
- Goal: make DEX’s balance of one token reach zero

Please check `solution_dex.py` for Execution Using Python

---
## 🧾 ERC20 Methods Used
| Method                           | Purpose                                                                      |
| -------------------------------- | ---------------------------------------------------------------------------- |
| `balanceOf(address)`             | Returns the token balance of a given address.                                |
| `transfer(to, amount)`           | Transfers tokens from `msg.sender` to another address.                       |
| `transferFrom(from, to, amount)` | Transfers tokens from one address to another, using allowance mechanism.     |
| `approve(spender, amount)`       | Grants another address (`spender`) permission to spend tokens.               |
| `allowance(owner, spender)`      | Returns remaining tokens `spender` is allowed to spend on behalf of `owner`. |

In this level, transferFrom was heavily used inside the Dex contract to pull tokens in and push tokens out during swaps.
We manually called approve() from our account to allow the DEX contract to spend our tokens on our behalf.
---
## 🧠 Key Takeaways
- Integer division in Solidity truncates decimals. Use SafeMath or fixed-point libraries in production.
- A DEX without slippage control is easily manipulable.
- Always sanity check pricing logic when building financial primitives.
- Testing price-impact exploits doesn't always require complex contracts — web3.py is enough!
---
## ✍️ Author

defi-dojo – A curated collection of real-world smart contract exploit simulations, automated testing, and in-depth technical writeups.

Created and maintained with ❤️ by [yprakash](mailto:yprakash.518@gmail.com).