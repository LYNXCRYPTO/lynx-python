from lynx.freezer import Freezer
from lynx.blockchain import Blockchain, RECEIVER, SENDER_PRIVATE_KEY
from eth.vm.forks.lynx.blocks import LynxBlock

def test_freezer():
    blockchain : Blockchain = Blockchain.create_blockchain()
    
    genesis : LynxBlock = blockchain.get_canonical_block_by_number(0)

    Freezer.store_block(genesis, blockchain.chaindb)

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
    print(block)

    blockchain.persist_block(block, perform_validation=True)

    Freezer.store_block(block, blockchain.chaindb)

    print(Freezer.get_block_by_number(block.number))


if __name__ == '__main__':
    test_freezer()