import uuid
import socket
import time
import threading
import traceback
import requests
from lynx.p2p.peer import Peer
from lynx.inventory import Inventory
from lynx.p2p.peer_connection import PeerConnection
from lynx.p2p.request import Request
from lynx.p2p.response import Response
from lynx.message import Message
from lynx.constants import PROTOCOL_VERSION, NODE_SERVICES, SUB_VERSION
from lynx.utilities import Utilities


class Server:

    def __init__(self, nonce: str, port=6969, host=None) -> None:
        """Initializes a servent with the ability to index information
        for up to max_nodes number of peers (max_nodes may be set to 0 to allow for an
        unlimited number of peers), listening on a given server port, with a given
        peer name/id and host address. If not supplied, the host address (host)
        will be determined by attempting to connect to an Internet host like Google.
        """

        self.nonce = nonce

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

        # self.account_inventory = Inventory(on_extension=self.send_all_peers_request, flag=4)
        # self.state_inventory = Inventory(on_extension=self.send_all_peers_request, flag=5)

        self.account_inventory_lock = threading.Lock()
        self.state_inventory_lock = threading.Lock()

        self.shutdown = False  # condition used to stop server listen

        print('Configuring Port...')
        print('Server Configured!')
        print(f'Server Information:\n\tHost: {self.host} (IPV4)\n\tPort: {self.port}\n\tNode ID (Nonce): {self.nonce}\n')


    def __init_server_host(self) -> None:
        """Attempts to connect to an Internet host like Google to determine
        the local machine's IP address.
        """
        print("Configuring IP Address...")
        ip_request = requests.request('GET', 'http://myip.dnsomatic.com')
        self.host = ip_request.text

    # def send_version_request(self, peer: Peer):
    #     """"""

    #     version_message = {'version': PROTOCOL_VERSION,
    #                        'services': NODE_SERVICES,
    #                        'timestamp': str(time.time()),
    #                        'nonce': self.nonce,
    #                        'address_from': '{}:{}'.format(self.host, self.port),
    #                        'address_receive': peer.address,
    #                        'sub_version': SUB_VERSION,
    #                        'start_accounts_count': Utilities.get_transaction_count(),
    #                        'max_states_in_transit': 10,
    #                        'relay': False,
    #                        }

    #     try:
    #         version_request_thread = threading.Thread(target=self.connect_and_send, args=[
    #             peer.host, peer.port, 'request', 1, version_message, peer.address], name='Version Request Thread')
    #         version_request_thread.start()
    #     except:
    #         self.__debug('Failed to Send Version Request. Retrying...')


    # def send_address_request(self, peer: Peer):
    #     """"""

    #     payload = {'address_count': 1,
    #                'address_list': [peer.address]}

    #     try:
    #         address_request_thread = threading.Thread(target=self.connect_and_send, args=[peer.host, peer.port, 'request', 2, payload, peer.address], name='Address Request Thread')
    #         address_request_thread.start()
    #     except:
    #         self.__debug('Failed to Send Address Request. Retrying...')

    
    # def send_campaign(self, peer: Peer):
    #     ...


    # def send_data_request(self, peer: Peer):
    #     """"""

    #     try:
    #         if len(peer.states_requested) < peer.max_states_in_transit:
    #             batch_amount = peer.max_states_in_transit - \
    #                 len(peer.states_requested)
    #             inventory_batch = self.state_inventory.get_batch(
    #                 amount=batch_amount)
    #             if len(inventory_batch) > 0:
    #                 payload = {'count': len(
    #                     inventory_batch), 'inventory': inventory_batch}

    #                 self.peer_lock.acquire()
    #                 peer.states_requested.extend(inventory_batch)
    #                 self.peer_lock.release()

    #                 data_request_thread = threading.Thread(target=self.connect_and_send, args=[
    #                     peer.host, peer.port, 'request', 5, payload, peer.address], name='Data Request Thread')
    #                 data_request_thread.start()
    #             else:
    #                 raise ValueError
    #         else:
    #             raise IndexError
    #     except IndexError:
    #         self.__debug(
    #             f'Peer Is Too Busy Reponding to {peer.max_states_in_transit} Requests!')
    #     except ValueError:
    #         self.__debug('There is Nothing to Request Data For!')
    #     except:
    #         self.__debug('Failed to send data request. Retrying...')
    #         del peer.states_requested[-len(inventory_batch):]


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

        print('\n********************\n')
        print('Incoming Peer Connection Detected!')

        try:
            host, port = client_socket.getpeername()
            print(f'Peer Connection Information:\n\tHost: {host} (IPV4)\n\tPort: {port}\n')
            peer_connection = PeerConnection(peer_id=None, host=host, port=port, sock=client_socket)

            message = peer_connection.receive_data()

            if message is None or not message.validate():
                raise ValueError

            if message.type.lower() == 'request':
                print(f'Received request from ({host}:{port})')
                print(f'Request Information:\n\tType: {message.type}\n\tFlag: {message.flag}\n\tData: {message.data}\n')

                Request(server=self, message=message, peer_connection=peer_connection)
            # elif message.message.type.upper() == 'RESPONSE':
            #     Response(node=self, message=message)

        except ValueError:
            traceback.print_exc()
            print('Message received was not formatted correctly or was of None value.')
        except:
            print('Failed to handle message')

        print('Disconnecting from ' + str(client_socket.getpeername()))
        print('\n********************')
        peer_connection.close()


    def start_server_listen(self) -> None:
        """"""

        server_socket = self.make_server_socket(self.port)
        server_socket.settimeout(2)

        print('Server Has Started Listening For Incoming Connections...')

        while not self.shutdown:
            try:
                # self.__debug('')
                client_socket, client_address = server_socket.accept()
                client_socket.settimeout(None)

                client_thread = threading.Thread(target=self.__handle_peer, args=[client_socket], name=('Client Thread'))
                client_thread.start()
            except KeyboardInterrupt:
                print('KeyboardInterrupt: stopping server listening')
                self.shutdown = True
                continue
            except:
                continue

        print('Stopping server listen')
        server_socket.close()


# end Server class
