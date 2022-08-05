from eth.chains.base import MiningChain
from eth_typing import Address
from eth.db.atomic import AtomicDB
from eth_keys import keys
from eth_utils import (
    ValidationError, 
    encode_hex
)
from eth.tools.builder.chain.builders import disable_pow_check
from eth.constants import GENESIS_BLOCK_NUMBER
from eth.vm.forks.lynx import LynxVM
from eth.abc import (
    BlockAPI,
    BlockPersistResult
)

SENDER_PRIVATE_KEY = keys.PrivateKey(bytes.fromhex('45a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d8'))
SENDER_ADDRESS = Address(SENDER_PRIVATE_KEY.public_key.to_canonical_address())
RECEIVER = Address(b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x02')

GENESIS_PARAMS = {'gas_limit': 3141592, 'timestamp': 1514764800, 'epoch': 1}

GENESIS_STATE = {
    SENDER_ADDRESS : {
        'balance': 69,
        'nonce': 0,
        'code': b'',
        'storage': {},
    }
}

class Blockchain(MiningChain):

    @classmethod
    def create_blockchain(cls) -> 'Blockchain':
        blockchain_config = Blockchain.configure(
                __name__='LynxChain',
                vm_configuration=((GENESIS_BLOCK_NUMBER, LynxVM),
            )   
        )
        
        blockchain : 'Blockchain' = blockchain_config.from_genesis(AtomicDB(), GENESIS_PARAMS, GENESIS_STATE) # pylint: disable=no-member
        disable_pow_check(blockchain)
        
        return blockchain

    def validate_block(self, block: BlockAPI) -> None:
        if block.is_genesis:
            raise ValidationError("Cannot validate genesis block this way")
        vm = self.get_vm(block.header)
        parent_header = self.get_block_header_by_hash(block.header.parent_hash)
        vm.validate_header(block.header, parent_header)

    def persist_block(self, block: BlockAPI, perform_validation: bool = True) -> BlockPersistResult:
        
        if perform_validation:
            self.validate_block(block)

        new_canonical_hashes, old_canonical_hashes = self.chaindb.persist_block(block)

        self.logger.debug('Persisted block: number %s | hash %s', block.number, encode_hex(block.hash))

        new_canonical_blocks = tuple(self.get_block_by_hash(header_hash) for header_hash in new_canonical_hashes)
        old_canonical_blocks = tuple(self.get_block_by_hash(header_hash) for header_hash in old_canonical_hashes)

        return BlockPersistResult(imported_block=block, new_canonical_blocks=new_canonical_blocks, old_canonical_blocks=old_canonical_blocks,)

