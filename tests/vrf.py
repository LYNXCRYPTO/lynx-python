from lynx.wallet import Wallet
from lynx.consensus.vrf import VRF


def test_vrf():
    wallet = Wallet()

    rand_num = VRF.generate_random_number(block_number=1, stake=2, wallet=wallet)

    print(rand_num)
    
    


if __name__ == "__main__":
    test_vrf()
