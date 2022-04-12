# node.py

from account import Account
from server import Server
from peer_connection import PeerConnection
from message import Message, SignedMessage
from request import Request
from response import Response
from utilities import Utilities
from hashlib import sha3_256
from os.path import exists
import json
import socket
import threading
import time
import traceback


def display_debug(msg):
    """Prints a message to the screen with the name of the current thread"""
    print("[%s] %s" % (str(threading.currentThread().getName()), msg))


class Node:
    """Implements the core functionality of a node on the Lynx network."""

    # ------------------------------------------------------------------------------
    def __init__(self, account: Account, server_port=6969, server_host=None, max_peers=12) -> None:
        # --------------------------------------------------------------------------
        """Initializes a node servent with the ability to index information
        for up to max_nodes number of peers (max_nodes may be set to 0 to allow for an
        unlimited number of peers), listening on a given server port, with a given
        peer name/id and host address. If not supplied, the host address (server_host)
        will be determined by attempting to connect to an Internet host like Google.
        """
        self.debug = 1

        self.account = account

        self.node_id = int.from_bytes(
            sha3_256(str((server_host, int(server_port))).encode()).digest(), byteorder='little')

        self.server = Server(account=account, server_host=server_host,
                             server_port=server_port, max_peers=max_peers)

        if not Utilities.is_known_peers_valid():
            Utilities.init_known_peers()

        Utilities.init_transactions()
        # self.initial_transaction_download()

        self.router = None

    # ------------------------------------------------------------------------------
    def connect_to_bootstrap_nodes(self):
        # --------------------------------------------------------------------------
        """"""

        bootstrap_nodes = {
            '1234': ('127.0.0.1', '6969'), }

        for node in bootstrap_nodes:
            if self.node_id != node:
                try:
                    bootstrap_node_thread = threading.Thread(target=self.connect_and_send, args=[
                                                             bootstrap_nodes[node][0], bootstrap_nodes[node][1], 'request', 1, 'Peer Request', node], name='Bootstrap Connection Thread (%s)' % node)
                    bootstrap_node_thread.start()
                except:
                    self.__debug(
                        'Failed to connect to bootstrap node (node_id: %s).' % node)

    # ------------------------------------------------------------------------------
    def initial_transaction_download(self):
        # --------------------------------------------------------------------------
        """"""
        self.__debug('Self.peers: %s' % self.server.peers)
        for peer in self.server.peers:
            try:
                transaction_download_thread = threading.Thread(target=self.connect_and_send, args=[
                                                               self.server.peers[peer][0], self.server.peers[peer][1], 'request', 2, 'Transaction Count Request', peer], name='Initial Transaction Download Thread (%s)' % peer)
                transaction_download_thread.start()
                print('Transaction download started!')
            except:
                self.__debug('Failed to request initial transaction download.')

    # ------------------------------------------------------------------------------
    def __run_stabilizer(self, stabilizer, delay) -> None:
        # --------------------------------------------------------------------------
        while not self.shutdown:
            stabilizer()
            time.sleep(delay)

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

        return self.connect_and_send(host, port, message_type, message_data, peer_id=next_peer_id)

    # ------------------------------------------------------------------------------
    def connect_and_send(self, host, port, message_type: str, message_flag: int, message_data, peer_id) -> list:
        # --------------------------------------------------------------------------
        """Connects and sends a message to the specified host:port. The host's
        reply, if expected, will be returned as a list.
        """

        message_replies = []
        try:
            peer_connection = PeerConnection(
                account=self.account, peer_id=peer_id, host=host, port=port, debug=self.debug)
            peer_connection.send_data(message_type, message_flag, message_data)
            self.__debug('Sent %s: %s' % (peer_id, message_type))

            if message_type == 'request':
                print('?{}'.format(peer_connection.s.getpeername()))
                reply = peer_connection.receive_data()
                while reply is not None:
                    message_replies.append(reply)
                    self.__debug('Got reply %s: %s' % (peer_id, str(reply)))
                    self.__debug(reply.message.data)
                    reply = peer_connection.receive_data()

                for response in message_replies:
                    Response(self, response)
            peer_connection.close()
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()
                self.__debug(
                    'Unable to send message to peer (%s, %s).' % (host, port))

        return message_replies

    # ------------------------------------------------------------------------------
    def check_live_peers(self) -> None:
        # --------------------------------------------------------------------------
        """Attempts to ping all currently know peers in order to ensure that they
        are still active. Removes any from the peer list that do not reply. This 
        function can be used as a simpler stabilizer.
        """

        peers_to_delete = []
        for peer_id in self.peers:
            is_connected = False
            try:
                self.__debug('Check live %s' % peer_id)
                host, port = self.server.peers[peer_id]
                peer_connection = PeerConnection(
                    account=self.account, peer_id=peer_id, host=host, port=port, debug=self.debug)
                peer_connection.send_data('PING', '')
                is_connected = True
            except:
                peers_to_delete.append(peer_id)
            if is_connected:
                peer_connection.close()

        self.server.peer_lock.acquire()
        try:
            for peer_id in peers_to_delete:
                if peer_id in self.server.peers:
                    del self.server.peers[peer_id]
        finally:
            self.server.peer_lock.release()

    # ------------------------------------------------------------------------------
    def __debug(self, message) -> None:
        # --------------------------------------------------------------------------
        if self.debug:
            display_debug(message)

# end Node class
