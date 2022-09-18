from lynx.consensus.leader_schedule import Leader, LeaderSchedule
from lynx.consensus.epoch_context import EpochContext
from lynx.consensus.vrf import VRF
from eth_account import Account
from eth.constants import ZERO_ADDRESS


def test_leader_schedule():
    account = Account.create()
    campaign = VRF.generate_random_number(1, account, 69)
    leader_schedule = LeaderSchedule()
    leader = Leader(address=ZERO_ADDRESS, stake=69, campaign=campaign)
    print("Before:")
    print(leader_schedule)

    leader_schedule.add_leader(1, leader)
    print("After:")
    print(leader_schedule)

if __name__ == '__main__':
    test_leader_schedule()