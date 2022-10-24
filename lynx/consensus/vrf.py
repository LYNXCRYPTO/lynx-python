from typing import Tuple
from eth_typing import BlockNumber, Address
from eth_account import Account
from eth_account.messages import encode_defunct


class VRF:
    """
    A class definition for generating psuedo-random numbers
    completely unique to an account. Potentially going to be
    used for block leader elections.
    """

    @classmethod
    def generate_random_number(cls, block_number: BlockNumber, account: Account) -> Tuple[int, int]:
        """
        Generates a psuedorandom number based on an account's private keys. Uses the Account 
        object to manage the account's private keys.
        """
        
        message_hash = encode_defunct(text=str(block_number))
        
        signed_message = account.sign_message(message_hash)

        return (block_number, int.from_bytes(signed_message.signature, 'big'))


        
    @classmethod 
    def verify_random_number(cls, block_number: BlockNumber, address: Address, campaign: int) -> bool:
        """
        Verifies the a validator's campaign to see whether it was actually signed by their corresponding
        private key. In order for this function to evaluate successful, the block number in which the validator
        generates a campaign for must be signed by their private key.
        """

        message_hash = encode_defunct(text=str(block_number))

        address_hex = Account.recover_message(signable_message=message_hash, signature=campaign)

        account_address = Address(bytes.fromhex(address_hex[2:]))

        return account_address == address

