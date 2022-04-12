from node import Node
from account import Account
from message import Message
import threading
import time


def main():
    account = Account()
    node = Node(account=account, server_port='6968')
    bootstrap_thread = threading.Thread(
        target=node.connect_to_bootstrap_nodes, args=[], name=('Bootstrap Thread'))
    bootstrap_thread.start()


if __name__ == "__main__":
    main()
