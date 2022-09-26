from lynx.consensus.vdf import VDF
from lynx.generator import Generator
from lynx.consensus.vrf import VRF
from lynx.wallet import Wallet
from lynx.blockchain import (
    Blockchain,
    RECEIVER, 
    SENDER_PRIVATE_KEY,
)

def test_vdf():

    epoch: int = 100
    count: int = 0
    slot: int = 30

    wallet = Wallet()

    blockchain: Blockchain = Blockchain.create_blockchain()
    genesis = blockchain.get_canonical_block_by_number(0)

    tx = blockchain.create_unsigned_transaction(
            nonce=0,
            gas_price=0,
            gas=100000,
            to=RECEIVER,
            value=20,
            data=b'Aliens are real!',
        )

    signed_tx = tx.as_signed_transaction(private_key=SENDER_PRIVATE_KEY)

    blockchain.apply_transaction(signed_tx)

    blockchain.set_header_timestamp(genesis.header.timestamp + 1)

    block_result = blockchain.get_vm().finalize_block(blockchain.get_block())
    block = block_result.block

 
    # while count < epoch:
    #     if slot <= count < slot + 10:
    #         blockchain.persist_block(block, perform_validation=True)

    #     proof = VDF.sequential_squaring(n=713, a=2, t=100000000) # ~5 Second Delay
    #     print('~5 Seconds Elapsed...')


if __name__ == "__main__":
    test_vdf()