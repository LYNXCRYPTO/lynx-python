from lynx.wallet import Wallet
from lynx.message import Message

def test_wallet():
    test_message = Message(type='request', flag=1, data='Aliens are real!')

    wallet = Wallet()
    wallet.sign("hello")
    pass



if __name__ == "__main__":
    test_wallet()