// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.8.15;

library Types {
    struct Allegation {
        mapping(address => uint256) witnesses; // Mapping of reporter's address to the timestamp of when they reported it
        uint256 numWitnesses;
        uint256 totalStakeOfWitnesses;
    }

    struct Validator {
        address addr;
        uint256 stake;
        uint256 delegatedStake;
        uint256 totalStake;
        address[] delegators;
        mapping(uint256 => Allegation) allegations; // Mapping of block number to any allegations
    }

    struct Delegator {
        address addr;
        uint256 totalDelegatedStake;
        mapping(address => uint256) delegatedValidators; // Mapping of validator's address to delegated stake amount
    }
}

contract DPOS {
    uint256 public totalStaked;
    uint256 public totalStakeDelegated;
    uint256 public totalBonded; // totalStake + totalStakeDelegated
    mapping(uint256 => uint256) public numValidators; // Mapping of block number to number of validators at that time
    mapping(uint256 => uint256) public numDelegators; // Mapping of block number to number of delegators at that time
    mapping(address => Types.Validator) public validators;
    mapping(address => Types.Delegator) public delegators;

    // State variables which can be voted upon
    uint256 public penaltyThreshold; // The amount of reports needed to penalize a validator
    uint256 public penalty; // The percent of a validator's stake to be slashed
    uint64 public decisionThreshold; // The number of consecutive successes required for a block to be finalized
    uint64 public slotSize; // The number of blocks included in each slot
    uint64 public epochSize; // The number of slots included in each epoch

    // Events to be emitted on changes made to the validator set
    event ValidatorAdded(address validator, uint256 stake);
    event ValidatorIncreasedStake(address validator, uint256 stakeIncrease);
    event ValidatorDecreasedStake(address validator, uint256 stakeDecrease);
    event ValidatorRemoved(address validator, uint256 stake);
    event ValidatorReported(
        address reporter,
        address validator,
        uint256 blockNumber
    );
    event ValidatorPenalized(
        address validator,
        uint256 blockNumber,
        uint256 penalty
    );

    // Events to be emitted on changes made to the delegator set
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

    constructor() {
        // Initialing state variables which can be voted upon
        // by validators

        slotSize = 10; // 10 blocks per slot
        epochSize = 10; // 10 slots per epoch

        decisionThreshold = 20; // 20 consecutive successes required for a block to be finalized

        // Because Solidity only allows for integer division, we use a int
        // that is 0 < x <= 100,000 to represent a decimal with three decimal places.
        penaltyThreshold = 66666; // 66.666% penalty threshold
        penalty = 2000; // 2.000% penalty enforced
    }

    function isValidator(address _validator) public view returns (bool) {
        return
            validators[_validator].addr != address(0) &&
            validators[_validator].stake > 0;
    }

    function addValidator(address _validator, uint256 _amount) private {
        validators[_validator].addr = _validator;
        validators[_validator].stake = _amount;
        validators[_validator].delegatedStake = 0;
        validators[_validator].totalStake = _amount;

        addTotalStaked(_amount);
        numValidators[block.number + 1]++;

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
        numValidators[block.number + 1]--;
        emit ValidatorRemoved(_validator, _amount);
    }

    function getStakeOf(address _validator) public view returns (uint256) {
        require(
            isValidator(_validator),
            "Provided validator isn't validing currently..."
        );
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
        require(
            isDelegator(_delegator),
            "Provided delegator isn't delegating currently..."
        );
        require(
            isValidator(_validator),
            "Provided delegator isn't delegating currently..."
        );
        return delegators[_delegator].delegatedValidators[_validator] > 0;
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
            isValidator(_validator),
            "Provided validator is not currently validating..."
        );
        require(
            isValidatorDelegated(_delegator, _validator),
            "Delegator is not currently delegated to the provided validator..."
        );
        return delegators[_delegator].delegatedValidators[_validator];
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
        delegateStake(_delegator, _validator, _amount);

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

    function isReported(
        address accuser,
        address _validator,
        uint256 blockNumber
    ) public view returns (bool) {
        return
            validators[_validator].allegations[blockNumber].witnesses[
                accuser
            ] != 0;
    }

    function penalizeValidator(address _validator, uint256 blockNumber)
        private
    {
        uint256 validatorPenalty = (getStakeOf(_validator) * penalty) / 100000;
        subtractStake(_validator, validatorPenalty);

        uint256 numDelegatorsToValidator = validators[_validator]
            .delegators
            .length;

        for (uint256 i = 0; i < numDelegatorsToValidator; i++) {
            address delegator = validators[_validator].delegators[i];
            uint256 delegatorPenalty = getDelegatedStakeOf(
                delegator,
                _validator
            );
            subtractDelegatedStake(delegator, _validator, delegatorPenalty);
        }

        emit ValidatorPenalized(_validator, blockNumber, validatorPenalty);
    }

    function accuseValidator(address _validator, uint256 blockNumber)
        public
        payable
    {
        require(
            isValidator(msg.sender),
            "Non-validators can't report validators..."
        );
        require(
            isValidator(_validator),
            "Provided validator is not currently validating..."
        );
        require(
            !isReported(msg.sender, _validator, blockNumber),
            "Can't report a validator twice for the same block..."
        );
        require(
            block.number - blockNumber < decisionThreshold,
            "Block has been finalized and is unable to be reported anymore..."
        );

        validators[_validator].allegations[blockNumber].witnesses[
            msg.sender
        ] = block.timestamp;
        validators[_validator]
            .allegations[blockNumber]
            .totalStakeOfWitnesses += getStakeOf(msg.sender);
        validators[_validator].allegations[blockNumber].numWitnesses++;

        uint256 totalStakeOfWitnesses = validators[_validator]
            .allegations[blockNumber]
            .totalStakeOfWitnesses;

        // If the percentage of validator's stake that reported this user is
        // greater than the voted upon threshold, then the user should be penalized.
        if ((totalStakeOfWitnesses * 100000) / totalStaked > penaltyThreshold) {
            penalizeValidator(_validator, blockNumber);
        }
    }
}
