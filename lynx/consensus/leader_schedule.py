from lynx.consensus.epoch import Epoch
from lynx.wallet import Wallet
from lynx.consensus.vrf import VRF
from eth_typing import BlockNumber

class LeaderSchedule:

    @classmethod
    def generate_campaign(cls, epoch: Epoch, wallet: Wallet) -> tuple:
        """Generates ten 256-bit random numbers to attempt to be
        elected as block leader for one of the slots in the current epoch."""
        rand_nums = []
        for block_number in range(epoch.start, epoch.end, epoch.slot_length):
            rand_num: int = VRF.generate_random_number(block_number=block_number, stake=69, wallet=wallet)
            rand_nums.append(rand_num)
            print(f'Random Number Generated for block {block_number}: {str(rand_num)[:10]}...')

        return tuple(rand_nums)

        
