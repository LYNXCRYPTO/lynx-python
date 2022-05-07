from account import Account
from peer import Peer
from peer_connection import PeerConnection
from request import Request
from response import Response
from message import Message
from constants import PROTOCOL_VERSION, NODE_SERVICES, SUB_VERSION
import time
import uuid
from utilities import Utilities
from hashlib import sha3_256
import socket
import threading
import traceback


def display_debug(msg):
    """Prints a message to the screen with the name of the current thread"""
    print("[%s] %s" % (str(threading.currentThread().getName()), msg))


class Server:

    # ------------------------------------------------------------------------------
    def __init__(self, nonce: str, port=6969, host=None, max_peers=12) -> None:
        # --------------------------------------------------------------------------
        """Initializes a servent with the ability to index information
        for up to max_nodes number of peers (max_nodes may be set to 0 to allow for an
        unlimited number of peers), listening on a given server port, with a given
        peer name/id and host address. If not supplied, the host address (host)
        will be determined by attempting to connect to an Internet host like Google.
        """

        self.debug = 1

        self.nonce = nonce

        self.max_peers = int(max_peers)
        self.port = int(port)
        if host:
            self.host = host
        else:
            self.__init_server_host()

        self.peer_lock = threading.Lock()

        test_peer = Peer(peer_info={'version': PROTOCOL_VERSION,
                                    'services': NODE_SERVICES,
                                    'timestamp': time.time(),
                                    'nonce': uuid.uuid4().hex + uuid.uuid1().hex,
                                    'address_from': '{}:{}'.format('127.0.0.1', '6968'),
                                    'address_receive': '{}:{}'.format('127.0.0.1', '6969'),
                                    'user_agent': SUB_VERSION,
                                    'start_accounts_known': 10,
                                    'relay': False,
                                    })
        # List of Peer objects
        self.peers = {'{}:{}'.format('127.0.0.1', '6968'): test_peer}

        self.shutdown = False  # condition used to stop server listen

    # ------------------------------------------------------------------------------
    def __init_server_host(self) -> None:
        # --------------------------------------------------------------------------
        """Attempts to connect to an Internet host like Google to determine
        the local machine's IP address.
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.connect(('8.8.8.8', 80))
        self.host = server_socket.getsockname()[0]
        self.__debug('SERVER HOST: ' + self.host)
        server_socket.close()

    # ------------------------------------------------------------------------------
    def send_version_request(self, host, port):
        # --------------------------------------------------------------------------
        """"""

        version_message = {'version': PROTOCOL_VERSION,
                           'services': NODE_SERVICES,
                           'timestamp': time.time(),
                           'nonce': self.nonce,
                           'address_from': '{}:{}'.format(self.host, self.port),
                           'address_receive': '{}:{}'.format(host, port),
                           'user_agent': SUB_VERSION,
                           'start_accounts_known': Utilities.get_transaction_count(),
                           'relay': False,
                           }

        try:
            version_message_thread = threading.Thread(target=self.connect_and_send, args=[
                host, port, 'request', 1, version_message, None], name='Version Message Sending Thread')
            version_message_thread.start()
        except:
            self.__debug('Failed to send version message. Retrying...')

    # ------------------------------------------------------------------------------
    def send_address_request(self, host, port):
        # --------------------------------------------------------------------------
        """"""

        payload = {'address_count': 1,
                   'address_list': ['{}:{}'.format(self.host, self.port)]}

        try:
            address_message_thread = threading.Thread(target=self.connect_and_send, args=[
                host, port, 'request', 2, payload, None], name='Address Message Sending Thread')
            address_message_thread.start()
        except:
            self.__debug('Failed to send version message. Retrying...')

    # ------------------------------------------------------------------------------
    def send_heartbeat_request(self):
        # --------------------------------------------------------------------------
        """"""

        for peer in self.peers:
            try:
                heartbeat_thread = threading.Thread(target=self.connect_and_send, args=[
                    self.peers[peer][0], self.peers[peer][1], 'request', 4, 'Heartbeat Request', peer], name='Heartbeat Thread (%s)' % peer)
                heartbeat_thread.start()
                print('Heartbeat request started!')
            except:
                self.__debug('Failed to request heartbeat from %s.' % peer)

    # ------------------------------------------------------------------------------
    def add_peer(self, host, port) -> bool:
        # --------------------------------------------------------------------------
        """Adds a peer name and host:port mapping to the known list of peers."""

        peer_id = int.from_bytes(
            sha3_256(str((host, int(port))).encode()).digest(), byteorder='little')
        if peer_id not in self.peers and (self.max_peers == 0 or len(self.peers) < self.max_peers):
            self.peer_lock.acquire()
            self.peers[peer_id] = (host, int(port))
            self.peer_lock.release()
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
            self.peer_lock.acquire()
            del self.peers[peer_id]
            self.peer_lock.release()

    # ------------------------------------------------------------------------------
    def insert_peer_at(self, index, peer_id, host, port) -> None:
        # --------------------------------------------------------------------------
        """Inserts a peer's information at a specific position in the list of peers.
        The functions insert_peer_at, get_peer_at, and remove_peer_at should not be 
        used concurrently with add_peer, get_peer, and/or remove_peer.
        """

        self.peer_lock.acquire()
        self.peers[index] = (peer_id, host, int(port))
        self.peer_lock.release()

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

        assert(self.max_peers == 0 or len(self.peers) <= self.max_peers)
        return self.max_peers > 0 and len(self.peers) == self.max_peers

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
    def __handle_peer(self, client_socket: socket.socket) -> None:
        # --------------------------------------------------------------------------
        """Dispatches messages from the socket connection."""

        self.__debug('New Thread Created: ' +
                     str(threading.currentThread().getName()))
        self.__debug('Connected ' + str(client_socket.getpeername()))

        try:
            host, port = client_socket.getpeername()
            peer_connection = PeerConnection(
                peer_id=None, host=host, port=port, sock=client_socket, debug=True)

            # add_peer_thread = threading.Thread(target=self.add_peer, args=[
            #                                    host, port], name='Add Peer Thread')
            # add_peer_thread.start()

            # add_unknown_peer_thread = threading.Thread(target=Utilities.add_unknown_peer, args=[
            #                                            host, port], name='Add Unknown Peer Thread')
            # add_unknown_peer_thread.start()

            self.__debug('Attempting to receive data from client...')
            message = peer_connection.receive_data()

            print('Is message of None value: {}'.format(message is None))
            if message is None or not message.validate():
                print(message)
                raise ValueError

            print('Message Type is {}'.format(message.type.upper()))
            if message.type.upper() == 'REQUEST':
                print('{}'.format(peer_connection.s.getpeername()))
                Request(server=self, message=message,
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
    def connect_and_send(self, host, port, message_type: str, message_flag: int, message_data, peer_id: None) -> list:
        # --------------------------------------------------------------------------
        """Connects and sends a message to the specified host:port. The host's
        reply, if expected, will be returned as a list.
        """

        message_replies = []
        try:
            peer_connection = PeerConnection(
                peer_id=peer_id, host=host, port=port, debug=self.debug)
            peer_connection.send_data(message_type, message_flag, message_data)
            self.__debug('Sent %s: %s' % (peer_id, message_type))
            self.__debug(message_data)

            if message_type == 'request':
                print('?{}'.format(peer_connection.s.getpeername()))
                reply: Message = peer_connection.receive_data()
                while reply is not None:
                    message_replies.append(reply)
                    self.__debug('Got reply %s: %s' % (peer_id, str(reply)))
                    self.__debug(reply.data)
                    reply = peer_connection.receive_data()

                for reply in message_replies:
                    if reply.type == 'request':
                        Request(self, reply, peer_connection)
                    elif reply.type == 'response':
                        Response(self, reply, peer_connection)
                    else:
                        self.__debug(
                            'Unable to handle message type of "{}"'.format(reply.type))
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
    def start_server_listen(self) -> None:
        # --------------------------------------------------------------------------
        """"""

        server_socket = self.make_server_socket(self.port)
        server_socket.settimeout(2)
        self.__debug('Server started with node: %s (%s:%d)' %
                     (self.nonce, self.host, self.port,))

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
