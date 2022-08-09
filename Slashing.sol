// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.8.15;

import "./Validation.sol";
import "./Delegation.sol";

contract Slashing {
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
