from __future__ import annotations
from message import Message, SignedMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from node import Node, PeerConnection


class Request:

    # ------------------------------------------------------------------------------
    def __init__(self, node: Node, message: SignedMessage, peer_connection: PeerConnection) -> None:
        # --------------------------------------------------------------------------
        """"""

        self.debug = 1

        self.node = node
        self.message = message
        self.peer_connection = peer_connection
        self.__request_selector()

    # ------------------------------------------------------------------------------
    def __request_selector(self) -> None:
        # --------------------------------------------------------------------------
        """"""

        if self.message.message.flag == 1:
            self.handle_known_peers_request()

    # ------------------------------------------------------------------------------
    def handle_known_peers_request(self) -> None:
        # --------------------------------------------------------------------------
        """"""

        self.peer_connection.send_data(
            message_type='response', message_flag=self.message.message.flag, message_data=self.node.known_peers)
        print('Known Peers Sent!')


# end Request class
