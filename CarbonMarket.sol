pragma solidity ^0.5.0;

contract CarbonMarket {
	uint public marketSupply;
	uint public price;
	uint public createTime;
	uint public limit;
	uint public translock;
	address public marketmaker;
	string public regdict = '[]';

	// Define events
	event Registration(address indexed _address, string _name);
	event Buy(address indexed _address, uint _amount);
	event Donation(address indexed _from, address indexed _to, uint _amount);
	event PutOnMarket(address indexed _seller, uint _amount);
	event Transaction(address indexed _seller, address indexed _buyer, uint _amount);

	// Creating Entity structure
	struct Entity {
		string name;
		uint balance;
	}

	// Tracking registered Ethereum addresses and market
	mapping (address => bool) public registeredEntities;
	mapping (address => Entity) public entityDetails;

	// User registration
	function register(string memory _name, string memory _dict) public {
		bool cond0 = (msg.sender != marketmaker);
		bool cond1;
		bytes memory emptystringtest = bytes(_name);
		if (emptystringtest.length == 0) {
			cond1 = false;
		} else {
			cond1 = true;
		}
		require(cond0 && cond1, "Invalid name.");
		registeredEntities[msg.sender] = true;
		entityDetails[msg.sender].name = _name;
		entityDetails[msg.sender].balance = 0;
		// updating register dict
		regdict = _dict;
		emit Registration(msg.sender, _name);
	}

	// Retrieve own name
	function myName() public view returns (string memory) {
		return entityDetails[msg.sender].name;
	}

	// Buy function
	function buy() public payable {
		uint userbal = returnBalance();
		entityDetails[msg.sender].balance = userbal;
		bool cond0 = (msg.sender != marketmaker);
		bool cond1 = (registeredEntities[msg.sender] == true);
		bool cond2 = (msg.value % price == 0);
		bool cond3 = (msg.value / price <= marketSupply);
		bool cond4 = expiry();
		if (cond4) {
			entityDetails[msg.sender].balance = 0;
		}
		require(cond0 && cond1 && cond2 && cond3, "Either you are not a registered user or your deposit amount is invalid or there is insufficient number of tokens available.");
		uint _deposit = msg.value / price;
		entityDetails[msg.sender].balance += _deposit;
		marketSupply -= _deposit;
		emit Buy(msg.sender, _deposit);
	}

	// Donate function
	function donate(address _address, uint _donation) public {
		uint userbal = returnBalance();
		entityDetails[msg.sender].balance = userbal;
		bool cond1 = (registeredEntities[_address] == true);
		bool cond2 = (entityDetails[msg.sender].balance >= _donation);
		bool cond3 = (registeredEntities[msg.sender] == true);
		bool cond4 = expiry();
		if (cond4) {
			entityDetails[msg.sender].balance = 0;
		}
		require(cond1 && cond2 && cond3, "Invalid address or donation amount.");
		entityDetails[msg.sender].balance -= _donation;
		entityDetails[_address].balance += _donation;
		emit Donation(msg.sender, _address, _donation);
	}

	// Sell function
	function sell(uint amount) public {
		uint userbal = returnBalance();
		entityDetails[msg.sender].balance = userbal;
		bool cond = (createTime + limit - now) > translock;
		bool cond2 = expiry();
		if (cond2) {
			entityDetails[msg.sender].balance = 0;
		}
		require(cond, "You are unable to sell any further tokens this year.");
		require(amount <= entityDetails[msg.sender].balance, "Insufficient balance.");
		marketSupply += amount;
		entityDetails[msg.sender].balance -= amount;
		msg.sender.transfer(amount * price);
		emit PutOnMarket(msg.sender, amount);
	}

	// Market Balance
	function AvailableTokens() public view returns (uint) {
		return marketSupply;
	}

	// Return balance
	function returnBalance() public view returns (uint) {
		uint TimeLeft = returnTimeRemaining();
		if (TimeLeft > 0) {
			return entityDetails[msg.sender].balance;
		} else {
			return 0;
		}
	}

	
	// Returns Time Elapsed
	function returnTimeElapsed() public view returns (uint) {
		return (now - createTime);
	}

	// Returns Time Remaining
	function returnTimeRemaining() public view returns (uint) {
		if ((createTime + limit) > now) {
			return (createTime + limit - now);
		} else {
			return 0;
		}
	}

	// Set Market
	function setMarket(uint _supply, uint _price, uint _limit, uint _translock) public {
		require(msg.sender == marketmaker, "You do not have the authorization of market maker.");
		price = _price;
		limit = _limit;
		createTime = now;
		marketSupply = _supply;
		if (_translock <= limit) {
			translock = _translock;
		} else {
			translock = limit;
		}
	}

	// check for expiry
	function expiry() internal view returns(bool) {
		if ((createTime + limit) > now) {
			return false;
		} else {
			return true;
		}
	}

	// Retrieve entity name
	function retrieveName(address _address) public view returns (string memory) {
		return entityDetails[_address].name;
	}

	// Retrieve entity balance
	function retrieveBal(address _address) public view returns (uint) {
		uint TimeLeft = returnTimeRemaining();
		if (TimeLeft > 0) {
			return entityDetails[_address].balance;
		} else {
			return 0;
		}
	}

	// Retrieve registration status
	function isRegistered() public view returns (bool) {
		return registeredEntities[msg.sender];
	}

	// Reset balance
	function reset(address _address) public {
		require(msg.sender == marketmaker, "You do not have the authorization of market maker.");
		entityDetails[_address].balance = 0;
	}

	// Reset self balance
	function resetself() public {
		bool cond = expiry();
		if (cond) {
			entityDetails[msg.sender].balance = 0;
		}
	}

	// Constructor function
	constructor () public {
		marketmaker = msg.sender;
		createTime = now;
		price = 1000000000000000;
		marketSupply = 1000000000;
		limit = 365 days;
		translock = 30 days;
	}
}