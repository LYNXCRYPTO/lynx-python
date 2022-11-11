# node.py
import uuid
import threading
import multiprocess
from multiprocess import Queue
import time
import socket
from typing import Any, List
from lynx.consensus.epoch_context import EpochContext
from lynx.consensus.generator import Generator
from lynx.consensus.snowball import SnowballConsensus
from lynx.p2p.bootstrap import Bootstrap
from lynx.p2p.server import Server
from lynx.p2p.peer import Peer
from lynx.p2p.peer_connection import PeerConnection
from lynx.p2p.request import Request
from lynx.p2p.response import Response
from lynx.p2p.message import Message, MessageType, MessageFlag
from lynx.p2p.mempool import Mempool
from lynx.consensus.leader_schedule import LeaderSchedule
from lynx.consensus.vrf import VRF
from lynx.consensus.registry import Registry
from lynx.freezer import Freezer
from lynx.constants import REGISTRY_CONTRACT_ADDRESS, PROTOCOL_VERSION, DEFAULT_PORT, DEFAULT_MAX_PEERS
from eth.chains.lynx import LynxChain, LYNX_VM_CONFIGURATION
from eth.db.atomic import AtomicDB
from eth.vm.forks.lynx.transactions import LynxTransaction
from eth.vm.forks.lynx.blocks import LynxBlock, LynxBlockHeader
from eth_account import Account
from eth_typing import Address, BlockNumber
from eth_keys import keys

