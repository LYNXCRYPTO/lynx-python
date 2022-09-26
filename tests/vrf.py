from lynx.consensus.vrf import VRF
from eth_account import Account
from eth_typing import Address


def test_vrf():
    account = Account.create()

    block_number, campaign = VRF.generate_random_number(block_number=1, account=account)

    address_bytes = bytes.fromhex(account.address[2:])
    address = Address(address_bytes)

    valid_vrf = VRF.verify_random_number(block_number=block_number, address=address, campaign=campaign)

    print(valid_vrf)
    
    


if __name__ == "__main__":
    test_vrf()
