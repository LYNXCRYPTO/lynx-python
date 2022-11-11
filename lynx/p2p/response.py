from __future__ import annotations
import time
from lynx.p2p.message import Message, MessageType, MessageFlag
from lynx.p2p.message_validation import MessageValidation
from lynx.freezer import Freezer
from lynx.p2p.peer import Peer
from eth.vm.forks.lynx.blocks import LynxBlock, LynxBlockHeader
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lynx.p2p.node import Node
    from lynx.p2p.peer_connection import PeerConnection


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
        
        if MessageValidation.validate_message(self.message):
            if self.message.flag is MessageFlag.HEARTBEAT:
                self.__handle_heartbeat()
            elif self.message.flag is MessageFlag.VERSION:
                self.__handle_version()
            elif self.message.flag is MessageFlag.ADDRESS:
                self.__handle_address()
            elif self.message.flag is MessageFlag.BLOCK:
                self.__handle_block()
            elif self.message.flag is MessageFlag.QUERY:
                self.__handle_query()


    def __handle_heartbeat(self) -> None:
        """"""
        host, port = self.peer_connection.socket.getpeername()
        peer = Peer(address=host, port=str(port), ping=self.response_time, last_alive=time.time())
        
        Freezer.store_peer(peer)
        

    def __handle_version(self) -> None:
        """Checks to see if verack message is valid, if so, node will send their
        IP address and port to the newly connected node in an attempt to become
        more well known and better connected.
        """

        peer = Peer(**self.message.data) 
        peer.ping=self.response_time
        peer.last_alive=time.time()

        if peer.address == self.node.server.host:
            peer.address = "127.0.0.1"

        self.node.add_peer(peer)
            

    def __handle_address(self) -> None:
        """"""

        peers = self.message.data['peers']
        
        for index, peer in enumerate(peers):
            p = Peer(address=peer['address'], port=peer['port'])
            peers[index] = p
        
        self.node.broadcast(MessageFlag.VERSION, peers=peers)


    def __handle_block(self) -> None:
        """
        """

        data = self.message.data['blocks']

        for data in self.message.data['blocks']:
            data['parent_hash'] = bytes.fromhex(data['parent_hash'])
            data['coinbase'] = bytes.fromhex(data['coinbase'])
            data['transaction_root'] = bytes.fromhex(data['transaction_root'])
            data['state_root'] = bytes.fromhex(data['state_root'])
            data['receipt_root'] = bytes.fromhex(data['receipt_root'])
            data['extra_data'] = bytes.fromhex(data['extra_data'])

            header : LynxBlockHeader = LynxBlockHeader(**data)
            block : LynxBlock = LynxBlock(header)
            # Works for now, but should import block instead of forging

            if self.node.is_bootstrapping:
                self.node.blockchain.import_block(block)
            else:
                self.node.snowball.add_block(header)


    def __handle_query(self) -> None:
        """
        """

        pass

# end Request class
