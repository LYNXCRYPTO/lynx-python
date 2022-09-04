from lynx.p2p.node import Node
from lynx.p2p.message import Message
from lynx.utilities import Utilities
import threading


def test_server():
    node = Node(port=6968)
    server_thread = threading.Thread(target=node.server.start_server_listen, args=[], name=('Server Thread'))
    server_thread.start()


if __name__ == "__main__":
    test_server()
