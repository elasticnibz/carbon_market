from web3 import Web3
import json
from flask import Flask, render_template, request, flash, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired
import os
from datetime import date

# Ganache URL connection
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))
print('Connection to node:', web3.isConnected())
ac_index = int(input('Enter default index of Ganache address:'))
web3.eth.defaultAccount = web3.eth.accounts[ac_index]

print(web3.eth.defaultAccount)

# Loading ABI from json
with open('abi.json') as f:
  abi = json.load(f)

# Loading deployed contract address and initating contract instance
with open('contract_details.json') as f1:
	contractdetails = json.load(f1)
contractadd = contractdetails['address']
contract=web3.eth.contract(address=contractadd, abi=abi)

# Form classes definition
class RegisrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	submit = SubmitField('Register')
class BuySellForm(FlaskForm):
	amount = IntegerField('Amount', validators=[DataRequired()])
	submit = SubmitField('Submit')
class DonateForm(FlaskForm):
	address = StringField('Address', validators=[DataRequired()])
	amount = IntegerField('Amount', validators=[DataRequired()])
	submit = SubmitField('Donate')
class SetMarket(FlaskForm):
	supply = IntegerField('Total Supply', validators=[DataRequired()])
	price = FloatField('Price (ETH)', validators=[DataRequired()])
	validity = FloatField('Validity (days)', validators=[DataRequired()])
	sell_lock = FloatField('Duration of Sale Freeze (days)', validators=[DataRequired()])
	submit = SubmitField('Set Market')

# Functions
def terminalparams():
	name = contract.functions.myName().call()
	availableSupply = contract.functions.AvailableTokens().call()
	totalseconds = contract.functions.returnTimeRemaining().call()
	daysleft = int(float(totalseconds)/(60*60*24))
	hoursleft = int((totalseconds - (daysleft*24*60*60))/(60*60))
	minsleft = int((totalseconds - (daysleft*24*60*60) - (hoursleft*60*60))/(60))
	secsleft = int(totalseconds - (daysleft*24*3600) - (hoursleft*3600) - (minsleft*60))
	balance = contract.functions.returnBalance().call()
	price = contract.functions.price().call()
	price = web3.fromWei(price, 'ether')
	etherbal = web3.eth.getBalance(web3.eth.defaultAccount)
	etherbal = web3.fromWei(etherbal, 'ether')
	etheraccount = web3.eth.defaultAccount
	sell_lock = contract.functions.translock().call()
	if totalseconds > sell_lock:
		sale_status = 'Sale of tokens permitted'
	else:
		sale_status = 'No further sale of tokens permitted'
	return name, availableSupply, balance, daysleft, hoursleft, minsleft, secsleft, price, etherbal, etheraccount, sale_status

# Setting up flask protocols
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret420'

@app.route('/')
@app.route('/index')
def index():
	availableSupply = contract.functions.AvailableTokens().call()
	limit0 = contract.functions.returnTimeRemaining().call()
	limit0 = float(limit0/(24*60*60))
	price = contract.functions.price().call()
	price = web3.fromWei(price, 'ether')
	address_user = web3.eth.defaultAccount
	address_MM = contract.functions.marketmaker().call()
	if address_user == address_MM:
		return render_template('index_master.html', availableSupply=availableSupply, price=price, limit=limit0)
	else:
		return render_template('index.html', availableSupply=availableSupply, price=price)    

