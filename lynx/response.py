from __future__ import annotations
from peer import Peer
from message import Message
from message_validation import MessageValidation
from utilities import Utilities
import json
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from node import Node, PeerConnection
    from server import Server


class Response:

    # ------------------------------------------------------------------------------
    def __init__(self, server: Server, message: Message, peer_connection: PeerConnection) -> None:
        # --------------------------------------------------------------------------
        """On creation, a Response object will automatically handle an incoming 
        message and call the corresponding function based on the message's flag
        """

        self.debug = 1

        self.server = server
        self.message = message
        self.peer_connection = peer_connection
        self.__response_selector()

    # ------------------------------------------------------------------------------
    def __response_selector(self) -> None:
        # --------------------------------------------------------------------------
        """Is called on intitialization and automatically will handle any information
        in response to a request.
        """

        if self.message.flag == 1:
            self.__handle_version_response()
        elif self.message.flag == 2:
            self.__handle_address_response()
        elif self.message.flag == 3:
            self.__handle_transaction_count_response()
        elif self.message.flag == 4:
            self.__handle_heartbeat_response()

    # ------------------------------------------------------------------------------
    def __handle_version_response(self) -> None:
        # --------------------------------------------------------------------------
        """Checks to see if verack message is valid, if so, node will send their
        IP address and port to the newly connected node in an attempt to become
        more well known and better connected.
        """

        if MessageValidation.validate_version_request(message=self.message):
            print("You've have been added as a peer.")
            if not self.server.max_peers_reached():
                host, port = self.peer_connection.s.getpeername()

                self.server.send_address_request(host, port)
        else:
            print('Unable to handle version response')

    # ------------------------------------------------------------------------------
    def __handle_address_response(self) -> None:
        # --------------------------------------------------------------------------
        """"""
        # Work on this next!!!!!!!!!!!!!
        if MessageValidateion.validate_address_response(message=self.message):
            print("You've have been added as a peer.")
            if not self.server.max_peers_reached():
                host, port = self.peer_connection.s.getpeername()

                self.server.send_address_request(host, port)
        else:
            print('Unable to handle version response')

    # ------------------------------------------------------------------------------
    def __handle_known_peers_response(self) -> None:
        # --------------------------------------------------------------------------
        """Updates a node's "known_peers.json" file with the information received
        in the message.
        """

        if isinstance(self.message.data, dict) and Peer.is_peers_file_valid():
            with open('../known_peers.json', 'r+') as known_peers_file:
                data = json.load(known_peers_file)
                data.update(self.message.data)
                known_peers_file.seek(0)
                known_peers_file.write(json.dumps(data))
                known_peers_file.truncate()
                print('"known_peers.json" updated!')
        else:
            Peer.init_peers_file(unknown_peer=data)

    # ------------------------------------------------------------------------------
    def __handle_transaction_count_response(self) -> None:
        # --------------------------------------------------------------------------
        """"""

        if isinstance(self.message.data, int):
            if Utilities.get_transaction_count() < self.message.data:
                print("START INITIAL TRANSACTION DOWNLOAD")

    # ------------------------------------------------------------------------------
    def __handle_heartbeat_response(self) -> None:
        # --------------------------------------------------------------------------
        """"""


# end Request class
