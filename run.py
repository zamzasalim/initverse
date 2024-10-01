from web3 import Web3
from eth_account import Account
import time
import sys
import os
from decimal import Decimal

from privateKeys import private_keys, VALUE_ETH, GAS_LIMIT_ADJUSTMENT, FEE_GWEI

networks = {
    'InitVerse': {
        'rpc_url': 'https://rpc-testnet.iniscan.com',
        'chain_id': 233,
        'contract_address': '0x7BEf93022D48b9df745B77D0Fd348fB415b026e2'  # Alamat Router ObsSwap
    }
}

USDT_ADDRESS = '0x36AA81a7aEeAB8f09e154d3E779Bb81beA54501A'
TOKEN_ADDRESS = '0xcF259Bca0315C6D32e877793B6a10e97e7647FdE'

def print_banner():
    banner_text = """
    \033[96m=========================================================
                        INITVERSE | AIRDROP ASC
    =========================================================
                  Credit By       : Airdrop ASC
                  Telegram Channel: @airdropasc
                  Telegram Group  : @autosultan_group
    =========================================================\033[0m
    """
    print(banner_text)

def get_current_gas_price(web3):
    try:
        gas_price_wei = web3.eth.gas_price
        gas_price_gwei = web3.from_wei(gas_price_wei, 'gwei')
        return gas_price_gwei
    except Exception as e:
        print(f"Error fetching gas price: {e}")
        return Decimal('0')

def send_swap_transaction(web3, account, contract, amount_out_min, path, to_address, deadline, nonce, amount_in, gas_limit):
    try:
        transaction = contract.functions.swapExactTokensForTokens(
            amount_in,
            amount_out_min,
            path,
            to_address,
            deadline
        ).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': gas_limit,  
            'gasPrice': web3.to_wei(10, 'gwei'),  
            'chainId': networks['InitVerse']['chain_id']
        })

        signed_txn = web3.eth.account.sign_transaction(transaction, private_key=account.key)

        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        return web3.to_hex(tx_hash)
    except ValueError as e:
        print(f"\033[91mError sending transaction on InitVerse: {e}\033[0m")
        return None
    except Exception as e:
        print(f"\033[91mUnexpected error sending transaction on InitVerse: {e}\033[0m")
        return None

def validate_private_key(private_key):
    if not private_key.startswith('0x'):
        private_key = '0x' + private_key
    if len(private_key) != 66:
        return None
    try:
        Account.from_key(private_key)
        return private_key
    except ValueError:
        return None

def create_tx_folder():
    base_folder = 'Tx_Hash'
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)
    return base_folder

def create_network_folder(base_folder, network_name):
    network_folder = os.path.join(base_folder, network_name.replace(' ', '-'))
    if not os.path.exists(network_folder):
        os.makedirs(network_folder)
    return network_folder

def create_swap_file(network_folder, swap_name):
    swap_file_path = os.path.join(network_folder, f'Tx_{swap_name.replace(" ", "-")}.txt')
    if not os.path.exists(swap_file_path):
        open(swap_file_path, 'w').close()  
    return swap_file_path

def save_tx_hash(tx_hash, source_network, swap_name):
    base_folder = create_tx_folder()
    source_folder = create_network_folder(base_folder, source_network)
    swap_file_path = create_swap_file(source_folder, swap_name)
    with open(swap_file_path, 'a') as file:
        file.write(f'{tx_hash}\n')

