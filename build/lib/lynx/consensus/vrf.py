from lynx.account import Account
import ecdsa


class VRF:
    """
    A class definition for generating psuedo-random numbers
    completely unique to an account. Potentially going to be
    used for block leader elections.
    """

    @classmethod
    def generate_random_number(self, account: Account) -> int:

        return 0
