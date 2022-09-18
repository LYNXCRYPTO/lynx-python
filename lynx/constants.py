from lynx.p2p.peer import Peer
from eth_typing import Address

PROTOCOL_VERSION = "10001"
NODE_SERVICES = ['NODE_NETWORK']
SUB_VERSION = '/LynxCore:0.0.0.1/'

ANY = 'any'
UINT256 = 'uint256'
BYTES = 'bytes'

UINT_256_MAX = 2**256 - 1
UINT_256_CEILING = 2**256
UINT_255_MAX = 2**255 - 1
UINT_255_CEILING = 2**255
UINT_255_NEGATIVE_ONE = -1 + UINT_256_CEILING
UINT_64_MAX = 2**64 - 1
NULL_BYTE = b'\x00'
EMPTY_WORD = NULL_BYTE * 32

UINT_160_CEILING = 2**160

# Freezer
MAX_DATA_FILE_SIZE = 2 * (10**9) # 2 gigabytes
FILE_NUM_BYTES = 2 
OFFSET_BYTES = 4 
INDEX_ROW_SIZE =  FILE_NUM_BYTES + OFFSET_BYTES # 6 bytes

# Node
DEFAULT_PORT = "6969"
DEFAULT_MAX_PEERS = 12

# Registry
REGISTRY_CONTRACT_ADDRESS = Address(bytes.fromhex('6969696969696969696969696969696969696969'))

# Bootstrapping
BOOTSTRAP_PEERS = [Peer(address="427.6.0.42", port="1234"), Peer(address="168.72.0.31", port="4321"), Peer(address="127.0.0.1", port="6968")]
# BOOTSTRAP_PEERS = [Peer(address="127.0.0.1", port="6968")]