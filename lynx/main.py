
from node import Node
from account import Account


def hello(peer_connection, message_data):
    print(message_data)


def main():
    account = Account()
    message = 'Hello there!'
    signature = account.sign_message(message)
    is_message_valid = account.verify_signature(
        message=message, sender_public_key=account.public_key, signature=signature)


if __name__ == "__main__":
    main()
