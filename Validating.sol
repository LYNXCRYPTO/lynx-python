// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.8.15;

library Types {
    struct Validator {
        address addr;
        uint256 stake;
        uint256 delegatedStake;
        uint256 totalStake;
        address[] delegators;
    }

    struct Delegator {
        address addr;
        uint256 totalDelegatedStake;
        mapping(address => uint256) delegatedValidators; // Mapping of validator's address to delegated stake amount
    }
}

contract Validating {
    // State variables that will be permanently stored in the blockchain
    uint256 public totalStaked;
    uint256 public totalStakeDelegated;
    uint256 public totalBonded;
    uint256 public numValidators;
    uint256 public numDelegators;
    mapping(address => Types.Validator) internal validators;
    mapping(address => Types.Delegator) internal delegators;

    // Events that will be emitted on changes
    event ValidatorAdded(address validator, uint256 stake);
    event ValidatorIncreasedStake(address validator, uint256 stakeIncrease);
    event ValidatorDecreasedStake(address validator, uint256 stakeDecrease);
    event ValidatorRemoved(address validator, uint256 stake);
    event DelegatorAdded(address delegator, address validator, uint256 stake);
    event DelegatorIncreasedStake(
        address delegator,
        address validator,
        uint256 stake
    );
    event DelegatorDecreasedStake(
        address delegator,
        address validator,
        uint256 stake
    );
    event DelegatorRemoved(address delegator, uint256 stake);

    constructor() {
        totalStaked = 0;
        totalStakeDelegated = 0;
        totalBonded = 0;
        numValidators = 0;
        numDelegators = 0;
    }

    function isValidator(address _validator) public view returns (bool) {
        return
            validators[_validator].addr != address(0) &&
            validators[_validator].stake > 0;
    }

    function addValidator(address _validator, uint256 _amount) public {
        Types.Validator memory newValidator = Types.Validator(
            _validator,
            _amount,
            0,
            _amount,
            new address[](0)
        );
        validators[_validator] = newValidator;

        addTotalStaked(_amount);
        numValidators++;

        emit ValidatorAdded(_validator, _amount);
    }

    function addStake(address _validator, uint256 _amount) public {
        validators[_validator].stake += _amount;
        addTotalStaked(_amount);
        emit ValidatorIncreasedStake(_validator, _amount);
    }

    function subtractStake(address _validator, uint256 _amount) public {
        validators[_validator].stake -= _amount;
        substractTotalStaked(_amount);
        emit ValidatorDecreasedStake(_validator, _amount);
    }

    function removeValidator(address _validator, uint256 _amount) public {
        delete validators[_validator];
        substractTotalStaked(_amount);
        numValidators--;
        emit ValidatorRemoved(_validator, _amount);
    }

    function stakeOf(address _validator) public view returns (uint256) {
        return validators[_validator].stake;
    }

    function getTotalStaked() public view returns (uint256) {
        return totalStaked;
    }

    function addTotalBonded(uint256 _amount) public {
        totalBonded += _amount;
    }

    function subtractTotalBonded(uint256 _amount) public {
        totalBonded -= _amount;
    }

    function addTotalStaked(uint256 _amount) public {
        totalStaked += _amount;
        addTotalBonded(_amount);
    }

    function substractTotalStaked(uint256 _amount) public {
        totalStaked -= _amount;
        subtractTotalBonded(_amount);
    }

    function addTotalDelegatedStaked(uint256 _amount) public {
        totalStakeDelegated += _amount;
        addTotalBonded(_amount);
    }

    function substractTotalDelegatedStaked(uint256 _amount) public {
        totalStakeDelegated -= _amount;
        subtractTotalBonded(_amount);
    }

    function depositStake() public payable {
        bool isValidating = isValidator(msg.sender);

        if (isValidating) {
            addStake(msg.sender, msg.value);
        } else {
            addValidator(msg.sender, msg.value);
        }
    }

    function withdrawStake(address payable _to, uint256 _amount) public {
        require(
            isValidator(msg.sender),
            "Sender is not currently a validator..."
        );
        require(
            _amount > validators[msg.sender].stake,
            "Sender does not have a sufficient amount staked currently..."
        );

        uint256 stake = validators[msg.sender].stake;
        if (_amount < stake) {
            subtractStake(msg.sender, _amount);
        } else {
            removeValidator(msg.sender, stake);
        }

        (bool success, ) = _to.call{value: _amount}("");
        require(success, "Withdraw failed...");
    }

    function isDelegator(address _delegator) public view returns (bool) {
        return
            validators[_delegator].addr != address(0) &&
            validators[_delegator].delegatedStake > 0;
    }

    function isValidatorDelegated(address _validator)
        public
        view
        returns (bool)
    {
        return delegators[msg.sender].delegatedValidators[_validator] > 0;
    }

    function delegateStake(address _validator, uint256 _amount) public {
        validators[_validator].delegators.push(msg.sender);
        validators[_validator].delegatedStake += _amount;
        validators[_validator].totalStake += _amount;
    }

    function addDelegator(address _validator, uint256 _amount) public {
        Types.Delegator storage newDelegator = delegators[msg.sender];

        newDelegator.addr = msg.sender;
        newDelegator.totalDelegatedStake = _amount;
        newDelegator.delegatedValidators[_validator] = _amount;

        delegateStake(_validator, _amount);

        addTotalDelegatedStaked(_amount);
        numDelegators++;

        emit DelegatorAdded(msg.sender, _validator, _amount);
    }

    function subtractDelegatedStake(address _validator, uint256 _amount)
        public
    {
        uint256 numOfDelegators = validators[_validator].delegators.length;
        for (uint64 i; i < numOfDelegators; i++) {
            if (msg.sender == validators[_validator].delegators[i]) {
                validators[_validator].delegators[i] = validators[_validator]
                    .delegators[numOfDelegators - 1];
                validators[_validator].delegators.pop();
            }
        }

        validators[_validator].delegatedStake -= _amount;
        validators[_validator].totalStake -= _amount;

        delegators[msg.sender].delegatedValidators[_validator] -= _amount;
        delegators[msg.sender].totalDelegatedStake -= _amount;

        substractTotalDelegatedStaked(_amount);

        emit DelegatorDecreasedStake(msg.sender, _validator, _amount);
    }

    function removeDelegator(uint256 _amount) public {
        delete delegators[msg.sender];
        substractTotalDelegatedStaked(_amount);
        numDelegators--;
        emit DelegatorRemoved(msg.sender, _amount);
    }

    function addDelegatedStake(address _validator, uint256 _amount) public {
        delegators[msg.sender].delegatedValidators[_validator] += _amount;
        delegators[msg.sender].totalDelegatedStake += _amount;

        delegateStake(_validator, _amount);

        addTotalDelegatedStaked(_amount);

        emit DelegatorIncreasedStake(msg.sender, _validator, _amount);
    }

    function depositDelegatedStake(address _validatorToStake, uint256 _amount)
        public
        payable
    {
        require(
            isDelegator(_validatorToStake),
            "Can't delegate stake because validator doesn't exist..."
        );

        bool isDelegating = isValidatorDelegated(_validatorToStake);

        if (isDelegating) {
            addDelegatedStake(_validatorToStake, _amount);
        } else {
            addDelegator(_validatorToStake, _amount);
        }
    }

    function withdrawDelegatedStake(
        address payable _to,
        address _validator,
        uint256 _amount
    ) public {
        require(
            isDelegator(msg.sender),
            "Sender is not currently a delegator..."
        );
        require(
            isValidator(_validator),
            "Can't withdraw delegated stake becase validator is not currently validating"
        );
        require(
            isValidatorDelegated(_validator),
            "Can't withdraw delegated stake because sender is not currently delegating to the specified validator"
        );
        require(
            _amount > validators[msg.sender].stake,
            "Sender does not have a sufficient amount of stake delegated currently..."
        );

        uint256 delegatedStake = delegators[msg.sender].totalDelegatedStake;
        if (_amount < delegatedStake) {
            subtractDelegatedStake(msg.sender, _amount);
        } else {
            removeDelegator(delegatedStake);
        }

        (bool success, ) = _to.call{value: _amount}("");
        require(success, "Withdraw failed...");
    }
}
