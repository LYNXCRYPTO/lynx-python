from node import Node
from account import Account
from message import Message
from utilities import Utilities
import threading


def main():
    account = Account()
    node = Node(account=account)
    server_thread = threading.Thread(
        target=node.start_server_listen, args=[], name=('Server Thread'))
    server_thread.start()


if __name__ == "__main__":
    main()
