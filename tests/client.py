from lynx.node import Node
from lynx.account import Account
from lynx.message import Message
from lynx.peer import Peer
from lynx.constants import *
import uuid
import threading
import time


def test_client():
    node = Node(server_port='6969')
    version_request_thread = threading.Thread(
        target=node.server.send_version_request, args=[Peer(version=PROTOCOL_VERSION,
                         services=NODE_SERVICES,
                         timestamp=str(time.time()),
                         nonce=uuid.uuid4().hex + uuid.uuid1().hex,
                         host='69.14.123.126',
                         port='6969',
                         sub_version=SUB_VERSION,
                         start_accounts_count=10,
                         relay=False,
                         )], name='Account Request Thread')
    version_request_thread.start()


if __name__ == "__main__":
    test_client()
