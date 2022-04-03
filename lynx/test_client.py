from node import Node
from account import Account
from message import Message
import threading


def main():
    account = Account()
    node = Node(account=account, server_port='6968')
    server_thread = threading.Thread(
        target=node.start_server_listen, args=[], name=('Server Thread'))
    server_thread.start()
    client_thread = threading.Thread(
        target=node.connect_to_bootstrap_nodes, args=[], name=('Client Thread'))
    client_thread.start()


if __name__ == "__main__":
    main()
