import socket
import threading
import requests
from typing import TYPE_CHECKING
from lynx.p2p.peer import Peer
from lynx.inventory import Inventory
from lynx.p2p.peer_connection import PeerConnection
from lynx.p2p.request import Request
from lynx.p2p.response import Response
from lynx.p2p.message import Message, MessageType
from lynx.constants import DEFAULT_PORT
if TYPE_CHECKING:
    from lynx.p2p.node import Node


class Server:

    def __init__(self, node: 'Node', port: str = DEFAULT_PORT, host=None) -> None:
        """Initializes a servent with the ability to index information
        for up to max_nodes number of peers (max_nodes may be set to 0 to allow for an
        unlimited number of peers), listening on a given server port, with a given
        peer name/id and host address. If not supplied, the host address (host)
        will be determined by attempting to connect to an Internet host like Google.
        """

        self.node = node
        self.port = port

        if host:
            self.host = host
        else:
            self.__init_server_host()

        # self.account_inventory = Inventory(on_extension=self.send_all_peers_request, flag=4)
        # self.state_inventory = Inventory(on_extension=self.send_all_peers_request, flag=5)

        self.account_inventory_lock = threading.Lock()
        self.state_inventory_lock = threading.Lock()

        self.shutdown = False  # condition used to stop server listen

        print('Configuring Port...')
        print('Server Configured!')
        print(f'Server Information:\n\tHost: {self.host} (IPV4)\n\tPort: {self.port}\n')


    def __init_server_host(self) -> None:
        """Attempts to connect to an Internet host like Google to determine
        the local machine's IP address.
        """
        print("Configuring IP Address...")
        ip_request = requests.request('GET', 'http://myip.dnsomatic.com')
        self.host = ip_request.text


    def make_server_socket(self, port, backlog=5) -> socket.socket:
        """Constructs and prepares a server socket listening on given port.

        For more information on port forwarding visit: https://stackoverflow.com/questions/45097727/python-sockets-port-forwarding
        """

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('', int(port)))
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

            message : Message = peer_connection.receive_data()

            if message is None or not message.validate():
                print(message.data)
                raise ValueError

            if message.type is MessageType.REQUEST:
                print(f'Received request from ({host}:{port})')
                print(f'Request Information:\n\tType: {message.type}\n\tFlag: {message.flag}\n\tData: {message.data}\n')

                Request(node=self.node, message=message, peer_connection=peer_connection)
            # elif message.message.type.upper() == 'RESPONSE':
            #     Response(node=self, message=message)

        except ValueError as e:
            print(e)
            print('Message received was not formatted correctly or was of None value.')
        except Exception as e:
            print(e)
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