@app.route('/register', methods=['GET', 'POST'])
def register():
	availableSupply = contract.functions.AvailableTokens().call()
	limit0 = contract.functions.returnTimeRemaining().call()
	limit0 = float(limit0/(24*60*60))
	price = contract.functions.price().call()
	price = web3.fromWei(price, 'ether')
	address_user = web3.eth.defaultAccount
	address_MM = contract.functions.marketmaker().call()
	if address_user == address_MM:
		return render_template('index_master.html', availableSupply=availableSupply, price=price, limit=limit0)
	else:
		form = RegisrationForm()
		status = contract.functions.isRegistered().call()
		regdict = contract.functions.regdict().call()
		regdict = regdict[:-1]
		if form.validate_on_submit():
			flash('Registration requested for user {}'.format(
				form.username.data))
			if status==False:
				today = date.today()
				todayd1 = today.strftime("%b-%d-%Y")
				entityinfo = {
					"name": form.username.data,
					"address": web3.eth.defaultAccount,
					"datejoined": todayd1
				}
				entityjson = json.dumps(entityinfo)
				regdict = regdict + entityjson + ', ]'
				contract.functions.register(form.username.data, regdict).transact()
				name, availableSupply, balance, daysleft, hoursleft, minsleft, secsleft, price, etherbal, etheraccount, sale_status = terminalparams()
				return render_template('terminal.html', 
					availableSupply=availableSupply, 
					balance=balance,
					name=name,
					daysleft=daysleft,
					hoursleft=hoursleft,
					minsleft=minsleft,
					secsleft=secsleft,
					price=price,
					etherbal=etherbal,
					etheraccount=etheraccount,
					sale_status=sale_status)
			else:
				availableSupply = contract.functions.AvailableTokens().call()
				price = contract.functions.price().call()
				price = web3.fromWei(price, 'ether')
				return render_template('index.html', availableSupply=availableSupply, price=price)
		return render_template('register.html', form=form)

@app.route('/terminal', methods=['GET', 'POST'])
def terminal():
	availableSupply = contract.functions.AvailableTokens().call()
	limit0 = contract.functions.returnTimeRemaining().call()
	limit0 = float(limit0/(24*60*60))
	price = contract.functions.price().call()
	price = web3.fromWei(price, 'ether')
	address_user = web3.eth.defaultAccount
	address_MM = contract.functions.marketmaker().call()
	if address_user == address_MM:
		return render_template('index_master.html', availableSupply=availableSupply, price=price, limit=limit0)
	else:
		status = contract.functions.isRegistered().call()
		if status:
			name, availableSupply, balance, daysleft, hoursleft, minsleft, secsleft, price, etherbal, etheraccount, sale_status = terminalparams()
			return render_template('terminal.html', 
				availableSupply=availableSupply, 
				balance=balance,
				name=name,
				daysleft=daysleft,
				hoursleft=hoursleft,
				minsleft=minsleft,
				secsleft=secsleft,
				price=price,
				etherbal=etherbal,
				etheraccount=etheraccount,
				sale_status=sale_status)
		else:
			availableSupply = contract.functions.AvailableTokens().call()
			price = contract.functions.price().call()
			price = web3.fromWei(price, 'ether')
			return render_template('index.html', availableSupply=availableSupply, price=price)

