from __future__ import annotations
import time
from lynx.p2p.message import Message, MessageType, MessageFlag
from lynx.message_validation import MessageValidation
from lynx.state import State
from lynx.freezer import Freezer
from lynx.p2p.peer import Peer
from os import listdir
from os.path import exists
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lynx.p2p.node import Node, PeerConnection
    from lynx.p2p.node import Node


class Response:

    def __init__(self, node: Node, message: Message, peer_connection: PeerConnection, response_time=float) -> None:
        """On creation, a Response object will automatically handle an incoming 
        message and call the corresponding function based on the message's flag
        """

        self.debug = 1

        self.node = node
        self.message = message
        self.peer_connection = peer_connection
        self.response_time = response_time
        self.__response_selector()


    def __response_selector(self) -> None:
        """Is called on intitialization and automatically will handle any information
        in response to a request.
        """

        if self.message.flag is MessageFlag.HEARTBEAT:
            self.__handle_heartbeat_response()
        if self.message.flag is MessageFlag.VERSION:
            self.__handle_version_response()


    def __handle_heartbeat_response(self) -> None:
        """"""
        host, port = self.peer_connection.socket.getpeername()
        peer = Peer(address=host, port=str(port), ping=self.response_time, last_alive=time.time())
        
        Freezer.store_peer(peer)
        


    def __handle_version_response(self) -> None:
        """Checks to see if verack message is valid, if so, node will send their
        IP address and port to the newly connected node in an attempt to become
        more well known and better connected.
        """

        if MessageValidation.validate_version_request(message=self.message):
            peer = Peer(version=self.message.data["version"], address=self.message.data["address"], port=self.message.data["port"], ping=self.response_time, last_alive=time.time())

            Freezer.store_peer(peer)
        else:
            print('Unable to handle address request')


# end Request class
