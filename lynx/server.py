from account import Account
from peer_connection import PeerConnection
from request import Request
from utilities import Utilities
from hashlib import sha3_256
import socket
import threading
import traceback


def display_debug(msg):
    """Prints a message to the screen with the name of the current thread"""
    print("[%s] %s" % (str(threading.currentThread().getName()), msg))


class Server():

    # ------------------------------------------------------------------------------
    def __init__(self, account: Account, node_id=None, server_port=6969, server_host=None, max_peers=12) -> None:
        # --------------------------------------------------------------------------
        """Initializes a servent with the ability to index information
        for up to max_nodes number of peers (max_nodes may be set to 0 to allow for an
        unlimited number of peers), listening on a given server port, with a given
        peer name/id and host address. If not supplied, the host address (server_host)
        will be determined by attempting to connect to an Internet host like Google.
        """
        self.debug = 1

        self.account = account

        if node_id is None:
            self.node_id = account.pub_key
        else:
            self.node_id = node_id

        self.max_peers = int(max_peers)
        self.server_port = int(server_port)
        if server_host:
            self.server_host = server_host
        else:
            self.__init_server_host()

        self.peer_lock = threading.Lock()

        self.peers = {}        # node_id => (host, port) mapping

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
    def add_peer(self, host, port) -> bool:
        # --------------------------------------------------------------------------
        """Adds a peer name and host:port mapping to the known list of peers."""

        peer_id = int.from_bytes(
            sha3_256(str((host, int(port))).encode()).digest(), byteorder='little')
        if peer_id not in self.peers and (self.max_peers == 0 or len(self.peers) < self.max_peers):
            self.peers[peer_id] = (host, int(port))
            self.__debug('Peer added: (%s)' % peer_id)
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

            add_peer_thread = threading.Thread(target=self.add_peer, args=[
                                               host, port], name='Add Peer Thread')
            add_peer_thread.start()

            add_unknown_peer_thread = threading.Thread(target=Utilities.add_unknown_peer, args=[
                                                       host, port], name='Add Unknown Peer Thread')
            add_unknown_peer_thread.start()

            self.__debug('Attempting to receive data from client...')
            message = peer_connection.receive_data()

            if message is None or not message.message.validate() or not message.is_signed():
                raise ValueError

            if message.message.type.upper() == 'REQUEST':
                print(';{}'.format(peer_connection.s.getpeername()))
                Request(node=self, message=message,
                        peer_connection=peer_connection)
            # elif message.message.type.upper() == 'RESPONSE':
            #     Response(node=self, message=message)

        except ValueError:
            self.__debug(
                'Message received was not formatted correctly or was of None value.')
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()
                self.__debug('Failed to handle message')

        self.__debug('Disconnecting ' + str(client_socket.getpeername()))
        peer_connection.close()

    # ------------------------------------------------------------------------------
    def make_server_socket(self, port, backlog=5) -> socket.socket:
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
    def start_server_listen(self) -> None:
        # --------------------------------------------------------------------------
        """"""

        server_socket = self.make_server_socket(self.server_port)
        server_socket.settimeout(2)
        self.__debug('Server started with node: %s (%s:%d)' %
                     (self.node_id, self.server_host, self.server_port,))

        while not self.shutdown:
            try:
                self.__debug('Listening for connections...')
                client_socket, client_address = server_socket.accept()
                client_socket.settimeout(None)

                client_thread = threading.Thread(
                    target=self.__handle_peer, args=[client_socket], name=('Client Thread'))
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

    # ------------------------------------------------------------------------------
    def __debug(self, message) -> None:
        # --------------------------------------------------------------------------
        if self.debug:
            display_debug(message)


# end Server class