@app.route('/buy', methods=['GET', 'POST'])
def buy():
	availableSupply = contract.functions.AvailableTokens().call()
	limit0 = contract.functions.returnTimeRemaining().call()
	limit0 = float(limit0/(24*60*60))
	price = contract.functions.price().call()
	price = web3.fromWei(price, 'ether')
	address_user = web3.eth.defaultAccount
	address_MM = contract.functions.marketmaker().call()
	if address_user == address_MM:
		return render_template('index_master.html', availableSupply=availableSupply, price=price, limit=limit0)
	else:
		form = BuySellForm()
		name, availableSupply, balance, daysleft, hoursleft, minsleft, secsleft, price, etherbal, etheraccount, sale_status = terminalparams()
		time = contract.functions.returnTimeRemaining().call()
		if time > 0:
			if form.validate_on_submit():
				flash('Request to buy {}'.format(
					form.amount.data))
				price = contract.functions.price().call()
				weiamount = price*(form.amount.data)
				weibalance = web3.eth.getBalance(web3.eth.defaultAccount)
				gasprice = web3.toWei('50', 'gwei')
				gasamt = 2000000
				if weibalance < ((gasamt*gasprice)+weiamount):
					flash('Insufficient ether balance!')
					return render_template('buy.html', form=form)
				elif availableSupply < form.amount.data:
					flash('Insufficient token supply avaialble for purchase!')
					return render_template('buy.html', form=form)
				else:
					# Transaction dictionary
					nonce = web3.eth.getTransactionCount(web3.eth.defaultAccount)
					tx = {
					    'nonce': nonce,
					    'to': contractadd,
					    'value': weiamount,
					    'gas': gasamt,
					    'gasPrice': web3.toWei('50', 'gwei')
					}
					contract.functions.buy().transact(tx)
					#tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
					name, availableSupply, balance, daysleft, hoursleft, minsleft, secsleft, price, etherbal, etheraccount, sale_status = terminalparams()
					flash('Transaction successful!')
					return render_template('terminal.html', 
						availableSupply=availableSupply, 
						balance=balance,
						name=name,
						daysleft=daysleft,
						hoursleft=hoursleft,
						minsleft=minsleft,
						secsleft=secsleft,
						price=price,
						etherbal=etherbal,
						etheraccount=etheraccount,
						sale_status=sale_status)
		return render_template('buy.html', form=form)

@app.route('/sell', methods=['GET', 'POST'])
def sell():
	availableSupply = contract.functions.AvailableTokens().call()
	limit0 = contract.functions.returnTimeRemaining().call()
	limit0 = float(limit0/(24*60*60))
	price = contract.functions.price().call()
	price = web3.fromWei(price, 'ether')
	address_user = web3.eth.defaultAccount
	address_MM = contract.functions.marketmaker().call()
	if address_user == address_MM:
		return render_template('index_master.html', availableSupply=availableSupply, price=price, limit=limit0)
	else:
		sell_lock = contract.functions.translock().call()
		form = BuySellForm()
		if (limit0*24*3600) > sell_lock:
			if form.validate_on_submit():
				flash('Request to sell {}'.format(
					form.amount.data))
				name, availableSupply, balance, daysleft, hoursleft, minsleft, secsleft, price, etherbal, etheraccount, sale_status = terminalparams()
				if form.amount.data > balance:
					flash('You cannot sell more than what you have!')
					return render_template('sell.html', form=form)
				else:
					contract.functions.sell(form.amount.data).transact()
					name, availableSupply, balance, daysleft, hoursleft, minsleft, secsleft, price, etherbal, etheraccount, sale_status = terminalparams()
					flash('Transaction successful!')
					return render_template('terminal.html', 
						availableSupply=availableSupply, 
						balance=balance,
						name=name,
						daysleft=daysleft,
						hoursleft=hoursleft,
						minsleft=minsleft,
						secsleft=secsleft,
						price=price,
						etherbal=etherbal,
						etheraccount=etheraccount,
						sale_status=sale_status)
		return render_template('sell.html', form=form)

@app.route('/donate', methods=['GET', 'POST'])
def donate():
	availableSupply = contract.functions.AvailableTokens().call()
	limit0 = contract.functions.returnTimeRemaining().call()
	limit0 = float(limit0/(24*60*60))
	price = contract.functions.price().call()
	price = web3.fromWei(price, 'ether')
	address_user = web3.eth.defaultAccount
	address_MM = contract.functions.marketmaker().call()
	if address_user == address_MM:
		return render_template('index_master.html', availableSupply=availableSupply, price=price, limit=limit0)
	else:
		form = DonateForm()
		bal = contract.functions.returnTimeRemaining().call()
		if bal > 0:
			if form.validate_on_submit():
				flash('Request to donate {} to address {}'.format(
					form.amount.data, form.address.data))
				name, availableSupply, balance, daysleft, hoursleft, minsleft, secsleft, price, etherbal, etheraccount, sale_status = terminalparams()
				if form.amount.data > balance:
					flash('You cannot donate what you do not have!')
					return render_template('donate.html', form=form)
				else:
					contract.functions.donate(form.address.data, form.amount.data).transact()
					name, availableSupply, balance, daysleft, hoursleft, minsleft, secsleft, price, etherbal, etheraccount, sale_status = terminalparams()
					flash('The recipent thanks you for your kind gesture!')
					return render_template('terminal.html', 
						availableSupply=availableSupply, 
						balance=balance,
						name=name,
						daysleft=daysleft,
						hoursleft=hoursleft,
						minsleft=minsleft,
						secsleft=secsleft,
						price=price,
						etherbal=etherbal,
						etheraccount=etheraccount,
						sale_status=sale_status)
		return render_template('donate.html', form=form)

