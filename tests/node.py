from lynx.p2p.node import Node
from eth.vm.forks.lynx import LynxVM
from eth.vm.forks.lynx.computation import LynxComputation
from eth_utils import keccak
from lynx.p2p.peer import Peer

def test_node():
    node : Node = Node()
    # node.send_campaign(Peer())

if __name__ == "__main__":
    test_node()