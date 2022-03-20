# node.py

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
    def __init__(self, max_peers, server_port, node_id=None, server_host=None) -> None:
        # --------------------------------------------------------------------------
        """Initializes a node servent with the ability to index information
        for up to max_nodes number of peers (max_nodes may be set to 0 to allow for an
        unlimited number of peers), listening on a given server port, with a given 
        peer name/id and host address. If not supplied, the host address (server_host)
        will be determined by attempting to connect to an Internet host like Google.
        """
        self.debug = 1

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

        self.node_lock = threading.Lock()

        self.peers = {}        # node_id => (host, port) mapping
        self.shutdown = False  # condition used to stop main loop

        self.handlers = {}
        self.router = None

    # ------------------------------------------------------------------------------
    def __init_server_host(self) -> None:
        # --------------------------------------------------------------------------
        """Attempts to connect to an Internet host like Google to determine
        the local machine's IP address.
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect(('www.google.com', 80))
        self.serverhost = server_socket.getsockname()[0]
        server_socket.close()

    # ------------------------------------------------------------------------------
    def __debug(self, msg) -> None:
        # --------------------------------------------------------------------------
        if self.debug:
            display_debug(msg)

    # ------------------------------------------------------------------------------
    def __handle_peer(self, client_socket) -> None:
        # --------------------------------------------------------------------------
        """Dispatches messages from the socket connection."""

        self.__debug('New Child '.join(
            str(threading.currentThread().getName())))
        self.__debug('Connected '.join(str(client_socket.getpeername())))

        host, port = client_socket.getpeername()
        peer_connection = PeerConnection(
            None, host, port, client_socket, debug=False)

        try:
            message_type, message_data = peer_connection.receive_data()
            if message_type:
                message_type = message_type.upper()
            if message_type not in self.handlers:
                self.__debug('Not handled: %s: %s' %
                             (message_type, message_data))
            else:
                self.__debug('Handling node message: %s: %s' %
                             (message_type, message_data))
                self.handlers[message_type](peer_connection, message_data)
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()

        self.__debug('Disconnecting '.join(str(client_socket.getpeername())))
        peer_connection.close()

    # ------------------------------------------------------------------------------
    def make_server_socket(self, port, backlog=5) -> socket:
        # --------------------------------------------------------------------------
        """Constructs and prepares a server socket listening on given port."""

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

        return self.connect_and_send(host, port, message_type, message_data, peer_id=next_peer_id, wait_for_reply=wait_for_reply)

    # ------------------------------------------------------------------------------
    def connect_and_send(self, host, port, message_type, message_data, peer_id, wait_for_reply=True) -> list[tuple[str, str]]:
        # --------------------------------------------------------------------------
        """Connects and sends a message to the specified host:port. The host's
        reply, if expected, will be returned as a list of tuples.
        """

        message_replies = []
        try:
            peer_connection = PeerConnection(
                peer_id, host, port, debug=self.debug)
            peer_connection.send_data(message_type, message_data)
            self.__debug('Sent %s: %s' % (peer_id, message_type))

            if wait_for_reply:
                reply = peer_connection.receive_data()
                while (reply != (None, None)):
                    message_replies.append(reply)
                    self.__debug('Got reply %s: %s' & (
                        peer_id, str(message_replies)))
                    reply = peer_connection.receive_data()
            peer_connection.close()
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()

        return message_replies

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
                    target=self.__handle_peer, args=[client_socket])
                client_thread.start()
            except KeyboardInterrupt:
                print('KeyboardInterrupt: stopping server listening')
                self.shutdown = True
                continue
            except:
                if self.debug:
                    traceback.print_exc()
                    continue

        self.__debug('Main loop exiting')

        server_socket.close()

# end Node class

# **********************************************************


class PeerConnection:

    # ------------------------------------------------------------------------------
    def __init__(self, peer_id, host, port, sock=None, debug=False) -> None:
        # --------------------------------------------------------------------------
        # any exceptions thrown upwards

        self.id = peer_id
        self.debug = debug

        if not sock:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((host, int(port)))
        else:
            self.s = sock

        self.sd = self.s.makefile('rw', 0)

    # ------------------------------------------------------------------------------
    def __make_message(self, message_type, message_data) -> bytes:
        # --------------------------------------------------------------------------
        message_length = len(message_data)
        message = struct.pack("!4sL%ds" % message_length,
                              message_type, message_length, message_data)
        return message

    # ------------------------------------------------------------------------------
    def __debug(self, message) -> None:
        # --------------------------------------------------------------------------
        if self.debug:
            display_debug(message)

    # ------------------------------------------------------------------------------
    def send_data(self, message_type, message_data) -> bool:
        # --------------------------------------------------------------------------
        """Send a message through a peer connection. Returns True on success or 
        False if there was an error.
        """

        try:
            message = self.__make_message(message_type, message_data)
            self.sd.write(message)
            self.sd.flush()
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()
            return False
        return True

    # ------------------------------------------------------------------------------
    def receive_data(self) -> tuple[str, str]:
        # --------------------------------------------------------------------------
        """Receive a message from a peer connection. Returns (None, None)
        if there was any error.
        """

        try:
            message_type = self.sd.read(4)
            if not message_type:
                return (None, None)

            len_str = self.sd.read(4)
            message_length = int(struct.unpack("!L", len_str)[0])
            message = ""

            while len(message) != message_length:
                data = self.sd.read(min(2048, message_length - len(message)))
                if not len(data):
                    break
                message.join(data)

            if len(message) != message_length:
                return (None, None)
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()
            return (None, None)

        return(message_type, message)

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
