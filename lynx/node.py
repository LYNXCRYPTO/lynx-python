# node.py

from account import Account
from message import Message, SignedMessage
from os.path import exists
import json
import pickle
import socket
import struct
import threading
import time
import traceback


def display_debug(msg):
    """Prints a message to the screen with the name of the current thread"""
    print("[%s] %s" % (str(threading.currentThread().getName()), msg))


class Node:
    """Implements the core functionality of a node on the Lynx network."""

    # ------------------------------------------------------------------------------
    def __init__(self, account: Account, server_port=6969, node_id=None, server_host=None, max_peers=12,) -> None:
        # --------------------------------------------------------------------------
        """Initializes a node servent with the ability to index information
        for up to max_nodes number of peers (max_nodes may be set to 0 to allow for an
        unlimited number of peers), listening on a given server port, with a given
        peer name/id and host address. If not supplied, the host address (server_host)
        will be determined by attempting to connect to an Internet host like Google.
        """
        self.debug = 1

        self.account = account

        self.max_peers = int(max_peers)
        self.server_port = int(server_port)
        if server_host:
            self.server_host = server_host
        else:
            self.__init_server_host()

        if node_id:
            self.node_id = node_id
        else:
            self.node_id = '%s:%d' % (self.server_host, self.server_port)

        self.peer_lock = threading.Lock()

        self.peers = {}        # node_id => (host, port) mapping
        self.known_peers = {}

        self.__init_known_peers()

        self.handlers = {}
        self.router = None

        self.shutdown = False  # condition used to stop server listen

    # ------------------------------------------------------------------------------
    def __init_server_host(self) -> None:
        # --------------------------------------------------------------------------
        """Attempts to connect to an Internet host like Google to determine
        the local machine's IP address.
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.connect(('8.8.8.8', 80))
        self.server_host = server_socket.getsockname()[0]
        self.__debug('SERVER HOST: ' + self.server_host)
        server_socket.close()

    # ------------------------------------------------------------------------------
    def __debug(self, message) -> None:
        # --------------------------------------------------------------------------
        if self.debug:
            display_debug(message)

    # ------------------------------------------------------------------------------
    def __init_known_peers(self) -> None:
        # --------------------------------------------------------------------------
        """Checks to see if known_peers.dat file exist. If exists, peers will be 
        added to self.known_peers. If the file is formatted incorrectly, 
        or the file does not exist, then create/re-initialize the file.
        """

        try:
            if exists('../known_peers.dat'):
                known_peers_file = open('../known_peers.dat', 'r+')
                data = json.loads(known_peers_file.read())
                if data and isinstance(data, dict):
                    self.known_peers = data
                    if len(self.known_peers) < 12:
                        self.__debug('Less than 12 known peers (%i).' %
                                     len(self.known_peers))
                else:
                    self.__debug('"known_peers.dat" is empty.')
            else:
                raise FileNotFoundError
        except ValueError:
            self.__debug(
                '"known_peers.dat" is formatted incorrectly or empty, Re-initializing...')
            known_peers_file.seek(0)
            known_peers_file.write(json.dumps(self.known_peers))
            known_peers_file.truncate()
        except FileNotFoundError:
            self.__debug('"known_peers.dat" not found. Creating new file...')
            known_peers_file = open('../known_peers.dat', 'w')
            known_peers_file.write(json.dumps(self.known_peers))
        except:
            self.debug('ERROR: Unable to read/write to "known_peers.dat".')
        finally:
            known_peers_file.close()

    # ------------------------------------------------------------------------------
    def discover_peers(self) -> None:
        # --------------------------------------------------------------------------
        self.__debug('Discover_peers() called!')

    # ------------------------------------------------------------------------------
    def connect_to_bootstrap_nodes(self):
        # --------------------------------------------------------------------------
        bootstrap_nodes = {
            '1234': ('127.0.0.1', '6969'), }
        for node in bootstrap_nodes:
            if self.node_id != node:
                try:
                    bootstrap_node_thread = threading.Thread(target=self.connect_and_send, args=[
                                                             bootstrap_nodes[node][0], bootstrap_nodes[node][1], 'request', 0, 'Peer Request', node], name='Bootstrap Connection Thread (%s)' % node)
                    bootstrap_node_thread.start()
                except:
                    self.__debug(
                        'Failed to connect to bootstrap node (node_id: %s)' % node)

    # ------------------------------------------------------------------------------
    def request_peers(self, peer_connection):
        # --------------------------------------------------------------------------
        message = Message(type='request', flag=0, data='Peer Request')
        signed_message = self.account.sign_message(message=message)
        peer_connection.send_data(signed_message)

    # ------------------------------------------------------------------------------
    def __handle_peer(self, client_socket: socket.socket) -> None:
        # --------------------------------------------------------------------------
        """Dispatches messages from the socket connection."""

        self.__debug('New Thread Created: ' +
                     str(threading.currentThread().getName()))
        self.__debug('Connected ' + str(client_socket.getpeername()))

        try:
            host, port = client_socket.getpeername()
            peer_connection = PeerConnection(
                account=self.account, peer_id=None, host=host, port=port, sock=client_socket, debug=True)

            self.__debug('Attemping to receive data from client')
            message = peer_connection.receive_data()

            if message is None:
                raise ValueError

            if message.message.type not in self.handlers:
                self.__debug('Not handled: %s: %s' %
                             (message.message.type, message.message.data))
            else:
                self.__debug('Handling node message: %s: %s' %
                             (message.message.type, message.message.data))
                self.handlers[message.message.type](
                    peer_connection, message.message.data)
        except ValueError:
            self.__debug(
                'Message receive was not formatted correctly or was of None value.')
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()
                self.__debug('Failed to handle message')

        self.__debug('Disconnecting ' + str(client_socket.getpeername()))
        peer_connection.close()

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
    def add_handler(self, message_type, handler) -> None:
        # --------------------------------------------------------------------------
        """Registers the handler for the given message type with this peer."""

        assert(len(message_type) == 4)
        self.handlers[message_type] = handler

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
    def add_peer(self, peer_id, host, port) -> bool:
        # --------------------------------------------------------------------------
        """Adds a peer name and host:port mapping to the known list of peers."""

        if peer_id not in self.peers and (self.max_peers == 0 or len(self.peers) < self.max_peers):
            self.peers[peer_id] = (host, int(port))
            return True
        return False

    # ------------------------------------------------------------------------------
    def get_peer(self, peer_id) -> tuple:
        # --------------------------------------------------------------------------
        """Returns the (host, port) tuple for the given peer name."""
        assert(peer_id in self.peers)  # maybe make this just return NULL
        return self.peers[peer_id]

    # ------------------------------------------------------------------------------
    def remove_peer(self, peer_id) -> None:
        # --------------------------------------------------------------------------
        """Removes peer information from the know list of peers."""

        if peer_id in self.peers:
            del self.peers[peer_id]

    # ------------------------------------------------------------------------------
    def insert_peer_at(self, index, peer_id, host, port) -> None:
        # --------------------------------------------------------------------------
        """Inserts a peer's information at a specific position in the list of peers.
        The functions insert_peer_at, get_peer_at, and remove_peer_at should not be 
        used concurrently with add_peer, get_peer, and/or remove_peer.
        """

        self.peers[index] = (peer_id, host, int(port))

    # ------------------------------------------------------------------------------
    def get_peer_at(self, index) -> tuple:
        # --------------------------------------------------------------------------

        if index not in self.peers:
            return None
        return self.peers[index]

    # ------------------------------------------------------------------------------
    def remove_peer_at(self, index) -> None:
        # --------------------------------------------------------------------------

        self.remove_peer(self, self.peers[index])

    # ------------------------------------------------------------------------------
    def number_of_peers(self) -> int:
        # --------------------------------------------------------------------------
        """Return the number of known peer's."""

        return len(self.peers)

    # ------------------------------------------------------------------------------
    def max_peers_reached(self) -> bool:
        # --------------------------------------------------------------------------
        """Returns whether the maximum limit of names has been added to the list of
        known peers. Always returns True if max_peers is set to 0
        """

        assert(self.max_peers == 0 or len(self.peers <= self.max_peers))
        return self.max_peers > 0 and len(self.peers) == self.max_peers

    # ------------------------------------------------------------------------------
    def make_server_socket(self, port, backlog=5) -> socket:
        # --------------------------------------------------------------------------
        """Constructs and prepares a server socket listening on given port.

        For more information on port forwarding visit: https://stackoverflow.com/questions/45097727/python-sockets-port-forwarding
        """

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('', port))
        server_socket.listen(backlog)
        return server_socket

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
    def connect_and_send(self, host, port, message_type, message_flag, message_data, peer_id) -> list[tuple[str, str]]:
        # --------------------------------------------------------------------------
        """Connects and sends a message to the specified host:port. The host's
        reply, if expected, will be returned as a list of tuples.
        """

        message_replies = []
        try:
            peer_connection = PeerConnection(
                account=self.account, peer_id=peer_id, host=host, port=port, debug=self.debug)
            peer_connection.send_data(message_type, message_flag, message_data)
            self.__debug('Sent %s: %s' % (peer_id, message_type))

            # if message_type == 'request':
            #     reply = peer_connection.receive_data()
            #     while (reply is not None):
            #         message_replies.append(reply)
            #         self.__debug('Got reply %s: %s' & (
            #             peer_id, str(message_replies)))
            #         reply = peer_connection.receive_data()
            peer_connection.close()
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()

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
                host, port = self.peers[peer_id]
                peer_connection = PeerConnection(
                    account=self.account, peer_id=peer_id, host=host, port=port, debug=self.debug)
                peer_connection.send_data('PING', '')
                is_connected = True
            except:
                peers_to_delete.append(peer_id)
            if is_connected:
                peer_connection.close()

        self.peer_lock.acquire()
        try:
            for peer_id in peers_to_delete:
                if peer_id in self.peers:
                    del self.peers[peer_id]
        finally:
            self.peer_lock.release()

    # ------------------------------------------------------------------------------
    def start_server_listen(self) -> None:
        # --------------------------------------------------------------------------
        server_socket = self.make_server_socket(self.server_port)
        server_socket.settimeout(2)
        self.__debug('Server started: %s (%s:%d)' %
                     (self.node_id, self.server_host, self.server_port,))

        while not self.shutdown:
            try:
                self.__debug('Listening for connections...')
                client_socket, client_address = server_socket.accept()
                client_socket.settimeout(None)

                client_thread = threading.Thread(
                    target=self.__handle_peer, args=[client_socket], name='Client Thread (%s)' % client_address)
                client_thread.start()
            except KeyboardInterrupt:
                print('KeyboardInterrupt: stopping server listening')
                self.shutdown = True
                continue
            except:
                if self.debug:
                    # traceback.print_exc()
                    continue

        self.__debug('Main loop exiting')

        server_socket.close()

