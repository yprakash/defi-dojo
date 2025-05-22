# Ethernaut Challenge 20: Denial

## 🧠 Challenge Summary

The `Denial` contract allows a designated `partner` address to receive a share of ETH during withdrawals. But the function responsible for paying the partner (`partner.call("")`) forwards **all available gas** — making it ripe for exploitation.

Our job is to **grief** the owner by **burning all the gas** in the partner's fallback function so the withdrawal process fails.

---

## 🔎 Key Concepts

### 🔥 3 Ways to Transfer ETH in Solidity

| Method                          | Gas Forwarded | On Failure     | Notes                                        |
|--------------------------------|---------------|----------------|----------------------------------------------|
| `transfer(amount)`             | 2,300         | Reverts        | Safe, simple, can’t be gas-griefed           |
| `send(amount)`                 | 2,300         | Returns false  | Legacy, rarely used                          |
| `call{value: amount}("")`      | All remaining | Returns false  | Dangerous, allows reentrancy and griefing    |

> 🧠 Ethernaut uses `partner.call("")` (dangerous) and `owner.transfer(...)` (safe) **on purpose** to illustrate this contrast.

---
## 🎯 Exploit Strategy
- Deploy a malicious contract with an infinite loop in its receive() function.
- Set this malicious contract as the partner.
- When withdraw() is called, your receive() runs forever.
- Gas gets exhausted, so owner’s transfer() fails.
- Withdrawal becomes impossible — you've DoS’ed the contract.
---
## 💬 Why assert(false) Isn't Ideal

```solidity
receive() external payable {
    assert(false);
}
```
But this causes an immediate revert. It's too obvious and detectable.

The more insidious attack is to silently burn all the gas, causing withdraw() to fail without an error — making debugging and mitigation harder.

---
## 🔐 Security Lessons
- Never forward all gas to external contracts unless absolutely necessary.
- Use .call() cautiously — consider using .transfer() or .send() where appropriate.
- Be aware of gas griefing as a denial-of-service vector.
- This challenge simulates real-world DoS scenarios with external dependency injection.
> 🧠 This is a gas griefing attack, not a theft attack.  
> Your malicious partner doesn't steal ETH — it just makes sure no one else can get it either.
---
## 🧠 Final Thoughts
This challenge isn't about stealing funds — it's about blocking access to them. It teaches an important Web3 lesson: gas mechanics are part of your attack surface. A subtle misuse of .call() can turn a cooperative function into a denial-of-service vulnerability.

---
## ✍️ Author

defi-dojo – A curated collection of real-world smart contract exploit simulations with automated testing and writeups.

Created and maintained with ❤️ by [yprakash](mailto:yprakash.518@gmail.com).