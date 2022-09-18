from typing import (
    Type,
    Any,
)
from eth_bloom import BloomFilter
from eth.vm.forks.frontier.constants import MAX_REFUND_QUOTIENT
from eth.rlp.blocks import BaseBlock
from eth.vm.state import BaseState
from eth.vm.base import BlockHeader
from eth.vm.forks.frontier.headers import compute_frontier_difficulty
from eth.vm.forks.lynx.headers import (create_lynx_header_from_parent, configure_lynx_header)
from .state import LynxState
from .blocks import LynxBlock, LynxBlockHeader
from .validation import validate_lynx_transaction_against_header
from eth._utils.db import get_parent_header
from eth.db.trie import make_trie_root_and_nodes
from eth.vm.base import VM
from eth.abc import (
    BlockHeaderAPI,
    BlockAPI,
    BlockAndMetaWitness,
    ReceiptAPI,
    StateAPI,
    SignedTransactionAPI,
    ComputationAPI,
)
from eth.rlp.logs import Log
from eth.rlp.receipts import Receipt
from eth_utils import (
    ValidationError,
)
from eth.constants import (
    BLOCK_REWARD,
    UNCLE_DEPTH_PENALTY_FACTOR,
    ZERO_HASH32,
)
from eth.validation import (
    validate_length_lte,
)


def make_lynx_receipt(computation: ComputationAPI, new_cumulative_gas_used: int) -> ReceiptAPI:
    # Reusable for other forks
    # This skips setting the state root (set to 0 instead). The logic for making a state root
    # lives in the FrontierVM, so that state merkelization at each receipt is skipped at Byzantium+.

    logs = [
        Log(address, topics, data)
        for address, topics, data
        in computation.get_log_entries()
    ]

    receipt = Receipt(
        state_root=ZERO_HASH32,
        gas_used=new_cumulative_gas_used,
        logs=logs,
    )

    return receipt

class LynxVM(VM):
    # Fork Name
    fork = 'lynx'

    # Classes
    block_class: Type[BaseBlock] = LynxBlock
    _state_class: Type[BaseState] = LynxState

    # Methods
    create_header_from_parent = staticmethod(create_lynx_header_from_parent)
    configure_header = configure_lynx_header

    @classmethod
    def calculate_net_gas_refund(cls, consumed_gas: int, gross_refund: int) -> int:
        max_refund = consumed_gas // MAX_REFUND_QUOTIENT
        return min(max_refund, gross_refund)

    def add_receipt_to_header(self,
                              old_header: BlockHeaderAPI,
                              receipt: ReceiptAPI) -> BlockHeaderAPI:
        return old_header.copy(
            bloom=int(BloomFilter(old_header.bloom) | receipt.bloom),
            gas_used=receipt.gas_used,
            state_root=self.state.make_state_root(),
        )

    @classmethod
    def finalize_gas_used(cls,
                          transaction: SignedTransactionAPI,
                          computation: ComputationAPI) -> int:

        gas_remaining = computation.get_gas_remaining()
        consumed_gas = transaction.gas - gas_remaining

        gross_refund = computation.get_gas_refund()
        net_refund = cls.calculate_net_gas_refund(consumed_gas, gross_refund)

        return consumed_gas - net_refund

    @classmethod
    def make_receipt(
            cls,
            base_header: BlockHeaderAPI,
            transaction: SignedTransactionAPI,
            computation: ComputationAPI,
            state: StateAPI) -> ReceiptAPI:

        gas_used = base_header.gas_used + cls.finalize_gas_used(transaction, computation)

        receipt_without_state_root = make_lynx_receipt(computation, gas_used)

        return receipt_without_state_root.copy(state_root=state.make_state_root())

    # Finalization
    def _assign_block_rewards(self, block: LynxBlock) -> None:
        block_reward = self.get_block_reward()

        if block_reward != 0:
            self.state.delta_balance(block.header.coinbase, block_reward)
            self.logger.debug(
                "BLOCK REWARD: %s -> %s",
                block_reward,
                block.header.coinbase,
            )
        else:
            self.logger.debug("No block reward given to %s", block.header.coinbase)

    def pack_block(self, block: LynxBlock, *args: Any, **kwargs: Any) -> LynxBlock:

        provided_fields = set(kwargs.keys())
        known_fields = set(BlockHeader._meta.field_names)
        unknown_fields = provided_fields.difference(known_fields)

        if unknown_fields:
            raise AttributeError(
                f"Unable to set the field(s) {', '.join(known_fields)} "
                "on the `BlockHeader` class. "
                f"Received the following unexpected fields: {', '.join(unknown_fields)}."
            )

        header: LynxBlockHeader = block.header.copy(**kwargs)
        packed_block = block.copy(header=header)

        return packed_block

    # Validation
    def validate_block(self, block: BlockAPI) -> None:
        if not isinstance(block, self.get_block_class()):
            raise ValidationError(
                f"This vm ({self!r}) is not equipped to validate a block of type {block!r}"
            )

        if block.is_genesis:
            validate_length_lte(
                block.header.extra_data,
                self.extra_data_max_bytes,
                title="BlockHeader.extra_data"
            )
        else:
            parent_header = get_parent_header(block.header, self.chaindb)
            self.validate_header(block.header, parent_header)

        tx_root_hash, _ = make_trie_root_and_nodes(block.transactions)
        if tx_root_hash != block.header.transaction_root:
            raise ValidationError(
                f"Block's transaction_root ({block.header.transaction_root!r}) "
                f"does not match expected value: {tx_root_hash!r}"
            )

        if not self.chaindb.exists(block.header.state_root):
            raise ValidationError(
                "`state_root` was not found in the db.\n"
                f"- state_root: {block.header.state_root!r}"
            )

    # Forging
    def forge_block(self, block: LynxBlock, *args: Any, **kwargs: Any) -> BlockAndMetaWitness:
        packed_block = self.pack_block(block, *args, **kwargs)

        block_result = self.finalize_block(packed_block)

        # Perform validation
        self.validate_block(block_result.block)

        return block_result

    # Outdated Methods
    def mine_block(self, block: BlockAPI, *args: Any, **kwargs: Any) -> BlockAndMetaWitness:
        packed_block = self.pack_block(block, *args, **kwargs)

        block_result = self.finalize_block(packed_block)

        # Perform validation
        self.validate_block(block_result.block)

        return block_result

    compute_difficulty = staticmethod(compute_frontier_difficulty)
    validate_transaction_against_header = validate_lynx_transaction_against_header

    @staticmethod
    def get_block_reward() -> int:
        return BLOCK_REWARD

    @staticmethod
    def get_uncle_reward(block_number: int, uncle: BlockHeaderAPI) -> int:
        return 0

    @classmethod
    def get_nephew_reward(cls) -> int:
        return 0
    