class Node:
    """Implements the core functionality of a node on the Lynx network."""

    def __init__(self, host: str = None, port: str = DEFAULT_PORT, peers: List[Peer] = [], max_peers: int = DEFAULT_MAX_PEERS, bootstrap_on_start : bool = True, listen_on_start : bool = True) -> None:
        """
        Initializes a node with the ability to receive requests, store information, and
        handle responses.
        """

        print('\nConfiguring Node...')
        # TODO: Make nonce the SHA256 of host
        self.nonce = uuid.uuid4().hex + uuid.uuid1().hex
        self.account : Account = Account.create()

        print('Initializing Peer Storage...')
        self.max_peers = int(max_peers)
        self.peers = peers
        # self.peer_lock = threading.Lock()

        self.server = Server(self, host=host, port=port)

        print('Configuring Lynx Virtual Machine...')
        print('Initializing Blockchain...')
        self.blockchain : LynxChain = self.__initialize_blockchain()

        print('Initializing Mempool...')
        self.mempool = Mempool()

        print('Initializing Leader Schedule...')
        self.leader_schedule = LeaderSchedule()

        print('Initializing Consensus Engine...')
        self.snowball = SnowballConsensus()
        
        if bootstrap_on_start:
            self.is_bootstrapping = True
            print('Configuring Bootstrap Process...')
            known_peers = Freezer.get_peers()
            if known_peers:
                Bootstrap.from_peers(self, known_peers)
                
            # if len(self.peers) < max_peers:
            #     Bootstrap.from_seeds(self)

        if listen_on_start:
            self.queue = multiprocess.Queue()
            self.blockchain.forge_block()
            # self.queue.put("SOMETHING")

            # if not self.is_bootstrapping:
            #     head : LynxBlockHeader = self.blockchain.get_canonical_head()
            #     epoch = EpochContext(start=(head.block_number - (head.epoch_block_number - 1)), slot=head.slot, size=head.epoch_size, slot_size=head.slot_size)
            #     self.generator = Generator(self, epoch)
            #     p1 = multiprocess.Process(target=self.generator.start_generator, args=(self.queue,), name='Generator Process')
            #     p1.start()
            
            self.server.start_server_listen(self.queue, self.leader_schedule)



    def __initialize_blockchain(self) -> LynxChain:
        """Initializes the blockchain."""

        SENDER_PRIVATE_KEY = keys.PrivateKey(bytes.fromhex('45a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d8'))
        SENDER_ADDRESS = Address(SENDER_PRIVATE_KEY.public_key.to_canonical_address())

        GENESIS_STATE = {
            SENDER_ADDRESS: {
                'balance': 69,
                'nonce': 0,
                'code': b'',
                'storage': {},
            },
            REGISTRY_CONTRACT_ADDRESS: {
                'balance': 69,
                'nonce': 0,
                'code': Registry.get_deployed_bytecode(),
                'storage': {},
            }
        }
    
        blockchain_config = LynxChain.configure(__name__='LynxChain', vm_configuration=LYNX_VM_CONFIGURATION)   
        
        return blockchain_config.from_genesis(AtomicDB(), {"timestamp": 0}, GENESIS_STATE)
        

    def connect(self, peer: Peer, socket_kind : socket.SocketKind = socket.SOCK_STREAM) -> PeerConnection:
        """Connects to the specified peer and returns the corresponding socket."""

        try:
            peer_connection = PeerConnection(host=peer.address, port=peer.port, socket_kind=socket_kind)

            return peer_connection
        
        except socket.gaierror as error:
            print(error)
            print(f'Unable to connect to {peer}, address is formatted incorrectly...')
            return None
        except OSError as error:
            print(f'Unable to connect to {peer}, network is unreachable...')
            return None

    
    def send(self, peer: Peer, peer_connection: PeerConnection, message_type: MessageType, message_flag: MessageFlag, message_data, retry: bool = True, wait_for_reply = True) -> list:
        """Sends a message to the specified peer connection."""

        message_replies = []

        try:
            start_time = time.time()

            peer_connection.send_data(message_type, message_flag, message_data)

            if wait_for_reply and message_type is MessageType.REQUEST:
                host, port = peer_connection.socket.getpeername()
                print(f'Attempting to receive a response from {peer}...')

                reply : Message = peer_connection.receive_data()
                while reply is not None:
                    message_replies.append(reply)
                    print(f'Received a reply from {peer}!')
                    reply = None # Temporary because line below stalled the program
                    # if peer_connection.is_open:
                    #     reply = peer_connection.receive_data()

                for i, r in enumerate(message_replies):
                    print(f'Reply #{i + 1} Contents:\n\tType: {r.type}\n\tFlag: {r.flag}\n\tData: {r.data}\n')
                    if r.type is MessageType.REQUEST:
                        Request(self, r, peer_connection)
                    elif r.type is MessageType.RESPONSE:
                        end_time = time.time()
                        response_time = end_time - start_time
                        Response(self, r, peer_connection, response_time)
                    else:
                        print(f'Unable to handle message type of "{r.type}"')

        except Exception as error:
            print(error)
        
        if retry and wait_for_reply and not message_replies:
            print('Retrying...')
            if peer_connection.is_closed():
                peer_connection : PeerConnection = self.connect(peer)

            if peer_connection is not None:
                return self.send(peer, peer_connection, message_type, message_flag, message_data, retry=False, wait_for_reply=wait_for_reply)
            else:
                print(f'Unable to reconnect to {peer}...')
        
        if peer_connection and peer_connection.is_open():
            peer_connection.close()

        return message_replies


    def broadcast(self, flag: MessageFlag, peers: List[Peer] = None, payload: Any = None) -> None:
        """Broadcasts a message to all known peers."""

        if peers is None:
            peers = self.peers.copy()

        for peer in peers:
            if flag is MessageFlag.HEARTBEAT:
                thread = threading.Thread(target=self.send_heartbeat, args=[peer], name=f'Heartbeat Thread ({peer.address})')
            elif flag is MessageFlag.VERSION:
                thread = threading.Thread(target=self.send_version, args=[peer], name=f'Version Thread ({peer.address})')
            elif flag is MessageFlag.TRANSACTION:
                thread = threading.Thread(target=self.send_transaction, args=[peer, payload], name=f'Transaction Thread ({peer.address})')
            elif flag is MessageFlag.ADDRESS:
                thread = threading.Thread(target=self.send_address_request, args=[peer], name=f'Address Thread ({peer.address})')
            elif flag is MessageFlag.BLOCK:
                thread = threading.Thread(target=self.send_block_request, args=[peer], name=f'Block Thread ({peer.address})')
            elif flag is MessageFlag.CAMPAIGN:
                thread = threading.Thread(target=self.send_campaign, args=[peer], name=f'Campaign Thread ({peer.address})')
            elif flag is MessageFlag.QUERY:
                thread = threading.Thread(target=self.send_query, args=[peer], name=f'Query Thread ({peer.address})')
            thread.start()


    def send_heartbeat(self, peer: Peer) -> None:
        """
        Sends a simple PING message to the specified peer. A PONG message should be expect
        in return. If not, the provided peer is considered offline.

        retry = True
        wait_for_reply = True
        """

        payload = 'PING'

        peer_connection : PeerConnection = self.connect(peer, socket_kind=socket.SOCK_DGRAM)
        if peer_connection is not None:
            self.send(peer, peer_connection, MessageType.REQUEST, MessageFlag.HEARTBEAT, payload)
            print('Heartbeat request sent!')

    
    def send_version(self, peer: Peer) -> None:
        """
        Sends a message containing information about the local machine's network preferences and
        software. This message is considered a "handshake" as it should be the introduction 
        message when connecting to new peers. In return, a peer may send a version message
        themselves if they would like to share information with you.

        retry = True
        wait_for_reply = True
        """
        
        payload = {"version": PROTOCOL_VERSION, "address": self.server.host, "port": self.server.port}

        peer_connection : PeerConnection = self.connect(peer)
        if peer_connection is not None:
            self.send(peer, peer_connection, MessageType.REQUEST, MessageFlag.VERSION, payload)
            print('Version request sent!')


    def send_transaction(self, peer: Peer, tx: LynxTransaction) -> None:
        """"""

        transaction = tx.as_dict()
        transaction['to'] = transaction['to'].hex()
        transaction['data'] = transaction['data'].hex()
        payload = transaction

        peer_connection : PeerConnection = self.connect(peer)
        if peer_connection is not None:
            self.send(peer, peer_connection, MessageType.REQUEST, MessageFlag.TRANSACTION, payload, wait_for_reply=False)
            print('Transaction sent!')

    
    def send_address_request(self, peer: Peer) -> None:
        """"""

        payload = {"address": self.server.host, "port": self.server.port}

        peer_connection : PeerConnection = self.connect(peer)
        if peer_connection is not None:
            self.send(peer, peer_connection, MessageType.REQUEST, MessageFlag.ADDRESS, payload)
            print('Address request sent!')


    def send_block_request(self, peer: Peer) -> None:
        """"""

        head : LynxBlockHeader = self.blockchain.get_canonical_head()
        
        payload = {"best_block": head.block_number}

        peer_connection : PeerConnection = self.connect(peer)
        if peer_connection is not None:
            self.send(peer, peer_connection, MessageType.REQUEST, MessageFlag.BLOCK, payload, wait_for_reply=True)
            print('Block sent!')
            


    def send_campaign(self, peer: Peer, block_number: int) -> None:
        """"""

        block_number, campaign = VRF.generate_random_number(block_number, self.account)

        payload = {block_number: {"address": self.account.address, "campaign": campaign}}

        peer_connection : PeerConnection = self.connect(peer)
        if peer_connection is not None:
            self.send(peer, peer_connection, MessageType.REQUEST, MessageFlag.CAMPAIGN, payload, wait_for_reply=False)
            print('Campaign sent!')

    
    def send_query(self, peer: Peer, block_number: BlockNumber) -> None:

        payload = {"block_number": block_number}

        peer_connection = self.connect(peer)
        if peer_connection is not None:
            self.send(peer, peer_connection, MessageType.REQUEST, MessageFlag.QUERY, payload)


    def add_peer(self, peer: Peer) -> bool:
        """
        Adds a peer to the known list of peers and stores the peer in the Freezer
        for long term storage.
        """

        if not self.max_peers_reached() and peer not in self.peers:
            # self.peer_lock.acquire()
            self.peers.append(peer)
            Freezer.store_peer(peer)
            # self.peer_lock.release()
            return True

        return False


    def get_peer(self, host: str, port: str) -> Peer:
        """
        Returns the Peer object for the given peer host and port.
        If no peer exists with the provided host and port, then
        None is returned.
        """

        for peer in self.peers:
            if peer.address == host and peer.port == port:
                return peer

        return None


    # def remove_peer(self, peer_id) -> None:
    #     """Removes peer information from the know list of peers."""

    #     if peer_id in self.peers:
    #         self.peer_lock.acquire()
    #         del self.peers[peer_id]
    #         self.peer_lock.release()


    # def insert_peer_at(self, index, peer_id, host, port) -> None:
    #     """Inserts a peer's information at a specific position in the list of peers.
    #     The functions insert_peer_at, get_peer_at, and remove_peer_at should not be
    #     used concurrently with add_peer, get_peer, and/or remove_peer.
    #     """

    #     self.peer_lock.acquire()
    #     self.peers[index] = (peer_id, host, int(port))
    #     self.peer_lock.release()


    # def get_peer_at(self, index) -> tuple:

    #     if index not in self.peers:
    #         return None

    #     return self.peers[index]

    # # ------------------------------------------------------------------------------
    # def remove_peer_at(self, index) -> None:
    #     # --------------------------------------------------------------------------

    #     self.remove_peer(self, self.peers[index])


    def number_of_peers(self) -> int:
        """
        Return the number of known peer's.
        """

        return len(self.peers)


    def max_peers_reached(self) -> bool:
        """
        Returns whether the maximum limit of peers has been added to the list of
        known peers. Always returns True if max_peers is set to 0
        """

        return len(self.peers) == self.max_peers
        


# end Node class
