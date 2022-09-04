from eth.vm.forks.lynx.transactions import LynxTransaction


class Mempool:

    def __init__(self, tx_expire_time: int = 300) -> None:
        self.transactions = []
        self__transaction_indexes = {}
        self.tx_expire_time = tx_expire_time

    def add_transaction(self, transaction: LynxTransaction) -> None:
        self.transactions.append(transaction)

    def remove_transaction(self, tx_hash: str) -> None:
        
