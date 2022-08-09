// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.8.15;

contract Validation {
    function isValidator(address _validator) public view returns (bool);

    function addTotalBonded(uint256 _amount) public;

    function subtractTotalBonded(uint256 _amount) public;

    function delegateStake(
        address _delegator,
        address _validator,
        uint256 _amount
    ) public;
}

contract Delegation {
    // Validation Contract
    Validation validation;

    // Structure representing a delegator and their attributes
    struct Delegator {
        address addr;
        uint256 totalDelegatedStake;
        mapping(address => uint256) delegatedValidators; // Mapping of validator's address to delegated stake amount
    }

    // ***************
    // Accounting Variables
    // ***************
    uint256 public totalStakeDelegated;
    mapping(uint256 => uint256) public numDelegators; // Mapping of block number to number of delegators at that time
    mapping(address => Delegator) public delegators;

    // ***************
    // Delegator Events
    // ***************
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
    event DelegatorPenalized(address delegator, uint256 penalty);

    // ***************
    // Constructor
    // ***************
    constructor() {
        // TODO: Add valdidation contract address to constructor (Voting.validationContractAddress)
        validation = Validation(address(0));
    }

    // ***************
    // Getter Functions
    // ***************
    function isDelegator(address _delegator) public view returns (bool) {
        return
            delegators[_delegator].addr != address(0) &&
            delegators[_delegator].totalDelegatedStake > 0;
    }

    function isValidatorDelegated(address _delegator, address _validator)
        public
        view
        returns (bool)
    {
        require(
            isDelegator(_delegator),
            "Provided delegator isn't delegating currently..."
        );
        require(
            validation.isValidator(_validator),
            "Provided delegator isn't delegating currently..."
        );
        return delegators[_delegator].delegatedValidators[_validator] > 0;
    }

    // ***************
    // Helper Functions
    // ***************
    function addTotalDelegatedStaked(uint256 _amount) private {
        totalStakeDelegated += _amount;
        validation.addTotalBonded(_amount);
    }

    function substractTotalDelegatedStaked(uint256 _amount) private {
        totalStakeDelegated -= _amount;
        validation.subtractTotalBonded(_amount);
    }

    function getTotalDelegatedStakeOf(address _delegator)
        public
        view
        returns (uint256)
    {
        require(
            isDelegator(_delegator),
            "Provided delegator is not currently validating..."
        );
        return delegators[_delegator].totalDelegatedStake;
    }

    function getDelegatedStakeOf(address _delegator, address _validator)
        public
        view
        returns (uint256)
    {
        require(
            isDelegator(_delegator),
            "Provided delegator is not currently validating..."
        );
        require(
            validation.isValidator(_validator),
            "Provided validator is not currently validating..."
        );
        require(
            isValidatorDelegated(_delegator, _validator),
            "Delegator is not currently delegated to the provided validator..."
        );
        return delegators[_delegator].delegatedValidators[_validator];
    }

    function addDelegator(
        address _delegator,
        address _validator,
        uint256 _amount
    ) private {
        validation.delegateStake(_delegator, _validator, _amount);

        delegators[_delegator].addr = _delegator;
        delegators[_delegator].totalDelegatedStake = _amount;
        delegators[_delegator].delegatedValidators[_validator] = _amount;

        addTotalDelegatedStaked(_amount);
        numDelegators[block.number + 1]++;

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
        numDelegators[block.number + 1]--;
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

    // ***************
    // Payable Functions
    // ***************
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
            validation.isValidator(_validator),
            "Can't withdraw delegated stake becase validator is not currently validating..."
        );
        require(
            isValidatorDelegated(msg.sender, _validator),
            "Can't withdraw delegated stake because sender is not currently delegating to the specified validator..."
        );
        require(
            _amount > validation.validators[msg.sender].stake,
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
