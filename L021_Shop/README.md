# 🛒 Ethernaut Level 21: Shop

> Difficulty: ★★★☆☆ Medium  
> Category: Smart Contract Interfaces, View Functions, Inheritance Tricks
---
## 🧠 Challenge Goal

Make the `isSold` flag `true` and reduce the shop's `price` to a value **less than 100**.

The contract relies on an interface:

```solidity
interface Buyer {
    function price() external view returns (uint);
}
```
The Shop contract calls buy() on itself, passing a Buyer contract as msg.sender. The trick lies in how it invokes Buyer.price() twice, expecting consistent results — but we’re going to exploit that assumption.

---
### 🤯 Key Insight: View Functions Aren't Always Pure
At first, we tend to use something like a toggle flag
```solidity
bool private toggle;
function price() external returns (uint) {
    toggle = !toggle;
    return toggle ? 101 : 1;
}
```
But the Buyer interface defines price() as a view function. Solidity strictly enforces that your implementation must also be view. You can't change contract state (like toggling a flag) in a view function.

The trick is to return different values based on whether the item has been sold — which we can query without violating view: `target.isSold() ? 1 : 101;`

This satisfies the interface, mutates no local state, and works beautifully.

---
## 🪓 View Functions as an Attack Vector
This challenge elegantly demonstrates:
- That view functions can still vary based on external state (like querying another contract)
- Solidity’s strict interface enforcement around view and pure
- How attackers can exploit naive assumptions about function determinism
---
## ✍️ Author

defi-dojo – A curated collection of real-world smart contract exploit simulations, automated testing, and in-depth technical writeups.

Created and maintained with ❤️ by [yprakash](mailto:yprakash.518@gmail.com).