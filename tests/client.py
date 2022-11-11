from lynx.p2p.node import Node
from lynx.p2p.message import Message, MessageFlag
from lynx.p2p.peer import Peer
from lynx.constants import *
from eth.vm.forks.lynx.blocks import LynxBlock
from eth.chains.lynx import LynxChain, LYNX_VM_CONFIGURATION
from eth.db.atomic import AtomicDB
from eth_typing import Address
from eth_keys import keys
import time
import threading


def test_client():
    node = Node(port='6969', peers=BOOTSTRAP_PEERS, listen_on_start=False)


if __name__ == "__main__":
    thread = threading.Thread(target=test_client, name='TEST CLIENT THREAD')
    thread.start()
 