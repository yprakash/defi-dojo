🧠 Telephone – Ethernaut Challenge

Category: Smart Contract Exploitation

Difficulty: Beginner

🔍 Challenge Summary

In this challenge, the contract’s ownership logic relies on tx.origin, making it vulnerable to phishing-style attacks. An attacker can exploit this by calling the contract via another contract, causing msg.sender != tx.origin.

🚀 Key Takeaways
- Authorization logic should never rely on tx.origin.
- Smart contract attackers can chain calls through contracts to spoof context.
- This simulates phishing-like attacks where users unknowingly sign malicious transactions.

💼 Why This Challenge Matters

Through this exercise, we can:
- Understand call context vulnerabilities in Solidity (tx.origin vs msg.sender)
- Can simulate realistic attacker scenarios using both Solidity and Python
- Write automated tests that verify exploit-ability and validate secure behavior
- Use Foundry, Web3.py, and pytest effectively

✍️ Author

defi-dojo – A curated series of smart contract audit challenges with automated tests and solutions.

Created and maintained by yprakash.