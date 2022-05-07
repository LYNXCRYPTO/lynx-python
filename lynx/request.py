from __future__ import annotations
from peer import Peer
from message import Message, SignedMessage
from utilities import Utilities
from message_validation import MessageValidation
from constants import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from peer_connection import PeerConnection
    from server import Server


class Request:

    # ------------------------------------------------------------------------------
    def __init__(self, server: Server, message: Message, peer_connection: PeerConnection) -> None:
        # --------------------------------------------------------------------------
        """"""

        self.debug = 1

        self.server = server
        self.message = message
        self.peer_connection = peer_connection
        self.__request_selector()

    # ------------------------------------------------------------------------------
    def __request_selector(self) -> None:
        # --------------------------------------------------------------------------
        """"""

        if self.message.flag == 1:
            self.__handle_version_request()
        elif self.message.flag == 2:
            self.__handle_address_request()
        elif self.message.flag == 3:
            self.__handle_transaction_count_request()
        elif self.message.flag == 4:
            self.__handle_heartbeat_request()

    # ------------------------------------------------------------------------------
    def __handle_version_request(self) -> None:
        # --------------------------------------------------------------------------
        """"""
        if MessageValidation.validate_version_request(message=self.message) and not self.server.max_peers_reached():
            Peer(peer_info=self.message.data)

            self.peer_connection.send_data(
                message_type='response', message_flag=self.message.flag)
        else:
            print(
                'Version request message is formatted incorrectly, unable to handle message...')

    # ------------------------------------------------------------------------------
    def __handle_address_request(self) -> None:
        # --------------------------------------------------------------------------
        """"""

        if MessageValidation.validate_address_request(message=self.message):
            for peer in self.server.peers:
                host, port = peer.split(':')
                # self.server.connect_and_send(
                #     host, port, self.message.type, self.message.flag, self.message.data, self.server.server.peers[peer].nonce)

            known_peers = Peer.get_known_peers().keys()
            self.peer_connection.send_data(
                self.message.type, self.message.flag, known_peers)

    # ------------------------------------------------------------------------------
    def __handle_known_peers_request(self) -> None:
        # --------------------------------------------------------------------------
        """"""

        known_peers = Peer.get_known_peers()
        print('!{}'.format(self.peer_connection.s.getpeername()))
        print(self.message.type)
        print(self.message.flag)
        self.peer_connection.send_data(
            message_type='response', message_flag=self.message.flag, message_data=known_peers)
        print('Known Peers Sent!')

    # ------------------------------------------------------------------------------
    def __handle_transaction_count_request(self) -> None:
        # --------------------------------------------------------------------------
        """"""

        transaction_count = Utilities.get_transaction_count()

        self.peer_connection.send_data(
            message_type='response', message_flag=self.message.flag, message_data=transaction_count)
        print('Transaction Count Sent!')

    # ------------------------------------------------------------------------------
    def __handle_heartbeat_request(self) -> None:
        # --------------------------------------------------------------------------
        """"""

        self.peer_connection.send_data(
            message_type='response', message_flag=self.message.flag, message_data='PONG')
        print('Heartbeat Sent!')


# end Request class
