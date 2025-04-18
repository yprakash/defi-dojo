## Problem Statement
#### Level 0: Hello Dev
You are given a simple contract with a public owner variable.
Can you become the owner of the contract?  

Difficulty: 🎯 Beginner  
Learning Objectives:
- Understand constructor logic
- Visibility
- Basic contract interaction

What’s the Vulnerability?  
- claimOwnership() is public and unprotected.
- Any user can call it and take over the contract.