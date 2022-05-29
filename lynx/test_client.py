from node import Node
from account import Account
from message import Message
import threading
import time


def test_client():
    node = Node(server_port='6968')
    version_request_thread = threading.Thread(
        target=node.server.send_version_request, args=['127.0.0.1', '6969'], name='Version Request Thread')
    version_request_thread.start()


if __name__ == "__main__":
    test_client()
