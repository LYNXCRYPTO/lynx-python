from lynx.p2p.node import Node
from lynx.p2p.peer import Peer
from lynx.constants import BOOTSTRAP_PEERS
import threading


def test_server():
    node = Node(port="6968", bootstrap_on_start=False)
    # server_thread = threading.Thread(target=node.server.start_server_listen, name=('Server Thread'))
    # server_thread.start()


if __name__ == "__main__":
    test_server()
