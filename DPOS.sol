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

contract DPOS {
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

    function addValidator(address _validator, uint256 _amount) private {
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

    function addStake(address _validator, uint256 _amount) private {
        validators[_validator].stake += _amount;
        addTotalStaked(_amount);
        emit ValidatorIncreasedStake(_validator, _amount);
    }

    function subtractStake(address _validator, uint256 _amount) private {
        validators[_validator].stake -= _amount;
        substractTotalStaked(_amount);
        emit ValidatorDecreasedStake(_validator, _amount);
    }

    function removeValidator(address _validator, uint256 _amount) private {
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

    function addTotalBonded(uint256 _amount) private {
        totalBonded += _amount;
    }

    function subtractTotalBonded(uint256 _amount) private {
        totalBonded -= _amount;
    }

    function addTotalStaked(uint256 _amount) private {
        totalStaked += _amount;
        addTotalBonded(_amount);
    }

    function substractTotalStaked(uint256 _amount) private {
        totalStaked -= _amount;
        subtractTotalBonded(_amount);
    }

    function addTotalDelegatedStaked(uint256 _amount) private {
        totalStakeDelegated += _amount;
        addTotalBonded(_amount);
    }

    function substractTotalDelegatedStaked(uint256 _amount) private {
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

    function withdrawStake(address _to, uint256 _amount) public payable {
        require(
            isValidator(msg.sender),
            "Sender is not currently a validator..."
        );
        require(
            _amount > validators[msg.sender].stake,
            "Sender does not have a sufficient amount staked currently..."
        );
        require(payable(_to).send(0), "To address is not payable...");

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

    function isValidatorDelegated(address _delegator, address _validator)
        public
        view
        returns (bool)
    {
        return delegators[_delegator].delegatedValidators[_validator] > 0;
    }

    function delegateStake(
        address _delegator,
        address _validator,
        uint256 _amount
    ) private {
        validators[_validator].delegators.push(_delegator);
        validators[_validator].delegatedStake += _amount;
        validators[_validator].totalStake += _amount;
    }

    function addDelegator(
        address _delegator,
        address _validator,
        uint256 _amount
    ) private {
        Types.Delegator storage newDelegator = delegators[_delegator];

        newDelegator.addr = _delegator;
        newDelegator.totalDelegatedStake = _amount;
        newDelegator.delegatedValidators[_validator] = _amount;

        delegateStake(_delegator, _validator, _amount);

        addTotalDelegatedStaked(_amount);
        numDelegators++;

        emit DelegatorAdded(_delegator, _validator, _amount);
    }

    function subtractDelegatedStake(
        address _delegator,
        address _validator,
        uint256 _amount
    ) private {
        uint256 numOfDelegators = validators[_validator].delegators.length;
        for (uint64 i; i < numOfDelegators; i++) {
            if (_delegator == validators[_validator].delegators[i]) {
                validators[_validator].delegators[i] = validators[_validator]
                    .delegators[numOfDelegators - 1];
                validators[_validator].delegators.pop();
            }
        }

        validators[_validator].delegatedStake -= _amount;
        validators[_validator].totalStake -= _amount;

        delegators[_delegator].delegatedValidators[_validator] -= _amount;
        delegators[_delegator].totalDelegatedStake -= _amount;

        substractTotalDelegatedStaked(_amount);

        emit DelegatorDecreasedStake(_delegator, _validator, _amount);
    }

    function removeDelegator(address _delegator, uint256 _amount) private {
        delete delegators[_delegator];
        substractTotalDelegatedStaked(_amount);
        numDelegators--;
        emit DelegatorRemoved(_delegator, _amount);
    }

    function addDelegatedStake(
        address _delegator,
        address _validator,
        uint256 _amount
    ) private {
        delegators[_delegator].delegatedValidators[_validator] += _amount;
        delegators[_delegator].totalDelegatedStake += _amount;

        delegateStake(_delegator, _validator, _amount);

        addTotalDelegatedStaked(_amount);

        emit DelegatorIncreasedStake(_delegator, _validator, _amount);
    }

    function depositDelegatedStake(address _validatorToStake, uint256 _amount)
        public
        payable
    {
        require(
            isDelegator(_validatorToStake),
            "Can't delegate stake because validator doesn't exist..."
        );

        bool isDelegating = isValidatorDelegated(msg.sender, _validatorToStake);

        if (isDelegating) {
            addDelegatedStake(msg.sender, _validatorToStake, _amount);
        } else {
            addDelegator(msg.sender, _validatorToStake, _amount);
        }
    }

    function withdrawDelegatedStake(
        address _to,
        address _validator,
        uint256 _amount
    ) public payable {
        require(
            isDelegator(msg.sender),
            "Sender is not currently a delegator..."
        );
        require(
            isValidator(_validator),
            "Can't withdraw delegated stake becase validator is not currently validating..."
        );
        require(
            isValidatorDelegated(msg.sender, _validator),
            "Can't withdraw delegated stake because sender is not currently delegating to the specified validator..."
        );
        require(
            _amount > validators[msg.sender].stake,
            "Sender does not have a sufficient amount of stake delegated currently..."
        );
        require(payable(_to).send(0), "To address is not payable...");

        uint256 delegatedStake = delegators[msg.sender].totalDelegatedStake;
        if (_amount < delegatedStake) {
            subtractDelegatedStake(msg.sender, _validator, _amount);
        } else {
            removeDelegator(msg.sender, delegatedStake);
        }

        (bool success, ) = _to.call{value: _amount}("");
        require(success, "Withdraw failed...");
    }
}
