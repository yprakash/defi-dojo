# 🥷 DeFi Dojo: A Custom Solidity CTF for Auditors & Builders

Welcome to **DeFi Dojo**, a curated set of **custom smart contract challenges** designed to help developers, auditors, and DeFi security enthusiasts hone their skills in:

- 🧠 **Vulnerability discovery**
- 🛡️ **Offensive & defensive smart contract design**
- 🧪 **Test-driven exploit development**
- 🐍 **Python-based attack automation**
- 🔍 **Audit-grade analysis and reasoning**
---
### 🧩 Challenge Design Philosophy

Each level:
- Is inspired by **real-world vulnerabilities**
- Has an **intentional flaw** in logic, visibility, control flow, or upgradeability
- Is paired with a **Python exploit script** that solves it programmatically
- Contains **Foundry tests** to simulate exploit scenarios onchain
---
### ✅ Skills You'll Develop

- Reentrancy, delegatecall abuse, fallback misuses, tx.origin auth flaws
- Upgradeable proxy issues, integer overflows, front-running
- Composable attack logic using Python & Solidity
---
### 🧠 Requirements

- [Foundry](https://book.getfoundry.sh/)
- [Anvil (local chain)]
- Python 3.10+
- `web3.py`, `python-dotenv`, `py-solc-x`
---
### 💡 Why This Exists

This repo is built by an **experienced backend engineer** transitioning into **smart contract security**.

Inspired by:
- [Ethernaut](https://ethernaut.openzeppelin.com/)
- [Capture the Ether](https://capturetheether.com/)
- Real audit reports from Trail of Bits, Spearbit, and others
---
⚙️ Python Automation Layer  
Each level includes an optional Python-based exploit script leveraging web3.py, pytest, and ABI introspection. This demonstrates advanced TDD, scripting, and offensive testing beyond Solidity. It simulates how real-world auditors and bug bounty hunters automate exploit pipelines.
---
## 📬 Feedback or Collaboration?
Feel free to contact me in case of any issues, or DM me on [LinkedIn](https://www.linkedin.com/in/yprakash/).  

If you’re hiring for protocol security or audit engineering — feel free to [reach out](mailto:yprakash.518@gmail.com).
