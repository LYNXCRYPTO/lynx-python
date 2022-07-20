from eth.abc import ABC
from eth.rlp.transactions import BaseTransaction
# from eth.vm.forks.arrow_glacier.transactions import (
#     ArrowGlacierLegacyTransaction,
#     ArrowGlacierTransactionBuilder,
#     ArrowGlacierUnsignedLegacyTransaction
# )

# class Transaction(ArrowGlacierLegacyTransaction, ABC):
#     ...

# class UnsignedTransaction(ArrowGlacierUnsignedLegacyTransaction):
#     """Object definition for a transaction. Transactions are defined
#     as a transfer of balance from one Lynx account to another. Transactions
#     include a hash, from address, to address, value (amount of LX being
#     transferred), and the transaction fee."""

#     ...
#     # def __init__(self, nonce: int, gas_price: int, gas_limit: int, to: str, value: int, data: str):
#     #     self.nonce = hex(nonce)
#     #     self.gas_price = hex(gas_price)
#     #     self.gas_limit = hex(gas_limit)
#     #     self.to = to
#     #     self.value = hex(value)
#     #     self.data = data.encode().hex()

#     # @classmethod
#     # def decode(cls, encoded: bytes):
#     #     return rlp.decode(encoded, sedes=cls)

#     # def encode(self):
#     #     return rlp.encode(self)

#     # def __str__(self) -> str:
#     #     return f'Nonce: {self.nonce}\nGas Price: {self.gas_price}\nGas Limit: {self.gas_limit}\nTo: {self.to}\nValue: {self.value}\nData: {self.data}'

# class TransactionBuilder(ArrowGlacierTransactionBuilder):
#     legacy_signed = ArrowGlacierLegacyTransaction
#     legacy_unsigned = ArrowGlacierUnsignedLegacyTransaction
