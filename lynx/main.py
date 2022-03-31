from node import Node
from account import Account
from message import Message


def main():
    account = Account()
    node = Node(account=account)
    node.connect_to_bootstrap_nodes()
    # node.start_server_listen()


if __name__ == "__main__":
    main()
