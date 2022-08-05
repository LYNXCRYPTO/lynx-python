// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.8.15;

contract Validating {
    uint256 public totalStaked;
    mapping(address => uint256) internal validators;

    // Events that will be emitted on changes
    event ValidatorAdded(address validator, uint256 stake);
    event ValidatorIncreasedStake(address validator, uint256 stakeIncrease);
    event ValidatorDecreasedStake(address validator, uint256 stakeDecrease);
    event ValidatorRemoved(address validator, uint256 stake);

    constructor() {
        totalStaked = 0;
    }

    function isValidator(address _validator) public view returns (bool) {
        return validators[_validator] != 0;
    }

    function addStake(address _validator, uint256 _amount) public {
        bool isValidating = isValidator(_validator);

        validators[_validator] += _amount;
        totalStaked += _amount;

        if (isValidating) {
            emit ValidatorIncreasedStake(_validator, _amount);
        } else {
            emit ValidatorAdded(_validator, _amount);
        }
    }

    function removeStake(address _validator, uint256 _amount) public {
        uint256 stake = validators[_validator];
        validators[_validator] -= _amount;

        totalStaked -= _amount;

        if (_amount < stake) {
            emit ValidatorDecreasedStake(_validator, _amount);
        } else {
            emit ValidatorRemoved(_validator, stake);
        }
    }

    function stakeOf(address _validator) public view returns (uint256) {
        return validators[_validator];
    }

    function getTotalStake() public view returns (uint256) {
        return totalStaked;
    }

    function depositStake() public payable {
        require(
            msg.value <= msg.sender.balance,
            "Sender does not have a sufficient balance..."
        );

        addStake(msg.sender, msg.value);
    }

    function withdrawStake(address payable _to, uint256 _amount) public {
        require(
            isValidator(msg.sender),
            "Sender is not currently a validator..."
        );
        require(
            _amount <= validators[msg.sender],
            "Sender does not have a sufficient amount staked currently..."
        );

        uint256 stake = validators[msg.sender];
        (bool success, ) = _to.call{value: stake}("");
        require(success, "Withdraw failed...");

        removeStake(msg.sender, _amount);
    }
}
