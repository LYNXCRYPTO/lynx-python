from lynx.freezer import Freezer
from lynx.p2p.node import Node
from lynx.p2p.peer import Peer
from eth.vm.forks.lynx.blocks import LynxBlock
from eth.vm.forks.lynx import LynxVM
from eth.chains.lynx import LynxChain
from eth.db.atomic import AtomicDB

def test_freezer():
    
    node = Node(port=6969, peers=[Peer(address='127.0.0.1', port=6968)])

    peer: Peer = node.peers[0]

    Freezer.store_peer(peer)

    print(Freezer.get_peers())
        
    
if __name__ == '__main__':
    test_freezer()