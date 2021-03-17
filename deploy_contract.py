import json
from web3 import Web3

ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))
print('Connection to node:', web3.isConnected())

ac_index = int(input('Enter default index of Ganache address:'))

web3.eth.defaultAccount = web3.eth.accounts[ac_index]

# Load ABI and BYTECODE
with open('abi.json') as f1:
  abi = json.load(f1)
with open('bytecode.json') as f2:
  bytecode = json.load(f2)

# Deploying smart contract and creating contract instance
carbonmarket = web3.eth.contract(abi=abi, bytecode=bytecode['object'])
tx_hash = carbonmarket.constructor().transact()
tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
contract = web3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
contractdetails = {'address': tx_receipt.contractAddress}
print('Contract deployed at:', tx_receipt.contractAddress)
with open('contract_details.json', 'w') as outfile:
	json.dump(contractdetails, outfile)