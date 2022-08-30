from lynx.freezer import Freezer
from lynx.blockchain import RECEIVER, SENDER_PRIVATE_KEY, GENESIS_BLOCK_NUMBER, GENESIS_PARAMS, GENESIS_STATE
from lynx.p2p.node import Node
from lynx.p2p.peer import Peer
from eth.vm.forks.lynx.blocks import LynxBlock
from eth.vm.forks.lynx import LynxVM
from eth.chains.lynx import LynxChain
from eth.db.atomic import AtomicDB

def test_freezer():
    
    node = Node(port=6969)

    peer: Peer = node.peers[0]

    Freezer.store_peer(peer)
        
    


if __name__ == '__main__':
    test_freezer()