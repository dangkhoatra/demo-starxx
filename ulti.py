from web3 import Web3
import configparser
import json
from eth_account import Account
from typing import List, Dict, Optional
from web3.middleware import geth_poa_middleware


Account.enable_unaudited_hdwallet_features()

config = configparser.ConfigParser()
config.read('config.ini')

RPC = config['DEFAULT']['RPC']
CHAIN_ID = config['DEFAULT']['ChainId']
ABI = config['DEFAULT']['ABI']
TOKEN = Web3.to_checksum_address(config['DEFAULT']['TokenContract'])
PRESALE_ADDRESS = config['DEFAULT']['PresaleAddress']


def get_input(w3: Web3, trx_hash: str) -> str:
    # PRESALE_ADDRESS = '0xA658742d33ebd2ce2F0bdFf73515Aa797Fd161D9'
    tx = w3.eth.get_transaction(trx_hash)
    if tx.to.lower() == PRESALE_ADDRESS.lower():
        print('Found transaction of presale address.')
        tx_receipt = w3.eth.get_transaction_receipt(trx_hash)
        if tx_receipt.status == 1:
            print({
                'hash': trx_hash,
                'input_hex': tx.input.hex(),
            })
            return tx.input.hex()



def connect_web3(rpc: str = RPC, using_middleware: bool = False) -> Web3:
    """
    Attempt to connect to a Web3 provider using the specified RPC URL.
    
    Args:
        rpc (str): The RPC endpoint URL to connect to.
        
    Returns:
        Web3: An instance of the Web3 class if the connection is successful.
        
    Raises:
        ValueError: If unable to connect to the specified RPC URL.
    """

    # Initialize a Web3 instance with the specified HTTP RPC endpoint.
    w3: Web3 = Web3(Web3.HTTPProvider(rpc))

    if using_middleware:
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # Check if the connection to the RPC was successful.
    if w3.is_connected():
        print(f'Connected to {rpc} successful.')
        return w3
    else:
        raise ValueError('Something went wrong. Please try other RPC to connecting web3.')
    

# def buy_presale_with_snipe(w3: Web3, pk: str, sender: str) -> None:
#     sender = Web3.to_checksum_address(sender)
#     latest_block = w3.eth.get_block('latest')
#     print(latest_block)
    


def buy_presale(w3: Web3, pk: str, sender: str, hex_data: str) -> None:
    sender = Web3.to_checksum_address(sender)

    tx = {
        # 'chainId': CHAIN_ID,
        'from': sender,
        'to': PRESALE_ADDRESS,
        'gas': 5000000,
        'gasPrice': w3.eth.gas_price,
        'nonce':w3.eth.get_transaction_count(sender),
        'data': hex_data,
    }

    signed_tx = w3.eth.account.sign_transaction(tx, pk)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    # Get transaction hash
    print(f"Transaction hash: {tx_hash.hex()}")

    # Wait for the transaction to be mined and get the transaction receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    _parse_tx_receipt(tx_receipt)


    
def send_vic(w3, pk, sender, receiver, amount) -> None:
    print(sender)
    print(receiver)
    tx = {
        'chainId': 88,
        'from': sender,
        'to': receiver,
        'value': int(amount*(10**18)),
        'gas': 21000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(sender),
    }
    print(tx)
    signed_tx = w3.eth.account.sign_transaction(tx, pk)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    # Get transaction hash
    print(f"Transaction hash: {tx_hash.hex()}")

def transfer_token(w3: Web3, pk: str, sender: str, receiver: str, amount: int) -> None:
    contract = w3.eth.contract(
        address=TOKEN,
        abi=ABI,
    )
    receiver = Web3.to_checksum_address(receiver)
    sender = Web3.to_checksum_address(sender)
    nonce = w3.eth.get_transaction_count(sender)
    value = amount*(10**18)
    balance = contract.functions.balanceOf(receiver).call()
    # print(balance/(10**18))
    remaining_amount = value - balance
    #print(remaining_amount/(10**18))
    if remaining_amount > 0:
        tx = contract.functions.transfer(receiver, remaining_amount).build_transaction({
            'gas': 200000,
            'gasPrice': w3.eth.gas_price,
            'nonce': nonce,
        })
    
        signed_tx = w3.eth.account.sign_transaction(tx, pk)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        # Get transaction hash
        print(f"Transaction hash: {tx_hash.hex()}")

        # Wait for the transaction to be mined and get the transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        _parse_tx_receipt(tx_receipt)
    else:
        print(f'- Wallet {receiver} has enought {amount} C98.')


def approve_token(w3: Web3, pk: str, sender: str) -> None:
    contract = w3.eth.contract(
        address=TOKEN,
        abi=ABI,
    )
    sender = Web3.to_checksum_address(sender)
    nonce = w3.eth.get_transaction_count(sender)
    unlimited_amount = 2**256 - 1

    gas_price = w3.eth.gas_price * 10

    tx = contract.functions.approve(PRESALE_ADDRESS, unlimited_amount).build_transaction({
        # 'chainId': CHAIN_ID,
        'gas': 200000,
        'gasPrice': w3.eth.gas_price,
        'nonce': nonce,
    })
    signed_tx = w3.eth.account.sign_transaction(tx, pk)

    # Send the transaction
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    # Get the transaction hash
    print(f"Sent transaction hash: {tx_hash.hex()}")

    # Optionally, wait for the transaction to be mined and get the receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    _parse_tx_receipt(tx_receipt)


def read_wallets(w3: Web3) -> List[Dict[str, str]]:
    with open('wallets.json', 'r+') as f:
        data = json.load(f)

    wallets: list = []
    for seed in data:
        # Create an account from the seed phrase
        wallet = w3.eth.account.from_mnemonic(seed.strip())
        wallets.append({
            'addr': wallet.address,
            'pk': wallet.key.hex(),
        })
    return wallets



def _parse_tx_receipt(tx_receipt):
    # Check if the transaction was successful
    tx_status = 'Success' if tx_receipt.status == 1 else 'Failure'

    if tx_receipt.status == 1:
        print(f"- Transaction is success. https://www.vicscan.xyz/tx/{tx_receipt.transactionHash.hex()}. Address: `{tx_receipt['from']}'")
        return 1
    else:
        print(f"- Transaction is failure. https://www.vicscan.xyz/tx/{tx_receipt.transactionHash.hex()}. Address: `{tx_receipt['from']}`")
        return 0

    # # Extracting key information
    # readable_receipt = {
    #     'Transaction Status': tx_status,
    #     'Transaction Hash': tx_receipt.transactionHash.hex(),
    #     'Block Number': tx_receipt.blockNumber,
    #     'From': tx_receipt['from'],
    #     'To': tx_receipt.to,
    #     'Gas Used': tx_receipt.gasUsed,
    #     'Cumulative Gas Used': tx_receipt.cumulativeGasUsed,
    #     'Contract Address': tx_receipt.contractAddress,
    # }

    # # Optionally, format and print the receipt for reading
    # for key, value in readable_receipt.items():
    #     print(f"{key}: {value}")

    return readable_receipt
