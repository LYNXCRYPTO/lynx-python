from lynx.p2p.node import Node
from lynx.p2p.message import Message, MessageFlag
from lynx.p2p.peer import Peer
from lynx.constants import *
import uuid
import threading
import time


def test_client():
    node = Node(port='6969')
    version_request_thread = threading.Thread(target=node.broadcast, args=[MessageFlag.HEARTBEAT], name='Client Thread')
    version_request_thread.start()


if __name__ == "__main__":
    test_client()
