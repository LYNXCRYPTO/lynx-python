# node.py

from account import Account
from server import Server
from peer import Peer
from peer_connection import PeerConnection
from message import Message, SignedMessage
from utilities import Utilities
import uuid
from constants import *
from hashlib import sha3_256
import threading
import time
import traceback


def display_debug(msg):
    """Prints a message to the screen with the name of the current thread"""
    print("[%s] %s" % (str(threading.currentThread().getName()), msg))


class Node:
    """Implements the core functionality of a node on the Lynx network."""

    # ------------------------------------------------------------------------------
    def __init__(self, server_port=6969, server_host=None, max_peers=12) -> None:
        # --------------------------------------------------------------------------
        """Initializes a node with the ability to receive requests, store information, and
        handle responses.
        """
        self.debug = 1

        self.max_peers = int(max_peers)
        self.nonce = uuid.uuid4().hex + uuid.uuid1().hex

        self.server = Server(host=server_host,
                             port=server_port, max_peers=max_peers, nonce=self.nonce)

        if not Peer.is_peers_file_valid():
            Peer.init_peers_file()

        Utilities.init_transactions()

        # heartbeat_thread = threading.Thread(
        #     target=self.__init_heartbeat, name='Heartbeat Thread')
        # heartbeat_thread.start()

        self.router = None

    # ------------------------------------------------------------------------------
    def send_known_peers_request(self):
        # --------------------------------------------------------------------------
        """"""

        bootstrap_nodes = {
            '1234': ('127.0.0.1', '6969'), }

        for node in bootstrap_nodes:
            if self.node_id != node:
                try:
                    peers_needed = self.max_peers - len(self.server.peers)
                    payload = {'peer_request_count': peers_needed}
                    bootstrap_node_thread = threading.Thread(target=self.server.connect_and_send, args=[
                                                             bootstrap_nodes[node][0], bootstrap_nodes[node][1], 'request', 2, payload, node], name='Bootstrap Connection Thread (%s)' % node)
                    bootstrap_node_thread.start()
                except:
                    self.__debug(
                        'Failed to connect to bootstrap node (node_id: %s).' % node)

    # ------------------------------------------------------------------------------
    def send_transaction_count_request(self):
        # --------------------------------------------------------------------------
        """"""

        self.__debug('Self.peers: %s' % self.server.peers)
        for peer in self.server.peers:
            try:
                transaction_download_thread = threading.Thread(target=self.server.connect_and_send, args=[
                                                               self.server.peers[peer][0], self.server.peers[peer][1], 'request', 3, 'Transaction Count Request', peer], name='Initial Transaction Download Thread (%s)' % peer)
                transaction_download_thread.start()
                print('Transaction download started!')
            except:
                self.__debug('Failed to request initial transaction download.')

    # ------------------------------------------------------------------------------
    def set_id(self, id) -> None:
        # --------------------------------------------------------------------------
        self.node_id = id

    # ------------------------------------------------------------------------------
    def start_stabilizer(self, stabilizer, delay) -> None:
        # --------------------------------------------------------------------------
        """Registers and starts a stabilizer function with this peer. The function
        The function will be activated every <delay> seconds.
        """

        stabilizer_thread = threading.Thread(
            target=self.__run_stabilizer, args=[stabilizer, delay])
        stabilizer_thread.start()

    # ------------------------------------------------------------------------------
    def add_router(self, router) -> None:
        # --------------------------------------------------------------------------
        """Registers a routing function with this peer. The setup of routing is as
        follows: This peer maintains a list of other know peers (in self.peers). The
        routing function should take the name of a peer (which may not necessarily
        be present in self.peers) and decide which of the known peers a message should
        be routed to next in order to (hopefully) reach the desired peer. The router 
        function should return a tuple of three values: (next_peer_id, host, and port).
        If the message cannot be routed, the next_peer_id should be None.
        """

        self.router = router

    # ------------------------------------------------------------------------------
    def send_to_peer(self, peer_id, message_type, message_data, wait_for_reply=True) -> list[tuple[str, str]]:
        # --------------------------------------------------------------------------
        """Send a message to the identified peer. In order to decide how to send
        the message, the router handler for this peer will be called. If no router
        function has been registered, it will not work. The router function should 
        provide the next immediate peer to whom the message should be forwarded. 
        The peer's reply, if it is expected, will be returned.

        Returns None if the message could not be routed.
        """

        if self.router:
            next_peer_id, host, port = self.router(peer_id)
        if not self.router or not next_peer_id:
            self.__debug('Unable to route %s to %s' % (message_type, peer_id))
            return None

        return self.server.connect_and_send(host, port, message_type, message_data, peer_id=next_peer_id)

    # ------------------------------------------------------------------------------
    def init_heartbeat(self) -> None:
        # --------------------------------------------------------------------------
        """Attempts to ping all currently know peers in order to ensure that they
        are still active. Removes any from the peer list that do not reply. This 
        function can be used as a simpler stabilizer.
        """

        while True:
            self.send_heartbeat_request()

            time.sleep(30)

    # ------------------------------------------------------------------------------
    def __debug(self, message) -> None:
        # --------------------------------------------------------------------------
        if self.debug:
            display_debug(message)

# end Node class
