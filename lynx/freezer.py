from pathlib import Path
import sys
from typing import (
    Sequence,
    Union,
    Any,
    Tuple,
    List
)
from enum import Enum
from lynx.p2p.peer import Peer
from eth.vm.forks.lynx.blocks import LynxBlockHeader, LynxBlock
from eth.vm.forks.lynx.transactions import LynxTransaction
from eth_typing import BlockNumber
from eth_utils import encode_hex
import rlp
import json
import snappy
from eth.abc import (
    SignedTransactionAPI,
    ReceiptAPI,
    ChainDatabaseAPI,
)
from lynx.constants import (
    MAX_DATA_FILE_SIZE,
    FILE_NUM_BYTES,
    OFFSET_BYTES,
    INDEX_ROW_SIZE,
)

class StorageType(Enum):
    """Enum for the different types of storage within the client's freezer"""

    HEADERS = 'headers'
    TRANSACTIONS = 'transactions'
    RECEIPTS = 'receipts'

    def validate_storage_type(self, data: Any) -> bool:
        if self is StorageType.HEADERS:
            return isinstance(data, LynxBlockHeader)
        if self is StorageType.TRANSACTIONS:
            return isinstance(data, tuple) and all(isinstance(tx, SignedTransactionAPI) for tx in data)
        if self is StorageType.RECEIPTS:
            return isinstance(data, tuple) and all(isinstance(receipt, ReceiptAPI) for receipt in data)
        return False


