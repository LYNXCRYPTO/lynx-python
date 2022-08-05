from lynx.consensus.leader_schedule import LeaderSchedule
from lynx.wallet import Wallet
from lynx.consensus.epoch import Epoch


def test_leader_schedule():
    wallet = Wallet()
    epoch = Epoch(start=0, slot_num=10, slot_length=10)

    LeaderSchedule.generate_campaign(epoch=epoch, wallet=wallet)

if __name__ == '__main__':
    test_leader_schedule()