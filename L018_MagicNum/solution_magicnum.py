import os

import solcx
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.getenv('PROVIDER_URL')))
if w3.is_connected():
    print("Successfully connected to the provider!")
else:
    print("Failed to connect to the given provider ", os.getenv('PROVIDER_URL'))
    exit()

# Load environment variables
_PRIVATE_KEY = os.getenv('PRIVATE_KEY')
_WALLET = w3.to_checksum_address(os.getenv('WALLET'))

def send_transaction_and_wait(transaction):
    signed_tx = w3.eth.account.sign_transaction(transaction, private_key=_PRIVATE_KEY)
    txn_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    assert tx_receipt['status'] == 1
    print(f'Completed transaction: {tx_receipt}')
    return tx_receipt

# Step 1: build bytecode transaction and deploy contract
creation_code = "69602a60005260206000f3600052600a6016f3"
tx = {
    "from": _WALLET,
    "to": None,  # for contract creation
    "data": "0x" + creation_code,
    "value": 0,
    "gas": 100000,
    "gasPrice": w3.eth.gas_price,
    'chainId': 11155111,
    'nonce': w3.eth.get_transaction_count(w3.to_checksum_address(_WALLET))
}
tx_receipt = send_transaction_and_wait(tx)
solver_address = tx_receipt["contractAddress"]
print('Created bytecode contract at ', solver_address)

# Step 2: Set the solver on the challenge contract
target_address = w3.to_checksum_address("<Your Instance address>")
target_abi = [{
    "inputs": [{"internalType": "contract Solver", "name": "_solver", "type": "address"}],
    "name": "setSolver",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
}]
magicnum = w3.eth.contract(address=target_address, abi=target_abi)
tx2 = magicnum.functions.setSolver(solver_address).build_transaction({
    'from': _WALLET,
    "gas": 100000,
    "gasPrice": w3.eth.gas_price,
    'chainId': 11155111,
    'nonce': w3.eth.get_transaction_count(w3.to_checksum_address(_WALLET))
})
tx_receipt = send_transaction_and_wait(tx2)
assert magicnum.functions.solver() == solver_address
print('Well done, You have completed this level!!!')
