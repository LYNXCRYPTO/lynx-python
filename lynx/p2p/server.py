import socket
import threading
import multiprocess
from typing import TYPE_CHECKING
from lynx.p2p.peer_connection import PeerConnection
from lynx.p2p.request import Request
from lynx.p2p.response import Response
from lynx.p2p.message import Message, MessageType
from lynx.p2p.ip import IP
from lynx.constants import DEFAULT_PORT
if TYPE_CHECKING:
    from lynx.p2p.node import Node


class Server:

    def __init__(self, node: 'Node', host : str = None, port: str = DEFAULT_PORT) -> None:
        """Initializes a servent with the ability to index information
        for up to max_nodes number of peers (max_nodes may be set to 0 to allow for an
        unlimited number of peers), listening on a given server port, with a given
        peer name/id and host address. If not supplied, the host address (host)
        will be determined by attempting to connect to an Internet host like Google.
        """

        print('\nConfiguring Server...')
        self.node = node
        self.port = port

        print("Resolving IP Address...")
        if host:
            self.host = host
        else:
            self.host = IP.get_external_ip()

        self.shutdown = False  # condition used to stop server listen

        print('Configuring Port...')
        print('Server Configured!')
        print(f'Server Information:\n\tHost: {self.host} (IPV4)\n\tPort: {self.port}\n')


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
            peer_connection = None
            print(e)
            print('Message received was not formatted correctly or was of None value.')
        except Exception as e:
            peer_connection = None
            print(e)
            print('Failed to handle message')

        if peer_connection and peer_connection.is_open():
            print('Disconnecting from ' + str(client_socket.getpeername()))
            peer_connection.close()

        print('\n********************')


    def start_server_listen(self, q, ls) -> None:
        """"""

        server_socket = self.make_server_socket(self.port)
        server_socket.settimeout(2)

        print('Server Has Started Listening For Incoming Connections...')

        while not self.shutdown:
            if q.empty():
                pass
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
