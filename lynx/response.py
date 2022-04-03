from __future__ import annotations
from message import Message, SignedMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from node import Node


class Response:

    # ------------------------------------------------------------------------------
    def __init__(self, node: Node, message: SignedMessage) -> None:
        # --------------------------------------------------------------------------
        """"""

        self.debug = 1

        self.node = node
        self.message = message
        self.__response_selector()

    # ------------------------------------------------------------------------------
    def __response_selector(self) -> None:
        # --------------------------------------------------------------------------
        """"""

        if self.message.message.flag == 1:
            self.handle_known_peers_response()

    # ------------------------------------------------------------------------------
    def handle_known_peers_response(self) -> None:
        # --------------------------------------------------------------------------
        """"""

        if isinstance(self.message.message.data, dict):
            self.node.known_peers = self.message.message.data
            print('Known peers: ' + str(self.node.known_peers))


# end Request class
