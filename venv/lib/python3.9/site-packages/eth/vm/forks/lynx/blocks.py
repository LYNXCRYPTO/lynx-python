from abc import ABC
from typing import (
    Type, 
    cast,
    List,
    Tuple,
    Sequence
)
from eth.abc import (
    BlockHeaderSedesAPI,
    TransactionBuilderAPI, 
    BlockHeaderAPI,
    MiningHeaderAPI,
    ChainDatabaseAPI,
    SignedTransactionAPI,
    ReceiptAPI,
    ReceiptBuilderAPI,
)
from eth.rlp.blocks import (
    BaseBlock,
)
from eth.vm.forks.london.transactions import LondonReceiptBuilder
from eth_bloom import (
    BloomFilter,
)
from eth_utils import (
    encode_hex,
)
from trie.exceptions import (
    MissingTrieNode,
)
from eth._utils.headers import (
    new_timestamp_from_parent,
)
from eth.exceptions import (
    BlockNotFound,
    HeaderNotFound,
)
from eth_hash.auto import keccak
import rlp
from rlp.sedes import (
    Binary,
    CountableList,
    big_endian_int,
    binary
)
from eth.rlp.sedes import (
    address,
    hash32,
    trie_root,
    uint256,
)
from eth.rlp.headers import (
    BlockHeader,
)
from eth_typing import (
    BlockNumber,
)
from eth_typing.evm import (
    Address,
    Hash32
)
from eth.constants import (
    ZERO_ADDRESS,
    ZERO_HASH32,
    EMPTY_UNCLE_HASH,
    GENESIS_NONCE,
    GENESIS_PARENT_HASH,
    BLANK_ROOT_HASH,
)
from eth.rlp.receipts import (
    Receipt,
)
from .transactions import LynxTransaction
from eth_utils import (
    humanize_hash,
)


class LynxBlockHeader(rlp.Serializable, BlockHeaderAPI):
    fields = [('parent_hash', hash32),
        ('coinbase', address),
        ('state_root', trie_root),
        ('transaction_root', trie_root),
        ('receipt_root', trie_root),
        ('bloom', uint256),
        ('block_number', big_endian_int),
        ('gas_used', big_endian_int),
        ('timestamp', big_endian_int),
        ('extra_data', binary),
        ('epoch', big_endian_int),
        ('slot', big_endian_int),
        ('epoch_block_number', big_endian_int),
        ('slot_size', big_endian_int),
        ('epoch_size', big_endian_int)]
    

    def __init__(self,
                 block_number: BlockNumber,
                 timestamp: int = None,
                 coinbase: Address = ZERO_ADDRESS,
                 parent_hash: Hash32 = ZERO_HASH32,
                 state_root: Hash32 = BLANK_ROOT_HASH,
                 transaction_root: Hash32 = BLANK_ROOT_HASH,
                 receipt_root: Hash32 = BLANK_ROOT_HASH,
                 epoch : int = 0,
                 slot : int = 0,
                 epoch_block_number : int = 0,
                 slot_size : int = 10,
                 epoch_size : int = 10,
                 bloom: int = 0,
                 gas_used: int = 0,
                 extra_data: bytes = b'',
                 ) -> None:
        if timestamp is None:
            if parent_hash == ZERO_HASH32:
                timestamp = new_timestamp_from_parent(None)
            else:
                # without access to the parent header, we cannot select a new timestamp correctly
                raise ValueError("Must set timestamp explicitly if this is not a genesis header")
        super().__init__(
            parent_hash=parent_hash,
            coinbase=coinbase,
            state_root=state_root,
            transaction_root=transaction_root,
            receipt_root=receipt_root,
            bloom=bloom,
            block_number=block_number,
            gas_used=gas_used,
            timestamp=timestamp,
            epoch=epoch,
            extra_data=extra_data,
            slot=slot,
            epoch_block_number=epoch_block_number,
            slot_size=slot_size,
            epoch_size=epoch_size,
        )

    def __str__(self) -> str:
        return f'<LynxBlockHeader #{self.block_number} {self.hash.hex()[2:10]}>'
    
    _hash = None

    @property
    def mining_hash(self) -> Hash32:
        return ZERO_HASH32

    @property
    def hash(self) -> Hash32:
        if self._hash is None:
            self._hash = keccak(rlp.encode(self))
        return cast(Hash32, self._hash)

    @property
    def hex_hash(self) -> str:
        return encode_hex(self.hash)

    @property
    def is_genesis(self) -> bool:
        # if removing the block_number == 0 test, consider the validation consequences.
        # validate_header stops trying to check the current header against a parent header.
        # Can someone trick us into following a high difficulty header with genesis parent hash?
        return self.parent_hash == GENESIS_PARENT_HASH and self.block_number == 0

    @property
    def base_fee_per_gas(self) -> int:
        raise AttributeError("Base fee per gas not available until London fork")
    
    
class LynxBackwardsHeader(BlockHeaderSedesAPI):
    """
    An rlp sedes class for block headers.

    It can serialize and deserialize *both* Lynx and pre-Lynx headers.
    """

    @classmethod
    def serialize(cls, obj: BlockHeaderAPI) -> List[bytes]:
        return obj.serialize(obj)

    @classmethod
    def deserialize(cls, encoded: List[bytes]) -> LynxBlockHeader:
        return LynxBlockHeader.deserialize(encoded)


class LynxBlock(BaseBlock):
    transaction_builder = LynxTransaction
    receipt_builder: Type[ReceiptBuilderAPI] = LondonReceiptBuilder
    fields = [
        ('header', LynxBlockHeader),
        ('transactions', CountableList(transaction_builder)),
    ]

    bloom_filter = None

    def __init__(self, header: BlockHeaderAPI, transactions: Sequence[SignedTransactionAPI] = None) -> None:
        if transactions is None:
            transactions = []

        self.bloom_filter = BloomFilter(header.bloom)

        super().__init__(
            header=header,
            transactions=transactions,
        )
        # TODO: should perform block validation at this point?

    #
    # Helpers
    #
    @property
    def number(self) -> BlockNumber:
        return self.header.block_number

    @property
    def hash(self) -> Hash32:
        return self.header.hash

    #
    # Transaction class for this block class
    #
    @classmethod
    def get_transaction_builder(cls) -> Type[TransactionBuilderAPI]:
        return cls.transaction_builder

    @classmethod
    def get_receipt_builder(cls) -> Type[ReceiptBuilderAPI]:
        return cls.receipt_builder

    #
    # Receipts API
    #
    def get_receipts(self, chaindb: ChainDatabaseAPI) -> Tuple[ReceiptAPI, ...]:
        return chaindb.get_receipts(self.header, self.get_receipt_builder())

    #
    # Header API
    #
    @classmethod
    def from_header(cls, header: BlockHeaderAPI, chaindb: ChainDatabaseAPI) -> "LynxBlock":
        """
        Returns the block denoted by the given block header.

        :raise eth.exceptions.BlockNotFound: if transactions or uncle headers are missing
        """

        try:
            transactions = chaindb.get_block_transactions(header, cls.get_transaction_builder())
        except MissingTrieNode as exc:
            raise BlockNotFound(f"Transactions not found in database for {header}: {exc}") from exc

        return cls(
            header=header,
            transactions=transactions,
        )