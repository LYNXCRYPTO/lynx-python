from eth.chains.base import MiningChain
from eth_typing import Address
from eth.db.atomic import AtomicDB
from eth_keys import keys
from eth_utils import ValidationError
from eth.tools.builder.chain.builders import disable_pow_check
from eth.constants import GENESIS_BLOCK_NUMBER
from eth.vm.forks.lynx import LynxVM

SENDER_PRIVATE_KEY = keys.PrivateKey(bytes.fromhex('45a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d8'))
SENDER_ADDRESS = Address(SENDER_PRIVATE_KEY.public_key.to_canonical_address())
RECEIVER = Address(b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x02')

GENESIS_PARAMS = {'gas_limit': 3141592, 'timestamp': 1514764800,}

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

    def verify_block(self) -> bool:
        vm = self.get_vm(self.header)
        current_block = vm.get_block()

        try:
            
            self.validate_block(current_block)

            self.chaindb.persist_block(current_block)
            self.header = self.create_header_from_parent(current_block.header)
        except ValidationError as error:
            print(error)
            return False
        return True

    