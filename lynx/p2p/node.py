# node.py
import uuid
import threading
import time
from typing import Any
from lynx.p2p.server import Server
from lynx.p2p.peer import Peer
from lynx.p2p.peer_connection import PeerConnection
from lynx.p2p.request import Request
from lynx.p2p.response import Response
from lynx.p2p.message import Message, MessageType, MessageFlag
from lynx.p2p.mempool import Mempool
from lynx.constants import *
from eth.chains.lynx import LynxChain, LYNX_VM_CONFIGURATION
from eth.db.atomic import AtomicDB
from eth.vm.forks.lynx.transactions import LynxTransaction


class Node:
    """Implements the core functionality of a node on the Lynx network."""

    def __init__(self, host=None, port=6969, max_peers : int =12) -> None:
        """Initializes a node with the ability to receive requests, store information, and
        handle responses.
        """

        print('\nConfiguring Node...')
        # TODO: Make nonce the SHA256 of host
        self.nonce = uuid.uuid4().hex + uuid.uuid1().hex
        print('Initializing Peer Storage...')
        self.max_peers = int(max_peers)
        self.peers = [Peer(address='127.0.0.1', port='6968')]
        self.peer_lock = threading.Lock()

        print('Initializing Mempool...')
        self.mempool = Mempool()
        self.mempool_lock = threading.Lock()

        print('Configuring Lynx Virtual Machine...')
        print('Initializing Blockchain...')
        self.blockchain : LynxChain = self.__initialize_blockchain()

        print('\nConfiguring Server...')
        self.server = Server(self, host=host, port=port)


    def __initialize_blockchain(self) -> LynxChain:
        """Initializes the blockchain."""
    
        blockchain_config = LynxChain.configure(__name__='LynxChain', vm_configuration=LYNX_VM_CONFIGURATION)   
        
        return blockchain_config.from_genesis(AtomicDB(), {"timestamp": 0}) # pylint: disable=no-member
        

    def connect(self, peer: Peer) -> PeerConnection:
        """Connects to the specified peer and returns the corresponding socket."""

        peer_connection = PeerConnection(host=peer.address, port=peer.port)

        return peer_connection

    
    def send(self, peer_connection: PeerConnection, message_type: str, message_flag: int, message_data, retry: bool = True) -> list:
        """Sends a message to the specified peer connection."""

        message_replies = []

        try:
            start_time = time.time()
            peer_connection.send_data(message_type, message_flag, message_data)

            if message_type is MessageType.REQUEST:
                host, port = peer_connection.socket.getpeername()
                print(f'Attempting to receive a response from ({host}:{port})...')
                reply : Message = peer_connection.receive_data()

                while reply is not None:
                    message_replies.append(reply)
                    print('Received a reply!')
                    reply = peer_connection.receive_data()

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

            peer_connection.close()

        except Exception as e:
            print(e)
            if retry:
                print('Retrying...')

        if not message_replies and retry:
            return self.send(peer_connection, message_type, message_flag, message_data, retry=False)
            
        return message_replies


    def broadcast(self, flag: MessageFlag, payload: Any = None):
        """Broadcasts a message to all known peers."""
        print("HELLO")
        for peer in self.peers:
            if flag is MessageFlag.HEARTBEAT:
                thread = threading.Thread(target=self.send_heartbeat, args=[peer], name=f'Heartbeat Thread ({peer.address})')
            elif flag is MessageFlag.VERSION:
                thread = threading.Thread(target=self.send_version, args=[peer], name=f'Version Thread ({peer.address})')
            elif flag is MessageFlag.TRANSACTION:
                thread = threading.Thread(target=self.send_transaction, args=[peer, payload], name=f'Transaction Thread ({peer.address})')
            thread.start()


    def send_heartbeat(self, peer: Peer):
        """"""

        payload = 'PING'

        peer_connection = self.connect(peer)
        self.send(peer_connection, MessageType.REQUEST, MessageFlag.HEARTBEAT, payload)
        print('Heartbeat request sent!')

    
    def send_version(self, peer: Peer):
        """"""

        payload = {"version": PROTOCOL_VERSION, "address": self.server.host, "port": self.server.port}

        peer_connection = self.connect(peer)
        self.send(peer_connection, MessageType.REQUEST, MessageFlag.VERSION, payload)
        print('Version request sent!')


    def send_transaction(self, peer: Peer, tx: LynxTransaction):
        """"""

        transaction = tx.as_dict()
        transaction['to'] = transaction['to'].hex()
        transaction['data'] = transaction['data'].hex()
        payload = transaction

        peer_connection =self.connect(peer)
        self.send(peer_connection, MessageType.REQUEST, MessageFlag.TRANSACTION, payload)
        print('Transaction sent!')



    def add_peer(self, peer: Peer) -> bool:
        """Adds a peer to the known list of peers."""

        if not self.max_peers_reached() and peer not in self.peers:
            self.peer_lock.acquire()
            self.peers.append(peer)
            self.peer_lock.release()
            return True

        return False


    def get_peer(self, address: str, port: str) -> Peer:
        """Returns the (host, port) tuple for the given peer name."""

        for peer in self.peers:
            if peer.address == address and peer.port == port:
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


    def get_peer_at(self, index) -> tuple:

        if index not in self.peers:
            return None
        return self.peers[index]

    # # ------------------------------------------------------------------------------
    # def remove_peer_at(self, index) -> None:
    #     # --------------------------------------------------------------------------

    #     self.remove_peer(self, self.peers[index])


    def number_of_peers(self) -> int:
        """Return the number of known peer's."""

        return len(self.peers)


    def max_peers_reached(self) -> bool:
        """Returns whether the maximum limit of names has been added to the list of
        known peers. Always returns True if max_peers is set to 0
        """

        assert(self.max_peers == 0 or len(self.peers) <= self.max_peers)
        return len(self.peers) == self.max_peers


# end Node class
