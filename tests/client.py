from lynx.p2p.node import Node
from lynx.p2p.message import Message, MessageFlag
from lynx.p2p.peer import Peer
from lynx.constants import *
from eth.vm.forks.lynx.blocks import LynxBlock
from eth.chains.lynx import LynxChain, LYNX_VM_CONFIGURATION
from eth.db.atomic import AtomicDB
from eth_typing import Address
from eth_keys import keys
import threading


def test_client():
    node = Node(port='6969', peers=[Peer(address='127.0.0.1', port='6968')])

    SENDER_PRIVATE_KEY = keys.PrivateKey(bytes.fromhex('45a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d8'))
    SENDER_ADDRESS = Address(SENDER_PRIVATE_KEY.public_key.to_canonical_address())

    GENESIS_PARAMS = {'timestamp': 1514764800}

    GENESIS_STATE = {
        SENDER_ADDRESS : {
            'balance': 69,
            'nonce': 0,
            'code': b'',
            'storage': {},
        }
    }

    blockchain_config = LynxChain.configure(
                __name__='LynxChain',
                vm_configuration=LYNX_VM_CONFIGURATION,
            )   
        
    blockchain : LynxChain = blockchain_config.from_genesis(AtomicDB(), GENESIS_PARAMS, GENESIS_STATE)
    
    genesis : LynxBlock = blockchain.get_canonical_block_by_number(block_number=0)

    vm = blockchain.get_vm()

    tx = vm.create_unsigned_transaction(
            nonce=0,
            gas_price=0,
            gas=1000000,
            to=SENDER_ADDRESS,
            value=20,
            data=b''
        )

    signed_tx = tx.as_signed_transaction(private_key=SENDER_PRIVATE_KEY)

    blockchain.apply_transaction(signed_tx)

    blockchain.forge_block()

    block : LynxBlock = blockchain.get_canonical_block_by_number(1)

    version_request_thread = threading.Thread(target=node.broadcast, args=[MessageFlag.CAMPAIGN, node.peers], name='Client Thread')
    version_request_thread.start()


if __name__ == "__main__":
    test_client()
 