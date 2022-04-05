from __future__ import annotations
from message import Message, SignedMessage
import json
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

        if isinstance(self.message.message.data, dict) and self.node.is_known_peers_valid():
            with open('../known_peers.json', 'r+') as known_peers_file:
                data = json.load(known_peers_file)
                data.update(self.message.message.data)
                known_peers_file.seek(0)
                known_peers_file.write(json.dumps(data))
                known_peers_file.truncate()
                print('"known_peers.json" updated!')
        else:
            self.node.__init_known_peers(unknown_peer=data)


# end Request class