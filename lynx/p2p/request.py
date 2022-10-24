from __future__ import annotations
from typing import TYPE_CHECKING
from eth_account import Account
from eth_account.messages import encode_defunct
from lynx.p2p.peer import Peer
from lynx.p2p.message import Message, MessageType, MessageFlag
from lynx.consensus.leader_schedule import Leader, LeaderSchedule
from lynx.consensus.vrf import VRF
from lynx.message_validation import MessageValidation
from lynx.constants import PROTOCOL_VERSION
from eth.vm.forks.lynx import LynxVM
from eth_typing import Address
if TYPE_CHECKING:
    from peer_connection import PeerConnection
    from lynx.p2p.node import Node
    

class Request:

    def __init__(self, node: Node, message: Message, peer_connection: PeerConnection) -> None:
        """
        Stages the node to handle a request message. Once staged, the corresponding handler
        function will be called to manage the request.
        """

        self.node = node
        self.message = message
        self.peer_connection = peer_connection
        self.__request_selector()


    def __request_selector(self) -> None:
        """
        Given the request's message, a function corresponding to the
        message's flag will be called in order to handle the request.
        """

        if self.message.flag is MessageFlag.HEARTBEAT:
            self.__handle_heartbeat()
        if self.message.flag is MessageFlag.VERSION:
            self.__handle_version()
        elif self.message.flag is MessageFlag.TRANSACTION:
            self.__handle_transaction()
        elif self.message.flag is MessageFlag.ADDRESS:
            self.__handle_address()
        elif self.message.flag is MessageFlag.BLOCK:
            self.__handle_block()
        elif self.message.flag is MessageFlag.CAMPAIGN:
            self.__handle_campaign()

    
    def __handle_heartbeat(self) -> None:
        """
        In response to a heartbeat request (PING), sends a PONG in response indicating 
        that the node is still alive and connected.
        """

        payload = 'PONG'

        self.peer_connection.send_data(message_type=MessageType.RESPONSE, message_flag=self.message.flag, message_data=payload)
        print('Heartbeat Sent!')


    def __handle_version(self) -> None:
        """
        In response to a version request, sends a version message back containing information
        relating to the node's software version, IP address, and port.
        """

        if MessageValidation.validate_version_request(self.message):
            peer = Peer(**self.message.data)
            peer_added = self.node.add_peer(peer)

            if peer_added:
                if self.node.server.host == peer.address:
                    address = '127.0.0.1'
                else:
                    address = self.node.server.host

                payload = {"version": PROTOCOL_VERSION, "address": address, "port": self.node.server.port}

                self.peer_connection.send_data(message_type=MessageType.RESPONSE, message_flag=self.message.flag, message_data=payload)

            else:
                if self.node.max_peers_reached():
                    print("Max peers reached, unable to add peer...")
                else:
                    print("Peer is already known...")
        else:
            print('Version request message is formatted incorrectly, unable to handle message...')


    def __handle_transaction(self) -> None:
        """
        Validates an incoming transaction. Checks whether the transaction is formatted correctly
        and if the transaction sender has the funds to complete the transaction.
        """
        
        if MessageValidation.validate_transaction_request(self.message):
            print('Transaction request received...')
            vm : LynxVM = self.node.blockchain.get_vm()
            raw_tx = self.message.data
            raw_tx['to'] = Address(raw_tx['to'].encode())
            raw_tx['data'] = raw_tx['data'].encode()
            #TODO FIX THIS
            tx = vm.create_transaction(**raw_tx)
            self.node.mempool.add_transaction(tx)

        else:
            print('Transaction request message is formatted incorrectly, unable to handle message...')


    def __handle_address(self) -> None:
        """
        In response to a address request, sends a message back containing a list
        of nodes that the local machine is currently connected to in an attempt
        to make the requesting node more well connected.
        """

        host, port = self.peer_connection.socket.getpeername()

        peers = []
        for peer in self.node.peers:
            if not peer.address == host:
                p = {"address": peer.address, "port": peer.port}
                peers.append(p)

        payload = {'peers': peers}

        self.peer_connection.send_data(message_type=MessageType.RESPONSE, message_flag=self.message.flag, message_data=payload)


    def __handle_block(self) -> None:
        """
        
        """

        if MessageValidation.validate_block_request(self.message):
            print("BLOCK RECEIVED")
        else:
            print('Block request message is formatted incorrectly, unable to handle message...')

    
    def __handle_campaign(self) -> None:
        """
        In response to a campaign request, the campaign will be checked to see whether
        it is greater than the existing campaign's candidate. If so, the validator will
        be elected as block leader.
        """

        if MessageValidation.validate_campaign_request(self.message):
            for block_number, leader in self.message.data.items():
                # TODO: Verify leader's campaign (campaign x validator's stake)
                new_leader : Leader = Leader(leader['address'], 69, leader['campaign'])
                address = Address(bytes.fromhex(new_leader.address[2:]))

                if VRF.verify_random_number(block_number, address, new_leader.campaign):
                    current_leader : Leader = self.node.leader_schedule.get_leader_by_block_number(block_number)
                    if current_leader is None or new_leader.campaign > current_leader.campaign:
                        self.node.leader_schedule.add_leader(block_number, new_leader)

        else:
            print('Campaign request message is formatted incorrectly, unable to handle message...')


    def __handle_query(self) -> None:
        """"""

        if MessageValidation.validate_query_request(self.message):
            if self.message.data["block_hash"] in self.node.snowball.undecided_blocks:
                pass
            

 

# end Request class
