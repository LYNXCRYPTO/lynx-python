from eth.vm.forks.lynx.blocks import LynxBlock, LynxBlockHeader
from lynx.blockchain import (
    Blockchain,
    RECEIVER, 
    SENDER_PRIVATE_KEY,
)

def test_blockchain():

    blockchain : Blockchain = Blockchain.create_blockchain()
    
    genesis : LynxBlock = blockchain.get_canonical_block_by_number(0)
    print(genesis.header.as_dict())

    # tx = blockchain.create_unsigned_transaction(
    #         nonce=0,
    #         gas_price=0,
    #         gas=100000,
    #         to=RECEIVER,
    #         value=20,
    #         data=b'Aliens are real!',
    #     )

    # signed_tx = tx.as_signed_transaction(private_key=SENDER_PRIVATE_KEY)

    # blockchain.apply_transaction(signed_tx)

    # blockchain.set_header_timestamp(genesis.header.timestamp + 1)

    # block_result = blockchain.get_vm().finalize_block(blockchain.get_block())
    # block = block_result.block

    # blockchain.persist_block(block, perform_validation=True)

    # print(LynxBlockHeader.serialize(blockchain.get_canonical_head()))


if __name__ == '__main__':
    test_blockchain()