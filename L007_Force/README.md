🧠 Force – Challenge Objective

The contract has:
- **No `receive()` or `fallback()`**
- **No `payable` functions**
- **0 ETH balance**

You must:
> Send ETH to the contract *anyway*, proving that Solidity contracts can receive Ether without explicitly allowing it.

⚔️ Vulnerability Insight

The challenge demonstrates a lesser-known but powerful EVM behavior:
- Contracts can receive ETH via **`selfdestruct`**, regardless of their code.
- `selfdestruct(address)` transfers the contract's entire balance to the given address — **bypassing any fallback logic**.

---

🧨 Exploit Summary

1. Deploy a simple attacker contract with some ETH:
   ```solidity
   selfdestruct(target);
2. On destruction, the ETH is force-sent to the target contract.
3. The Ethernaut level checks the contract has a non-zero balance — and passes!

🚀 Key Takeaways
- selfdestruct is a low-level opcode that can force ETH transfers, even to contracts that don’t accept ETH.
- Relying on payable functions or receive() to prevent ETH receipt is not sufficient.
- Always validate balance-sensitive logic carefully — don’t assume a contract can’t receive ETH.

✍️ Author

defi-dojo – A curated collection of real-world smart contract exploit simulations with automated testing and writeups.

Created and maintained with ❤️ by yprakash.