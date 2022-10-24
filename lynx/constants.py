from lynx.p2p.peer import Peer
from eth_typing import Address

PROTOCOL_VERSION = '10001'
NODE_SERVICES = ['NODE_NETWORK']
SUB_VERSION = '/LynxCore:0.0.0.1/'

# Freezer
MAX_DATA_FILE_SIZE = 2 * (10**9) # 2 gigabytes
FILE_NUM_BYTES = 2 
OFFSET_BYTES = 4 
INDEX_ROW_SIZE =  FILE_NUM_BYTES + OFFSET_BYTES # 6 bytes

# Node
DEFAULT_PORT = '6969' # LMAO
DEFAULT_MAX_PEERS = 12

# Server
EXTERNAL_IP_HOSTS = ['https://checkip.amazonaws.com', 'https://api.ipify.org', 'http://myip.dnsomatic.com']

# Registry
REGISTRY_CONTRACT_ADDRESS = Address(bytes.fromhex('6969696969696969696969696969696969696969'))

# Bootstrapping
BOOTSTRAP_PEERS = [Peer(address='427.6.0.42', port='1234'), Peer(address='168.72.0.31', port='4321'), Peer(address='127.0.0.1', port='6968')]