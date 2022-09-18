from typing import List
import threading
import time
from eth.vm.forks.lynx.transactions import LynxTransaction


class Mempool:

    def __init__(self, tx_expire_time: int = 300) -> None:
        self.transactions : List[LynxTransaction] = []
        self.__transaction_indexes = {}
        self.tx_expire_time = tx_expire_time
        self.mempool_lock = threading.Lock()


    def add_transaction(self, transaction: LynxTransaction) -> None:
        self.mempool_lock.acquire()
        index: int = self.getTransactionCount()
        self.transactions.append(transaction)
        self.__transaction_indexes[transaction.hash] = (index, time.time())
        self.mempool_lock.release()


    def remove_transaction(self, tx_hash: str) -> None:
        try:
            self.mempool_lock.acquire()
            if self.getTransactionCount() == 1:
                self.transactions = []
                self.__transaction_indexes = {}
                
            else:
                index = self.__transaction_indexes[tx_hash][0]
                last_transaction : LynxTransaction = self.transactions.pop()
                last_transaction_timestamp = self.__transaction_indexes[last_transaction.hash][1]
                self.transactions[index] = last_transaction
                self.__transaction_indexes[last_transaction.hash] = (index, last_transaction_timestamp)
                del self.__transaction_indexes[tx_hash]
        except KeyError:
            print('Transaction not found in mempool...')
        finally:
            self.mempool_lock.release()


    def getTransactionCount(self) -> int:
        return len(self.transactions)

    
    def start_expiry_listener(self) -> None:
        
        while self.getTransactionCount() > 0:
            for transaction in self.transactions:
                timestamp = self.__transaction_indexes[transaction.hash][1]
                if time.time() - timestamp > self.tx_expire_time:
                    self.remove_transaction(transaction.hash)
            time.sleep(5)