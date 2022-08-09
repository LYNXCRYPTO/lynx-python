// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.8.15;

contract Delegation {
    function isDelegator(address _delegator) public view returns (bool);
}

contract Validation {
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

    Delegation delegation;

    // ***************
    // Accounting variables
    // ***************
    uint256 public totalStaked;
    uint256 public totalBonded; // The total amount of lynx staked and delegated within the system
    mapping(uint256 => uint256) public numValidators; // Mapping of block number to number of validators at that time
    mapping(address => Validator) public validators;

    // ***************
    // Votable variables
    // ***************
    uint256 public penaltyThreshold; // The amount of reports needed to penalize a validator
    uint256 public penalty; // The percent of a validator's stake to be slashed
    uint64 public decisionThreshold; // The number of consecutive successes required for a block to be finalized
    uint64 public slotSize; // The number of blocks included in each slot
    uint64 public epochSize; // The number of slots included in each epoch

    // ***************
    // Validator Events
    // ***************
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

    // ***************
    // Constructor
    // ***************
    constructor() {
        // TODO: Add valdidation contract address to constructor (Voting.delegationContractAddress)
        delegation = Delegation(address(0));

        slotSize = 10; // 10 blocks per slot
        epochSize = 10; // 10 slots per epoch

        decisionThreshold = 20; // 20 consecutive successes required for a block to be finalized

        // Because Solidity only allows for integer division, we use a int
        // that is 0 < x <= 100,000 to represent a decimal with three decimal places.
        penaltyThreshold = 66666; // 66.666% penalty threshold
        penalty = 2000; // 2.000% penalty enforced
    }

    // ***************
    // Getter Functions
    // ***************
    function isValidator(address _validator) public view returns (bool) {
        return
            validators[_validator].addr != address(0) &&
            validators[_validator].stake > 0;
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

    // ***************
    // Helper Functions
    // ***************
    function addTotalBonded(uint256 _amount) public {
        // TODO: Make sure to require that msg.sender == Voting.delegationContractAddress
        totalBonded += _amount;
    }

    function subtractTotalBonded(uint256 _amount) public {
        // TODO: Make sure to require that msg.sender == Voting.delegationContractAddress
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

    function delegateStake(
        address _delegator,
        address _validator,
        uint256 _amount
    ) public {
        require(
            delegation.isDelegator(_delegator),
            "Provided delegator isn't delgating currently..."
        );
        require(
            isValidator(_delegator),
            "Provided delegator isn't delgating currently..."
        );
        validators[_validator].delegators.push(_delegator);
        validators[_validator].delegatedStake += _amount;
        validators[_validator].totalStake += _amount;
    }

    // ***************
    // Payable Functions
    // ***************
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
}
