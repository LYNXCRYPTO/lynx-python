from eth_typing import BlockNumber
from lynx.wallet import Wallet


class VRF:
    """
    A class definition for generating psuedo-random numbers
    completely unique to an account. Potentially going to be
    used for block leader elections.
    """

    @classmethod
    def generate_random_number(self, block_number: BlockNumber, stake: int, wallet: Wallet) -> int:
        """Generates a psuedorandom number based on an account's
        private keys. Uses the Wallet object to manage the account's
        private keys.
        """
        
        signature = wallet.sign(block_number)

        rand_num = int.from_bytes(signature, 'big') * stake

        return rand_num


        