class Freezer:

    @classmethod
    def create_freezer(cls) -> None:
        cls.__create_freezer_dir()
        cls.__create_peers_dir()
        cls.__create_chain_dir()
        cls.__create_index_dir()
        cls.__create_data_dir()
        cls.__create_header_data_dir()
        cls.__create_transactions_data_dir()
        cls.__create_receipts_data_dir()


    @classmethod
    def freezer_exists(cls) -> bool:
        current_working_directory = Path.cwd()
        return (current_working_directory / 'freezer').exists()


    @classmethod
    def __create_freezer_dir(cls) -> None:
        current_working_directory = Path.cwd()
        Path(current_working_directory / 'freezer').mkdir(exist_ok=True)


    @classmethod
    def chain_dir_exists(cls) -> bool:
        current_working_directory = Path.cwd()
        return (current_working_directory / 'freezer' / 'chain').exists()


    @classmethod
    def __create_chain_dir(cls) -> None:
        current_working_directory = Path.cwd()
        Path(current_working_directory / 'freezer' / 'chain').mkdir(exist_ok=True)

    @classmethod
    def peers_dir_exists(cls) -> bool:
        current_working_directory = Path.cwd()
        return (current_working_directory / 'freezer' / 'peers').exists()


    @classmethod
    def __create_peers_dir(cls) -> None:
        current_working_directory = Path.cwd()
        Path(current_working_directory / 'freezer' / 'peers').mkdir(exist_ok=True)


    @classmethod
    def chain_index_dir_exists(cls) -> bool:
        current_working_directory = Path.cwd()
        return (current_working_directory / 'freezer' / 'chain' / 'indexes').exists()


    @classmethod
    def __create_index_dir(cls) -> None:
        current_working_directory = Path.cwd()
        Path(current_working_directory / 'freezer' / 'chain' / 'indexes').mkdir(exist_ok=True)


    @classmethod
    def chain_data_dir_exists(cls) -> bool:
        current_working_directory = Path.cwd()
        return (current_working_directory / 'freezer' / 'chain' / 'data').exists()

    @classmethod
    def peers_data_dir_exists(cls) -> bool:
        current_working_directory = Path.cwd()
        return (current_working_directory / 'freezer' / 'peers' / 'data').exists()


    @classmethod
    def __create_data_dir(cls) -> None:
        current_working_directory = Path.cwd()
        Path(current_working_directory / 'freezer' / 'chain' / 'data').mkdir(exist_ok=True)
        Path(current_working_directory / 'freezer' / 'peers' / 'data').mkdir(exist_ok=True)


    @classmethod
    def data_type_dir_exists(cls, data_type: StorageType) -> bool:
        current_working_directory = Path.cwd()
        return Path(current_working_directory / 'freezer' / 'chain' / 'data' / data_type.value).exists()

    @classmethod
    def __create_data_type_dir(cls, data_type: StorageType) -> None:
        current_working_directory = Path.cwd()
        Path(current_working_directory / 'freezer' / 'chain' / 'data' / data_type.value).mkdir(exist_ok=True)


    @classmethod
    def __create_header_data_dir(cls) -> None:
        return cls.__create_data_type_dir(data_type=StorageType.HEADERS)
    

    @classmethod
    def __create_transactions_data_dir(cls) -> None:
        return cls.__create_data_type_dir(data_type=StorageType.TRANSACTIONS)

    
    @classmethod
    def __create_receipts_data_dir(cls) -> None:
        return cls.__create_data_type_dir(data_type=StorageType.RECEIPTS)
    

    @classmethod 
    def header_index_exists(cls) -> bool:
        current_working_directory = Path.cwd()
        return (current_working_directory / 'freezer' / 'chain' / 'indexes' / 'headers.cidx').exists()


    @classmethod
    def __store_chain_data(cls, data_type: StorageType, data: Union[LynxBlockHeader, Tuple[SignedTransactionAPI], Tuple[ReceiptAPI]]) -> Tuple[int, int]:
        """Adds the given header to the header data directory and returns 
        the a tuple with the file number and the offset of the data
        
        TODO Generalize this function to handle bodies, receipts, etc.
        """
        
        if not cls.data_type_dir_exists(data_type):
            cls.create_freezer()

        if not data_type.validate_storage_type(data):
            raise ValueError("Invalid data type")

        data_rlp = rlp.encode(data)
        compressed = snappy.compress(data_rlp)
        data_size = sys.getsizeof(compressed)

        current_working_directory = Path.cwd()
        data_directory = Path(current_working_directory / 'freezer' / 'chain' / 'data' / data_type.value)
        files = list(data_directory.glob(f'{data_type.value}.*.cdat'))
        file_num = len(files)

        if file_num == 0 or (Path(max(files)).stat().st_size + data_size) > MAX_DATA_FILE_SIZE:
            file_num += 1
            file_name = f'{data_type.value}.{str(file_num).zfill(4)}.cdat'
            file_path = Path(current_working_directory / 'freezer' / 'chain' / 'data' / data_type.value / file_name)
            file_mode = 'wb'
        else:
            file_path = Path(max(files))
            file_mode = 'ab'

        with open(file_path, file_mode) as file:
            offset = file.tell() if file_mode == 'ab' else 0
            file.write(compressed)
            file.close()

        return file_num, offset


    @classmethod
    def __store_chain_index(cls, data_type: StorageType, file_num: int, offset: int) -> None:
        """Maps the given header to the file and offset where the data can be found
        
        TODO Generalize this function to handle bodies, receipts, etc.
        """
        
        if not cls.chain_index_dir_exists():
            cls.create_freezer()

        current_working_directory = Path.cwd()
        file_path = Path(current_working_directory / 'freezer' / 'chain' / 'indexes' / f'{data_type.value}.cidx')

        file_num_bytes = file_num.to_bytes(2, byteorder='big')
        offset_bytes = offset.to_bytes(4, byteorder='big')
        header_index = file_num_bytes + offset_bytes

        file_mode = 'ab' if file_path.exists() else 'wb'
        with open(file_path, file_mode) as file:
                file.write(header_index)
                file.close()

    
    @classmethod
    def __store_header(cls, header: LynxBlockHeader) -> None:
        """Adds the given header to the header data directory and returns 
        the a tuple with the file number and the offset of the data
        """
        file_num, offset = cls.__store_chain_data(StorageType.HEADERS, header)
        cls.__store_chain_index(StorageType.HEADERS, file_num, offset)


    @classmethod
    def __store_transactions(cls, transactions: Tuple[SignedTransactionAPI]) -> None:
        """Adds the given header to the header data directory and returns 
        the a tuple with the file number and the offset of the data
        """
        file_num, offset = cls.__store_chain_data(StorageType.TRANSACTIONS, transactions)
        cls.__store_chain_index(StorageType.TRANSACTIONS, file_num, offset)

    
    @classmethod
    def __store_receipts(cls, receipts: Tuple[ReceiptAPI]) -> None:
        """Adds the given header to the header data directory and returns 
        the a tuple with the file number and the offset of the data
        """
        file_num, offset = cls.__store_chain_data(StorageType.RECEIPTS, receipts)
        cls.__store_chain_index(StorageType.RECEIPTS, file_num, offset)


    @classmethod
    def store_block(cls, block: LynxBlock, chaindb: ChainDatabaseAPI) -> None:
        """Adds the given block to the freezer"""
        if not cls.freezer_exists():
            cls.create_freezer()

        header = block.header
        transactions = block.transactions
        receipts = block.get_receipts(chaindb)

        cls.__store_header(header)
        cls.__store_transactions(transactions)
        cls.__store_receipts(receipts)


    @classmethod
    def read_chain_index_file(cls, data_type: StorageType, offset: int) -> Tuple[int, int, int]:
        """Reads the index file of the given data type (headers, transactions, receipts) at the 
        given offset and returns the file number, offset, and the next block's offset. 
        if the next block does not exist or is in another file next_block_offset will be None. 
        This function is used by read_header_data_file().
        
        returns (file_num, offset, next_block_offset)
        """

        current_working_directory = Path.cwd()
        file_path = Path(current_working_directory / 'freezer' / 'chain' / 'indexes' / f'{data_type.value}.cidx')
        with open(file_path, 'rb') as file:
            file_length = len(file.read())
            if offset + INDEX_ROW_SIZE > file_length:
                raise IndexError('Block offset is out of range')

            file.seek(offset)
            file_num_bytes = file.read(FILE_NUM_BYTES)
            offset_bytes = file.read(OFFSET_BYTES)

            if offset + (INDEX_ROW_SIZE * 2) > file_length:
                next_block_offset = None
            else:
                file.seek(offset + (INDEX_ROW_SIZE) + FILE_NUM_BYTES)
                next_block_offset_bytes = file.read(OFFSET_BYTES)
                next_block_offset = int.from_bytes(next_block_offset_bytes, byteorder='big')
            file.close()

        file_num = int.from_bytes(file_num_bytes, byteorder='big')
        offset = int.from_bytes(offset_bytes, byteorder='big')
        return file_num, offset, next_block_offset


    @classmethod
    def read_chain_data_file(cls, data_type: StorageType, file_num: int, start: int, end: int = None) -> Union[LynxBlockHeader, Tuple[SignedTransactionAPI], Tuple[ReceiptAPI]]:
        """Reads the header data file from the given start index to the end index 
        and returns a BlockHeaderAPI, tuple[SignedTransactionAPI], or a tuple[ReceiptAPI] object.
        depending on the data type.
        
        TODO Generalize this function to handle receipts
        """

        current_working_directory = Path.cwd()
        file_path = Path(current_working_directory / 'freezer' / 'chain' / 'data' / f'{data_type.value}' / f'{data_type.value}.{str(file_num).zfill(4)}.cdat')
        with open(file_path, 'rb') as file:
            data_range = None if end is None else end - start 
            file.seek(start)
            compressed = file.read(data_range)
            file.close()

        data_rlp = snappy.decompress(compressed)
        data_bytes = rlp.decode(data_rlp)

        if data_type is StorageType.HEADERS:
            return LynxBlockHeader.deserialize(data_bytes)
        if data_type is StorageType.TRANSACTIONS:
            return [LynxTransaction.deserialize(tx) for tx in data_bytes]
        # if data_type is StorageType.RECEIPTS:
        #     return [LondonReceipt.deserialize(tx) for tx in bytes]
        return None


    @classmethod
    def get_block_header_by_number(cls, block_number: BlockNumber) -> LynxBlockHeader:
        
        index_file_offset = block_number * INDEX_ROW_SIZE

        file_num, offset, next_block_offset = cls.read_chain_index_file(StorageType.HEADERS, index_file_offset)
        header = cls.read_chain_data_file(StorageType.HEADERS, file_num, offset, next_block_offset)
        return header


    @classmethod
    def get_block_transactions_by_number(cls, block_number: BlockNumber) -> Sequence[SignedTransactionAPI]:
        
        index_file_offset = block_number * INDEX_ROW_SIZE

        file_num, offset, next_block_offset = cls.read_chain_index_file(StorageType.TRANSACTIONS, index_file_offset)
        transactions = cls.read_chain_data_file(StorageType.TRANSACTIONS, file_num, offset, next_block_offset)
        return transactions
    

    @classmethod
    def get_block_by_number(cls, block_number: BlockNumber) -> LynxBlockHeader:
        
        header = cls.get_block_header_by_number(block_number)
        transactions = cls.get_block_transactions_by_number(block_number)
        return LynxBlock(header, transactions)


    @classmethod
    def __store_peer_data(cls, peer: Peer) -> int:

        if not isinstance(peer, Peer):
            raise ValueError("Invalid data type")

        data = peer.as_dict()
        data_size = sys.getsizeof(data)

        current_working_directory = Path.cwd()
        data_directory = Path(current_working_directory / 'freezer' / 'peers' / 'data')
        files = list(data_directory.glob('peers.*.json'))
        file_num = len(files)

        if file_num == 0 or (Path(max(files)).stat().st_size + data_size) > MAX_DATA_FILE_SIZE:
            file_num += 1
            file_name = f'peers.{str(file_num).zfill(4)}.json'
            file_path = Path(current_working_directory / 'freezer' / 'peers' / 'data' / file_name)
            file_size = 0
            file_mode = 'w+'
        else:
            file_path = Path(max(files))
            file_size = file_path.stat().st_size
            file_mode = 'r+'

        with open(file_path, file_mode) as file:
            if file_size > 0:
                #TODO: Handle if file is corrupted
                file_contents = json.load(file)
                file_contents[peer.address] = data
                file_contents = json.dumps(file_contents)
                file.seek(0)
                file.truncate(0)
            else:
                file_contents = json.dumps({peer.address:data})
            file.write(file_contents)
            file.close()

        return file_num


    @classmethod
    def store_peer(cls, peer: Peer) -> None:
        """Adds the given peer to the freezer"""

        if not cls.freezer_exists():
            cls.create_freezer()

        cls.__store_peer_data(peer)


    @classmethod
    def get_peers(cls, max_peers: int = 25) -> Tuple[Peer]:
        """"""

        if not cls.freezer_exists():
            cls.create_freezer()
            return ()
        
        current_working_directory = Path.cwd()
        data_directory = Path(current_working_directory / 'freezer' / 'peers' / 'data')
        files = list(data_directory.glob('peers.*.json'))

        peers : List[Peer] = []

        for f in files:
            file_path = Path(f)
            with open(file_path, 'r') as file:
                file_contents = json.load(file)
                for key, value in file_contents.items():
                    if len(peers) < max_peers:
                        peer : Peer = Peer(address=value['address'], port=value['port'])
                        peers.append(peer)

        return tuple(peers)
