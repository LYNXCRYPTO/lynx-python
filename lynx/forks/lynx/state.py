from typing import Type

from eth.abc import TransactionExecutorAPI
from .computation import LynxComputation
from eth.vm.forks.arrow_glacier.state import ArrowGlacierState
from eth.vm.forks.berlin.state import BerlinState
from eth.vm.forks.arrow_glacier.state import ArrowGlacierTransactionExecutor
from eth.vm.forks.berlin.state import BerlinTransactionExecutor


class LynxTransactionExecutor(BerlinTransactionExecutor):
    pass


class LynxState(BerlinState):
    computation_class = LynxComputation
    transaction_executor_class: Type[TransactionExecutorAPI] = LynxTransactionExecutor