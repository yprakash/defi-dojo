🧠 Token – Ethernaut Challenge

Category: Smart Contract Exploitation

Difficulty: Beginner

🔍 Challenge Summary

This challenge simulates a simple ERC20 token with a basic transfer function and a vulnerability in arithmetic logic. It invites you to drain all tokens from an account by exploiting a bug.

🚀 Key Takeaways
- Solidity 0.8+ introduces built-in overflow/underflow protection — a major security improvement.
- Always use SafeMath or upgrade to newer compiler versions for arithmetic safety.
- Insecure ERC20 implementations can be exploited without needing contract deployment — just a malicious EOA.

💼 Why This Challenge Matters

Through this exercise, we can:
- Understand core ERC20 mechanics and balance manipulation
- Can identify and exploit integer underflows
- Automate exploits using both Solidity tests and Python Web3.py
- Simulate both attacker and victim scenarios
- Demonstrate understanding of historical smart contract bugs and secure coding practices

✍️ Author

defi-dojo – A curated collection of real-world smart contract exploit simulations with automated testing and writeups.

Created and maintained with ❤️ by yprakash.