import traceback
from lynx.forks.lynx.blocks import LynxBlock, LynxBlockHeader
from lynx.wallet import Wallet
from lynx.blockchain import Blockchain
from eth.chains.base import MiningChain
from eth_typing import Address
from eth.constants import ZERO_ADDRESS, ZERO_HASH32, GENESIS_BLOCK_NUMBER
from eth_keys import keys
from eth.vm.forks.arrow_glacier import ArrowGlacierVM
from eth.vm.forks.byzantium import ByzantiumVM
from eth.vm.forks.berlin import BerlinVM
from eth.vm.forks.berlin.blocks import BerlinBlock
from lynx.forks import LynxVM
from eth.db.atomic import AtomicDB
from eth.consensus.pow import mine_pow_nonce
from eth.tools.builder import chain
from lynx.blockchain import RECEIVER, SENDER_PRIVATE_KEY, SENDER_ADDRESS
import json
from eth.vm.header import HeaderSedes

def test_blockchain():

    blockchain : Blockchain = Blockchain.create_blockchain()
    
    genesis : BerlinBlock = blockchain.get_canonical_block_by_number(0)
    blockchain2 = chain.builders.copy(blockchain)

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

    blockchain.persist_block(block, perform_validation=False)
    print(blockchain.get_canonical_head().as_dict())
    # print(blockchain.get_canonical_block_by_number(0).header)
    # nonce, mix_hash = mine_pow_nonce(
    #     block.number,
    #     block.header.mining_hash,
    #     block.header.difficulty
    # )



    # # print()
    # blockchain.mine_block(mix_hash=mix_hash, nonce=nonce)
    # blockchain.validate_block()
    # # print()
    # print(genesis.header)
    # print(blockchain.get_canonical_block_header_by_number(1))
    # print(blockchain2.get_canonical_head())
    # print(blockchain2.import_block(blockchain.get_canonical_block_by_number(1), perform_validation=True))
    # print(blockchain2.get_canonical_head())
    # # blockchain.chaindb.db.set(b'12345', 'hello'.encode())
    # print(blockchain.chaindb.db.get(b'12345').decode())

if __name__ == '__main__':
    test_blockchain()