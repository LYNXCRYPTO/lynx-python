from lynx.p2p.node import Node
from lynx.account import Account
from lynx.message import Message
from lynx.p2p.peer import Peer
from lynx.constants import *
import uuid
import threading
import time


def test_client():
    node = Node(port='6969')
    version_request_thread = threading.Thread(target=node.send_heartbeat_request, args=[], name='Client Thread')
    version_request_thread.start()


if __name__ == "__main__":
    test_client()
