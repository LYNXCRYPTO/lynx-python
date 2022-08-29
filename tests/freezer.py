from lynx.freezer import Freezer
from lynx.blockchain import RECEIVER, SENDER_PRIVATE_KEY, GENESIS_BLOCK_NUMBER, GENESIS_PARAMS, GENESIS_STATE
from eth.vm.forks.lynx.blocks import LynxBlock
from eth.vm.forks.lynx import LynxVM
from eth.chains.lynx import LynxChain
from eth.db.atomic import AtomicDB

def test_freezer():
    blockchain_config = LynxChain.configure(
            __name__='LynxChain',
            vm_configuration=((GENESIS_BLOCK_NUMBER, LynxVM),
        )   
    )
        
    blockchain : LynxChain = blockchain_config.from_genesis(AtomicDB(), GENESIS_PARAMS, GENESIS_STATE) # pylint: disable=no-member
    
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

    vm : LynxVM = blockchain.get_vm()

    block = blockchain.get_block()

    blockchain.forge_block()

    Freezer.store_block(block, blockchain.chaindb)

    print(Freezer.get_block_by_number(block.number))


if __name__ == '__main__':
    test_freezer()