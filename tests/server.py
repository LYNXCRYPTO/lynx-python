from lynx.node import Node
from lynx.account import Account
from lynx.message import Message
from lynx.utilities import Utilities
import threading


def test_server():
    node = Node()
    server_thread = threading.Thread(
        target=node.server.start_server_listen, args=[], name=('Server Thread'))
    server_thread.start()


if __name__ == "__main__":
    test_server()
