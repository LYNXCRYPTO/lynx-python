# from lynx.transaction import Transaction
from eth.vm.forks.arrow_glacier.transactions import ArrowGlacierLegacyTransaction
from eth.vm.forks.muir_glacier.transactions import MuirGlacierUnsignedTransaction
    

def test_transaction():
    tx = ArrowGlacierLegacyTransaction.create_unsigned_transaction(nonce=0, gas_price=1, gas=21000, to='0x1234567890123456789012345678901234567890'.encode(), value=1, data='Aliens are real!'.encode())
    print(tx.as_dict())
    # tx = ArrowGlacierLegacyTransaction.create_unsigned_transaction(nonce=0, gas_price=1, gas=21000, to='0x1234567890123456789012345678901234567890'.encode(), value=1, data='Aliens are real!'.encode())
    # tx = Transaction.create_unsigned_transaction(nonce=0, gas_price=1, gas=21000, to='0x1234567890123456789012345678901234567890'.encode(), value=1, data='Aliens are real!'.encode())
    # print(tx)
    # tx_encode = tx.encode()
    # tx_decode = tx.decode(tx_encode)
    # print(tx_decode)
    ...

if __name__ == "__main__":
    test_transaction()