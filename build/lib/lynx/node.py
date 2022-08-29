# node.py

from lynx.account import Account
from lynx.p2p.server import Server
from lynx.peer import Peer
from lynx.peer_connection import PeerConnection
from lynx.message import Message, SignedMessage
from lynx.utilities import Utilities
import uuid
from lynx.constants import *
import threading
import time
import traceback


def display_debug(msg):
    """Prints a message to the screen with the name of the current thread"""
    print(msg)


class Node:
    """Implements the core functionality of a node on the Lynx network."""


    def __init__(self, server_port=6969, server_host=None, max_peers=12) -> None:
        """Initializes a node with the ability to receive requests, store information, and
        handle responses.
        """
        self.debug = 1

        self.max_peers = int(max_peers)
        self.nonce = uuid.uuid4().hex + uuid.uuid1().hex

        self.__debug('\nConfiguring Node...')
        self.__debug('Configuring Known Peers File...')
        if not Peer.is_peers_file_valid():
            self.__debug('Initializing Known Peers File...')
            Peer.init_peers_file()

        self.__debug('Configuring Accounts Directory...')
        Utilities.init_accounts()

        self.__debug('\nConfiguring Server...')
        self.server = Server(host=server_host,
                             port=server_port, max_peers=max_peers, nonce=self.nonce)

        self.router = None


    def set_id(self, id) -> None:
        self.node_id = id
        

    def add_router(self, router) -> None:
        """Registers a routing function with this peer. The setup of routing is as
        follows: This peer maintains a list of other know peers (in self.peers). The
        routing function should take the name of a peer (which may not necessarily
        be present in self.peers) and decide which of the known peers a message should
        be routed to next in order to (hopefully) reach the desired peer. The router 
        function should return a tuple of three values: (next_peer_id, host, and port).
        If the message cannot be routed, the next_peer_id should be None.
        """

        self.router = router

    
    def __debug(self, message) -> None:
        if self.debug:
            display_debug(message)

# end Node class
