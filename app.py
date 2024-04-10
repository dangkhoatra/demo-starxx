from ulti import (
    connect_web3, 
    config, 
    read_wallets,
    approve_token,
    transfer_token,
    send_vic,
    buy_presale,
    get_input,
)

from typing import List, Dict
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def _buy_presale_snipe(w3, wallets) -> None:

    current_block = None
    input_hex: str = None
    while True:
        latest_block = w3.eth.get_block('latest')
        block_number = latest_block['number']
        txs = latest_block['transactions']
        if current_block != block_number:
            current_block = block_number
            print(f'Find new block: {current_block}. This block has {len(txs)} transactions')
            # print(f'This block has {len(txs)} transactions')
            if len(txs) > 0:
                for tx in txs:
                    #if get_input(w3, tx.hex()):
                    input_hex: str = get_input(w3, tx.hex())
                    if input_hex:
                        print(f"Trigger found in transaction: {tx.hex()}")
                        break
            if input_hex:
                break
        time.sleep(0.25)
    
    for wallet in wallets:
        buy_presale(w3, wallet['pk'], wallet['addr'], input_hex)



def _buy_presale_snipe_concurrently(w3, wallets) -> None:
    current_block = None
    input_hex: str = None
    while True:
        latest_block = w3.eth.get_block('latest')
        block_number = latest_block['number']
        txs = latest_block['transactions']
        if current_block != block_number:
            current_block = block_number
            print(f'Find new block: {current_block}. This block has {len(txs)} transactions')
            # print(f'This block has {len(txs)} transactions')
            if len(txs) > 0:
                for tx in txs:
                    #if get_input(w3, tx.hex()):
                    input_hex: str = get_input(w3, tx.hex())
                    if input_hex:
                        print(f"Trigger found in transaction: {tx.hex()}")
                        break
            if input_hex:
                break
        time.sleep(0.25)
    # Use ThreadPoolExecutor to execute buy_presale concurrently
    with ThreadPoolExecutor(max_workers=len(wallets)) as executor:
        # Dictionary to hold future to wallet mapping
        future_to_wallet = {executor.submit(buy_presale, w3, wallet['pk'], wallet['addr'], input_hex): wallet for wallet in wallets}
        
        for future in as_completed(future_to_wallet):
            wallet = future_to_wallet[future]
            try:
                result = future.result()
                print(f"Transaction for {wallet['addr']} completed with result: {result}")
            except Exception as exc:
                print(f"Transaction for {wallet['addr']} generated an exception: {exc}")


def _buy_presale(w3, wallets: List[Dict[str, str]]) -> None:
    hex_data = '0x2a28e5a33d49118cf356a65301ce647dc467e4233197019731351ba4a1af9cb0b04cc2b700000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000000'
    
    # Use ThreadPoolExecutor to execute buy_presale concurrently
    with ThreadPoolExecutor(max_workers=len(wallets)) as executor:
        # Dictionary to hold future to wallet mapping
        future_to_wallet = {executor.submit(buy_presale, w3, wallet['pk'], wallet['addr'], hex_data): wallet for wallet in wallets}
        
        for future in as_completed(future_to_wallet):
            wallet = future_to_wallet[future]
            try:
                result = future.result()
                print(f"Transaction for {wallet['addr']} completed with result: {result}")
            except Exception as exc:
                print(f"Transaction for {wallet['addr']} generated an exception: {exc}")


def _approve_token(w3, wallets):
    for wallet in wallets:
        # print(wallet)
        approve_token(w3, wallet['pk'], wallet['addr'])



def _approve_token_concurrently(w3, wallets):
    with ThreadPoolExecutor(max_workers=len(wallets)) as executor:
        # Create a future for each approve_token task
        futures = [executor.submit(approve_token, w3, wallet['pk'], wallet['addr']) for wallet in wallets]

        # Optionally, wait for each to complete and handle results/errors
        for future in as_completed(futures):
            try:
                # Get the result of the future. 
                # Note: You can also pass arguments to the result method to timeout if needed
                result = future.result()
                # Process result here (if approve_token returns any value)
            except Exception as e:
                print(f"An error occurred: {e}")


def _transfer_c98_concurrently(w3, wallets):
    sender = ''
    pk = ''
    amount = 130

    with ThreadPoolExecutor(max_workers=len(wallets)) as executor:
        futures = [executor.submit(
            transfer_token, 
            w3,
            pk,
            sender,
            wallet['addr'],
            amount,
        ) for wallet in wallets]

         # Optionally, wait for each to complete and handle results/errors
        for future in as_completed(futures):
            try:
                # Get the result of the future. 
                # Note: You can also pass arguments to the result method to timeout if needed
                result = future.result()
                # Process result here (if approve_token returns any value)
            except Exception as e:
                print(f"An error occurred: {e}")


def _transfer_c98(w3, wallets):
    sender = ''
    
    pk = ''
    
    amount = 130
    for wallet in wallets:
        transfer_token(
            w3=w3, 
            pk=pk,
            sender=sender,
            receiver=wallet['addr'],
            amount=amount,
        )
        #send_vic(w3, sender.key.hex(), sender.address, wallet['addr'], 0.1)


def handle_chosen_menu(w3, wallets):

    choice = print_menu()
    if choice == 1:
        _approve_token_concurrently(w3, wallets)
    elif choice == 2:
        _transfer_c98(w3, wallets)
    elif choice == 3:
        _buy_presale(w3, wallets)
    elif choice == 4:
        _buy_presale_snipe_concurrently(w3, wallets)
    else:
        print("Invalid option, please try again.")
    

def print_menu():
    choice = int(input(
"""
    Please chose the options:
    1) Approve token
    2) Transfer C98 to purchase presale
    3) Buy presale
    4) Buy presale with snipe

Please enter your choice: """
    ))
    try:
        if choice in [1, 2, 3, 4]:  # Check if the choice is valid
            return choice
        else:
            print("Please select a valid option.")
    except ValueError:  # Catch non-integer inputs
        print("Please enter a number.")


if __name__ == '__main__':
    w3 = connect_web3(using_middleware=True)
    wallets = read_wallets(w3)
    handle_chosen_menu(w3, wallets)