
from node import Node
from account import Account
from message import Message


def hello(peer_connection, message_data):
    print(message_data)


def main():
    message = Message()
    message.validate()


if __name__ == "__main__":
    main()
