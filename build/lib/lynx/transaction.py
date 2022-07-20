
from ctypes import addressof
from mimetypes import init
from random import gauss


class Transaction:
    """Object definition for a transaction. Transactions are defined
    as a transfer of balance from one Lynx account to another. Transactions
    include a hash, from address, to address, value (amount of LX being
    transferred), and the transaction fee."""

    def make_transaction(self, nonce, gas_price, gas, address, value, data, v, r, s):
        self.nonce = nonce,
        self.gas_price = gas_price
        self.gas = gas
        self.to = address
        self.value = value
        self.data = data
        self.v = v
        self.r = r
        self.s = s