# end Node class

# **********************************************************


class PeerConnection:

    # ------------------------------------------------------------------------------
    def __init__(self, peer_id, host, port, sock=None, account: Account = None, debug=False) -> None:
        # --------------------------------------------------------------------------
        # any exceptions thrown upwards

        self.account = account

        self.id = peer_id
        self.debug = debug

        if not sock:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((host, int(port)))
        else:
            self.s = sock

        # Initializes a file in read/write mode
        self.sd = self.s.makefile('rw', 1024)

    # ------------------------------------------------------------------------------
    def __debug(self, message) -> None:
        # --------------------------------------------------------------------------
        if self.debug:
            display_debug(message)

    # ------------------------------------------------------------------------------
    def __make_message(self, message_type, message_flag, message_data) -> SignedMessage:
        # --------------------------------------------------------------------------
        """Packs the message into a Message object and then signs it using the 
        provided Account object.

        For more information about packing visit: https://docs.python.org/3/library/struct.html
        """

        message = Message(type=message_type,
                          flag=message_flag, data=message_data)
        signed_message = self.account.sign_message(message=message)
        return signed_message

    # ------------------------------------------------------------------------------
    def send_data(self, message_type, message_flag, message_data) -> bool:
        # --------------------------------------------------------------------------
        """Send a message through a peer connection. Returns True on success or 
        False if there was an error.
        """

        try:
            signed_message = self.__make_message(
                message_type, message_flag, message_data)
            signed_message_JSON = signed_message.to_JSON()
            signed_message_binary = signed_message_JSON.encode()
            self.s.send(signed_message_binary)
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()
            return False
        return True

    # ------------------------------------------------------------------------------
    def receive_data(self) -> SignedMessage:
        # --------------------------------------------------------------------------
        """Receive a message from a peer connection. Returns an empty SignedMessage
        if there was any error.
        """
        self.__debug('Attempting to receive data...')

        try:
            signed_message_binary = self.s.recv(1024)
            signed_message = SignedMessage.from_JSON(signed_message_binary)
            return signed_message
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()
            return None

    # ------------------------------------------------------------------------------
    def close(self) -> None:
        # --------------------------------------------------------------------------
        """Close the peer connection. The send and receive methods will not work
        after this call.
        """

        self.s.close()
        self.s = None
        self.sd = None

    # ------------------------------------------------------------------------------
    def __str__(self) -> str:
        # --------------------------------------------------------------------------
        return "|%s|" & id

# end PeerConnection class
