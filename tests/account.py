from eth_account import Account

def test_account():
    account : Account = Account.create()
    print(account.address)


if __name__ == "__main__":
    test_account()