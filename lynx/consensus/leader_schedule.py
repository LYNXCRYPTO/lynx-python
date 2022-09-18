import threading
from typing import Tuple, Dict
from eth_typing import Address
from lynx.consensus.epoch_context import EpochContext
from lynx.consensus.vrf import VRF
from eth_account import Account
from eth_typing import BlockNumber


class Leader:

    def __init__(self, address: Address, stake: int, campaign: int) -> None:
        """"""

        self.address = address
        self.stake = stake
        self.campaign = campaign


class LeaderSchedule:

    def __init__(self) -> None:
        """"""

        self.leader_schedule : Dict[BlockNumber, Leader] = {}
        self.leader_lock = threading.Lock()

    
    def __str__(self) -> str:
        """"""

        return self.leader_schedule.__str__()


    @classmethod
    def generate_campaign(cls, epoch: EpochContext, account: Account) -> tuple:
        """Generates ten 256-bit random numbers to attempt to be
        elected as block leader for one of the slots in the current epoch."""

        rand_nums = []
        for block_number in range(epoch.start, epoch.end, epoch.slot_size):
            rand_num: Tuple[int, int] = VRF.generate_random_number(block_number=block_number, stake=69, account=account)
            rand_nums.append(rand_num)
            print(f'Random Number Generated for Block {block_number}: {str(rand_num)[:10]}...')

        return rand_nums

    
    def add_leader(self, block_number: BlockNumber, leader: Leader) -> None:
        """"""
        self.leader_lock.acquire()
        if block_number in self.leader_schedule:
            current_leader : Leader = self.leader_schedule[block_number]
            if leader.campaign <= current_leader:
                raise ValueError

        self.leader_schedule[block_number] = leader
        self.leader_lock.release()
        
    
    def get_leader_by_block_number(self, block_number: BlockNumber) -> Tuple[int, int]:
        """"""

        if block_number in self.leader_schedule:
            return self.leader_schedule[block_number]
        
        return None
        
    
        
