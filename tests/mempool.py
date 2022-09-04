from lynx.p2p.mempool import Mempool
from eth.vm.forks.lynx import LynxVM
from eth.vm.forks.lynx.transactions import LynxTransaction
from eth_typing import Address
from eth_keys import keys

def test_mempool():
    SENDER_PRIVATE_KEY = keys.PrivateKey(bytes.fromhex('45a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d8'))
    SENDER_ADDRESS = Address(SENDER_PRIVATE_KEY.public_key.to_canonical_address())

    mempool = Mempool(tx_expire_time=20)

    tx = LynxVM.create_unsigned_transaction(
            nonce=0,
            gas_price=0,
            gas=1000000,
            to=b'',
            value=20,
            data=b''
        )

    print(type(tx))

    signed_tx = tx.as_signed_transaction(private_key=SENDER_PRIVATE_KEY)

    print(type(signed_tx))

    mempool.add_transaction(signed_tx)

    print(signed_tx.as_dict())

    # mempool.start_expiry_listener()


if __name__ == "__main__":
    test_mempool()