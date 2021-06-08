# Import dependencies
import subprocess
import json
import os
from dotenv import load_dotenv

# Load and set environment variables
load_dotenv()
mnemonic=os.getenv("mnemonic")

# cwd = os.getcwd()
# print(cwd)

# Import constants.py and necessary functions from bit and web3
# from constants import *
from constants import BTC, BTCTEST, ETH
from web3 import Web3
from web3.middleware import geth_poa_middleware
import bit
from bit import Key, PrivateKey, PrivateKeyTestnet
from bit.network import NetworkAPI
from eth_account import Account

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

 
# Create a function called `derive_wallets`
def derive_wallets(coin=BTC, mnemonic=mnemonic, numderive=3):
    command = f'php ./derive -g --mnemonic="{mnemonic}" --cols=all --coin={coin} --numderive={numderive} --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    return json.loads(output)

# Create a dictionary object called coins to store the output from `derive_wallets`.
coins = {
    ETH: derive_wallets(ETH, mnemonic, numderive=3),
    BTCTEST: derive_wallets(BTCTEST, mnemonic, numderive=3)
}

# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    elif coin == BTCTEST:
        return bit.PrivateKeyTestnet(priv_key)


# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin, account, to, amount):
    if coin == ETH:
        value = w3.toWei(amount, "ether")
        gasEstimate = w3.eth.estimateGas(
            {"from": account.address, "to": to, "amount": value}
        )
        return {
            "from": account.address,
            "to": to,
            "value": value,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(account.address),
        }
    elif coin == BTCTEST:
        return bit.PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])

# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin, account, to, amount):
    if coin == ETH:
        raw_tx = create_tx(coin, account, to, amount)
        signed_tx = account.sign_transaction(raw_tx)
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return result.hex()
    elif coin == BTCTEST:
        raw_tx = create_tx(coin, account, to, amount)
        signed_tx = account.sign_transaction(raw_tx)
        return NetworkAPI.broadcast_tx_testnet(signed_tx)