@app.route('/setmarket', methods=['GET', 'POST'])
def setmarket():
	availableSupply = contract.functions.AvailableTokens().call()
	limit0 = contract.functions.returnTimeRemaining().call()
	limit0 = float(limit0/(24*60*60))
	price = contract.functions.price().call()
	price = web3.fromWei(price, 'ether')
	address_user = web3.eth.defaultAccount
	address_MM = contract.functions.marketmaker().call()
	if address_user != address_MM:
		return render_template('index.html', availableSupply=availableSupply, price=price)
	else:
		form = SetMarket()
		if form.validate_on_submit():
			flash('Request to set up supply of {} CTs at {} ETH/CT, valid for {} days.'.format(
				form.supply.data, form.price.data, form.validity.data))
			# Resetting user balances to zero
			regdict = contract.functions.regdict().call()
			if len(regdict) > 2:
				regdict = regdict[:-3] + ']'
				reglist = json.loads(regdict)
				for reg in reglist:
					entity_add = reg['address']
					contract.functions.reset(entity_add).transact()
			weiprice = web3.toWei(form.price.data, 'ether')
			limit = int((form.validity.data)*24*3600)
			sell_lock = int((form.sell_lock.data)*24*3600)
			supply = form.supply.data
			tx_hash1 = contract.functions.setMarket(supply, weiprice, limit, sell_lock).transact()
			receipt1 = web3.eth.waitForTransactionReceipt(tx_hash1)
			availableSupply = contract.functions.AvailableTokens().call()
			price = contract.functions.price().call()
			price = web3.fromWei(price, 'ether')
			limit0 = contract.functions.returnTimeRemaining().call()
			limit0 = float(limit0/(24*60*60))
			return render_template('index_master.html', availableSupply=availableSupply, price=price, limit=limit0)
		return render_template('setmarket.html', form=form)

@app.route('/entities', methods=['GET', 'POST'])
def entities():
	availableSupply = contract.functions.AvailableTokens().call()
	limit0 = contract.functions.returnTimeRemaining().call()
	limit0 = float(limit0/(24*60*60))
	price = contract.functions.price().call()
	price = web3.fromWei(price, 'ether')
	address_user = web3.eth.defaultAccount
	address_MM = contract.functions.marketmaker().call()
	if address_user != address_MM:
		return render_template('index.html', availableSupply=availableSupply, price=price)
	else:
		regdict = contract.functions.regdict().call()
		if len(regdict)>2:
			timeleft = contract.functions.returnTimeRemaining().call()
			sell_lock = contract.functions.translock().call()
			regdict = regdict[:-3] + ']'
			reglist = json.loads(regdict)
			for reg in reglist:
				entity_add = reg['address']
				if timeleft == 0:
					contract.functions.reset(entity_add).transact()
				reg['ctbalance'] = contract.functions.retrieveBal(entity_add).call()
			return render_template('entities.html', reglist=reglist)
		else:
			flash('No entities have registered yet!')
			return render_template('index_master.html', availableSupply=availableSupply, price=price, limit=limit0)
	
if __name__ == '__main__':
	app.run(debug=True)