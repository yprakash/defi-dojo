🧠 Delegation – Challenge Summary

This challenge revolves around a smart contract that uses delegatecall to a helper contract (Library pattern). The vulnerability lies in how delegatecall can manipulate the storage of the calling contract, including its owner.

🚀 Key Takeaways
- delegatecall is powerful but dangerous if storage layouts overlap.
- Any exposed function in the delegate contract can be exploited if blindly called.
- Always restrict and validate inputs to delegatecall usage.

💼 Why It Matters

Through this exercise, we can:
- Understand low-level EVM concepts like delegatecall.
- Can exploit storage layout collisions
- Automate smart contract attacks using both Solidity and Python

✍️ Author

defi-dojo – A curated collection of real-world smart contract exploit simulations with automated testing and writeups.

Created and maintained with ❤️ by yprakash.