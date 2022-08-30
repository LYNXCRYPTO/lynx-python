import uuid
import socket
import time
import threading
import traceback
import requests
from lynx.peer import Peer
from lynx.inventory import Inventory
from lynx.peer_connection import PeerConnection
from lynx.request import Request
from lynx.response import Response
from lynx.p2p.message import Message
from lynx.constants import PROTOCOL_VERSION, NODE_SERVICES, SUB_VERSION
from lynx.utilities import Utilities


def display_debug(msg):
    """Prints a message to the screen with the name of the current thread"""
    print(msg)


class Server:

    def __init__(self, nonce: str, port=6969, host=None, max_peers=12) -> None:
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

        test_peer = Peer(version=PROTOCOL_VERSION,
                         services=NODE_SERVICES,
                         timestamp=str(time.time()),
                         nonce=uuid.uuid4().hex + uuid.uuid1().hex,
                         host='127.0.0.1',
                         port='6969',
                         sub_version=SUB_VERSION,
                         start_accounts_count=10,
                         relay=False,
                         )
        # List of Peer objects
        self.peers = {'{}:{}'.format('127.0.0.1', '6969'): test_peer}

        self.account_inventory = Inventory(
            on_extension=self.send_all_peers_request, flag=4)
        self.state_inventory = Inventory(
            on_extension=self.send_all_peers_request, flag=5)

        self.account_inventory_lock = threading.Lock()
        self.state_inventory_lock = threading.Lock()

        self.shutdown = False  # condition used to stop server listen

        self.__debug('Configuring Port...')
        self.__debug('Server Configured!')
        self.__debug('Server Information:\n\tHost: {} (IPV4)\n\tPort: {}\n\tNode ID (Nonce): {}\n'.format(
            self.host, self.port, self.nonce))


    def __debug(self, message) -> None:
        if self.debug:
            display_debug(message)


    def __init_server_host(self) -> None:
        """Attempts to connect to an Internet host like Google to determine
        the local machine's IP address.
        """
        print("Configuring IP Address...")
        ip_request = requests.request('GET', 'http://myip.dnsomatic.com')
        self.host = ip_request.text

    # ------------------------------------------------------------------------------
    def send_version_request(self, peer: Peer):
        # --------------------------------------------------------------------------
        """"""

        version_message = {'version': PROTOCOL_VERSION,
                           'services': NODE_SERVICES,
                           'timestamp': str(time.time()),
                           'nonce': self.nonce,
                           'address_from': '{}:{}'.format(self.host, self.port),
                           'address_receive': peer.address,
                           'sub_version': SUB_VERSION,
                           'start_accounts_count': Utilities.get_transaction_count(),
                           'max_states_in_transit': 10,
                           'relay': False,
                           }

        try:
            version_request_thread = threading.Thread(target=self.connect_and_send, args=[
                peer.host, peer.port, 'request', 1, version_message, peer.address], name='Version Request Thread')
            version_request_thread.start()
        except:
            self.__debug('Failed to Send Version Request. Retrying...')


    def send_address_request(self, peer: Peer):
        """"""

        payload = {'address_count': 1,
                   'address_list': [peer.address]}

        try:
            address_request_thread = threading.Thread(target=self.connect_and_send, args=[
                peer.host, peer.port, 'request', 2, payload, peer.address], name='Address Request Thread')
            address_request_thread.start()
        except:
            self.__debug('Failed to Send Address Request. Retrying...')

    
    def send_campaign(self, peer: Peer):
        ...


    def send_data_request(self, peer: Peer):
        """"""

        try:
            if len(peer.states_requested) < peer.max_states_in_transit:
                batch_amount = peer.max_states_in_transit - \
                    len(peer.states_requested)
                inventory_batch = self.state_inventory.get_batch(
                    amount=batch_amount)
                if len(inventory_batch) > 0:
                    payload = {'count': len(
                        inventory_batch), 'inventory': inventory_batch}

                    self.peer_lock.acquire()
                    peer.states_requested.extend(inventory_batch)
                    self.peer_lock.release()

                    data_request_thread = threading.Thread(target=self.connect_and_send, args=[
                        peer.host, peer.port, 'request', 5, payload, peer.address], name='Data Request Thread')
                    data_request_thread.start()
                else:
                    raise ValueError
            else:
                raise IndexError
        except IndexError:
            self.__debug(
                f'Peer Is Too Busy Reponding to {peer.max_states_in_transit} Requests!')
        except ValueError:
            self.__debug('There is Nothing to Request Data For!')
        except:
            self.__debug('Failed to send data request. Retrying...')
            del peer.states_requested[-len(inventory_batch):]


    def send_heartbeat_request(self):
        """"""

        for peer in self.peers:
            try:
                heartbeat_thread = threading.Thread(target=self.connect_and_send, args=[
                    self.peers[peer][0], self.peers[peer][1], 'request', 4, 'Heartbeat Request', peer], name=f'Heartbeat Thread ({peer})')
                heartbeat_thread.start()
                print('Heartbeat request started!')
            except:
                self.__debug(f'Failed to request heartbeat from ({peer}).')


    def send_all_peers_request(self, flag: int = 0) -> None:
        """"""

        if 0 < flag < 100:
            for peer_id, peer in self.peers.items():
                if flag == 1:
                    self.send_version_request(peer)
                elif flag == 2:
                    self.send_address_request(peer)
                # elif flag == 3:
                #     self.send_accounts_request(peer)
                # elif flag == 4:
                #     self.send_states_request(peer)
                elif flag == 5:
                    self.send_data_request(peer)


    def add_peer(self, peer: Peer) -> bool:
        """Adds a peer name and host:port mapping to the known list of peers."""

        peer_id = '{}:{}'.format(peer.host, peer.port)
        if peer_id not in self.peers and (self.max_peers == 0 or len(self.peers) < self.max_peers):
            self.peer_lock.acquire()
            self.peers[peer_id] = peer
            self.peer_lock.release()
            self.__debug('Peer added: (%s)' % peer_id)
            return True

        return False


    def get_peer(self, peer_id) -> tuple:
        """Returns the (host, port) tuple for the given peer name."""

        assert(peer_id in self.peers)  # maybe make this just return NULL
        return self.peers[peer_id]


    def remove_peer(self, peer_id) -> None:
        """Removes peer information from the know list of peers."""

        if peer_id in self.peers:
            self.peer_lock.acquire()
            del self.peers[peer_id]
            self.peer_lock.release()


    def insert_peer_at(self, index, peer_id, host, port) -> None:
        """Inserts a peer's information at a specific position in the list of peers.
        The functions insert_peer_at, get_peer_at, and remove_peer_at should not be
        used concurrently with add_peer, get_peer, and/or remove_peer.
        """

        self.peer_lock.acquire()
        self.peers[index] = (peer_id, host, int(port))
        self.peer_lock.release()


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
        return self.max_peers > 0 and len(self.peers) == self.max_peers


    def make_server_socket(self, port, backlog=5) -> socket.socket:
        """Constructs and prepares a server socket listening on given port.

        For more information on port forwarding visit: https://stackoverflow.com/questions/45097727/python-sockets-port-forwarding
        """

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('', port))
        server_socket.listen(backlog)
        return server_socket


    def __handle_peer(self, client_socket: socket.socket) -> None:
        """Dispatches messages from the socket connection."""

        self.__debug('\n********************\n')
        self.__debug('Incoming Peer Connection Detected!')

        try:
            host, port = client_socket.getpeername()
            self.__debug(
                'Peer Connection Information:\n\tHost: {} (IPV4)\n\tPort: {}\n'.format(host, port))
            peer_connection = PeerConnection(
                peer_id=None, host=host, port=port, sock=client_socket, debug=True)

            message = peer_connection.receive_data()

            if message is None or not message.validate():
                raise ValueError

            if message.type.lower() == 'request':
                self.__debug(
                    'Received request from ({}:{})'.format(host, port))
                self.__debug('Request Information:\n\tType: {}\n\tFlag: {}\n\tData: {}\n'.format(
                    message.type, message.flag, message.data))

                Request(server=self, message=message,
                        peer_connection=peer_connection)
            # elif message.message.type.upper() == 'RESPONSE':
            #     Response(node=self, message=message)

        except ValueError:
            traceback.print_exc()
            self.__debug(
                'Message received was not formatted correctly or was of None value.')
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()
                self.__debug('Failed to handle message')

        self.__debug('Disconnecting from ' + str(client_socket.getpeername()))
        self.__debug('\n********************')
        peer_connection.close()


    def connect_and_send(self, host, port, message_type: str, message_flag: int, message_data, peer_id=None) -> list:
        """Connects and sends a message to the specified host:port. The host's
        reply, if expected, will be returned as a list.
        """

        message_replies = []
        try:
            peer_connection = PeerConnection(
                peer_id=peer_id, host=host, port=port, debug=self.debug)
            peer_connection.send_data(message_type, message_flag, message_data)

            if message_type == 'request':
                self.__debug(
                    f'Attempting to receive a response from ({peer_id})...')
                reply: Message = peer_connection.receive_data()
                while reply is not None:
                    message_replies.append(reply)
                    self.__debug('Received a reply!')
                    reply = peer_connection.receive_data()

                for i, r in enumerate(message_replies):
                    self.__debug(
                        f'Reply #{i + 1} Contents:\n\tType: {r.type}\n\tFlag: {r.flag}\n\tData: {r.data}\n')

                    if r.type == 'request':
                        Request(self, r, peer_connection)
                    elif r.type == 'response':
                        Response(self, r, peer_connection)
                    else:
                        self.__debug(
                            f'Unable to handle message type of "{r.type}"')
            peer_connection.close()
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()
                self.__debug(
                    'Unable to send message to peer (%s, %s).' % (host, port))

        return message_replies


    def start_server_listen(self) -> None:
        """"""

        server_socket = self.make_server_socket(self.port)
        server_socket.settimeout(2)

        self.__debug(
            'Server Has Started Listening For Incoming Connections...')

        while not self.shutdown:
            try:
                # self.__debug('')
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

        self.__debug('Stopping server listen')
        server_socket.close()



# end Server class