def run_swap_network(account, active_swaps, swap_count):
    print("\nRunning \033[96m{}\033[0m swaps for active networks: {}".format(swap_count, ', '.join([swap for swap, active in active_swaps.items() if active])))
    total_success = 0
    web3 = Web3(Web3.HTTPProvider(networks['InitVerse']['rpc_url']))

    try:
        nonce = web3.eth.get_transaction_count(account.address)
    except Exception as e:
        print(f"\033[91mError fetching nonce: {e}\033[0m")
        return

    router_abi = [
        {
            "inputs": [
                {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                {"internalType": "address[]", "name": "path", "type": "address[]"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"}
            ],
            "name": "swapExactTokensForTokens",
            "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ]

    contract = web3.eth.contract(address=networks['InitVerse']['contract_address'], abi=router_abi)

    for _ in range(swap_count):
        for swap, active in active_swaps.items():
            if not active:
                continue  

            try:
                if swap == "INI to TOKEN":
                    amount_out_min = 0
                    path = [networks['InitVerse']['contract_address'], TOKEN_ADDRESS]
                    gas_limit = 140600
                    amount_in = Web3.to_wei(0.002, 'ether')  # 0.002 INI
                    display_amount = "0.002 INI"

                elif swap == "INI to USDT":
                    amount_out_min = 0
                    path = [networks['InitVerse']['contract_address'], USDT_ADDRESS]
                    gas_limit = 128542
                    amount_in = Web3.to_wei(0.002, 'ether')  # 0.002 INI
                    display_amount = "0.002 INI"

                elif swap == "TOKEN to INI":
                    amount_out_min = 0
                    path = [TOKEN_ADDRESS, networks['InitVerse']['contract_address']]
                    gas_limit = 209126
                    amount_in = Web3.to_wei(0.001, 'ether')  # 0.001 TOKEN
                    display_amount = "0.001 TOKEN"

                elif swap == "USDT to INI":
                    amount_out_min = 0
                    path = [USDT_ADDRESS, networks['InitVerse']['contract_address']]
                    gas_limit = 145873
                    amount_in = Web3.to_wei(0.001, 'ether')  # 0.001 USDT
                    display_amount = "0.001 USDT"

                to_address = account.address
                deadline = int(time.time()) + 60 * 20  

                tx_hash = send_swap_transaction(
                    web3,
                    account,
                    contract,
                    amount_out_min,
                    path,
                    to_address,
                    deadline,
                    nonce,
                    amount_in,
                    gas_limit
                )

                if tx_hash:
                    print(f"\033[92mTx Hash: {tx_hash}\nSwap: {swap} | Amount: {display_amount}\033[0m")
                    save_tx_hash(tx_hash, 'InitVerse', swap)
                    total_success += 1

                nonce += 1  
                time.sleep(5)  
            except KeyboardInterrupt:
                print("\n\033[93mBot Stop\033[0m")
                sys.exit(0)
            except Exception as e:
                print(f"\033[91mError processing {swap}: {e}\033[0m")

    print(f"\n\n\033[92mAll Active Swaps Complete: Total {total_success}\033[0m")

def main():
    os.system('clear') if os.name == 'posix' else os.system('cls')  
    print_banner()

    print("    \033[96m=== Main Menu ===\033[0m")
    print("    1. InitVerse")
    print("    2. Run Swap Network")
    print("    \033[96m==================\033[0m\n")

    network_choice = input("    \033[96mNetwork choice (1-2): \033[0m")

    if network_choice == "1":
        print("\033[94mWhat the hell are you looking for? Get the hell out of here -_-\033[0m")
        sys.exit(0)

    elif network_choice == "2":
        active_swaps = {
            "INI to TOKEN": True,
            "INI to USDT": True,
            "USDT to INI": True,
            "TOKEN to INI": True
        }

        while True:
            os.system('clear')  
            print_banner()  
            print("\n\033[96m    Select Networks to Disable \033[0m")
            for idx, (swap, active) in enumerate(active_swaps.items(), start=1):
                status = "\033[92mActive\033[0m" if active else "\033[91mInactive\033[0m"
                print(f"    {idx}. {swap} [{status}]")
            print(f"    {len(active_swaps) + 1}. Run Swap")

            choice = input(f"    \033[96mSelect network to toggle (1-{len(active_swaps)}) or {len(active_swaps)+1} to run swap: \033[0m")

            if choice.isdigit():
                choice = int(choice)
                if 1 <= choice <= len(active_swaps):
                    swap_name = list(active_swaps.keys())[choice - 1]
                    active_swaps[swap_name] = not active_swaps[swap_name]
                elif choice == len(active_swaps) + 1:
                    break  
                else:
                    print("\033[91mInvalid choice. Please try again.\033[0m")
            else:
                print("\033[91mInvalid input. Please enter a number.\033[0m")

        os.system('clear')  
        print_banner()

        try:
            swap_count = int(input("\033[96mHow many times to make Transactions: \033[0m"))
        except ValueError:
            print("\033[91mInvalid input. Please enter a valid number.\033[0m")
            sys.exit(1)

        private_key = validate_private_key(private_keys[0])
        if not private_key:
            print("\033[91mInvalid private key format.\033[0m")
            sys.exit(1)
        account = Account.from_key(private_key)

        os.system('clear')  
        print_banner()  
        run_swap_network(account, active_swaps, swap_count)

    else:
        print("\033[91mInvalid selection.\033[0m")
        sys.exit(1)

if __name__ == "__main__":
    main()