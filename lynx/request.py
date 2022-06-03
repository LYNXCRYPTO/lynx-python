from __future__ import annotations
from typing import TYPE_CHECKING
import json
from os import listdir
from os.path import exists
from state import State
from peer import Peer
from message import Message, SignedMessage
from message_validation import MessageValidation
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
            self.__handle_account_request()
        elif self.message.flag == 4:
            self.__handle_data_request()
        elif self.message.flag == 5:
            self.__handle_heartbeat_request()

    # ------------------------------------------------------------------------------
    def __handle_version_request(self) -> None:
        # --------------------------------------------------------------------------
        """"""
        if MessageValidation.validate_version_request(message=self.message) and not self.server.max_peers_reached():

            peer = Peer(peer_info=self.message.data)
            self.server.add_peer(peer)

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
            # for peer in self.server.peers:
            #     host, port = peer.split(':')
            # self.server.connect_and_send(
            #     host, port, self.message.type, self.message.flag, self.message.data, self.server.server.peers[peer].nonce)

            known_peers = [*Peer.get_known_peers()]
            payload = {'address_count': len(
                known_peers), 'address_list': known_peers}

            self.peer_connection.send_data(
                'response', self.message.flag, payload)

    # ------------------------------------------------------------------------------
    def __handle_account_request(self) -> None:
        # --------------------------------------------------------------------------
        """"""

        if MessageValidation.validate_account_request(message=self.message):

            account_path = '../accounts/{}/'.format(
                self.message.data['account'])
            state_path = account_path + 'states/'

            if exists(account_path) and exists(state_path):
                state_hashes = []
                count = 1
                best_state_found = False
                for file in listdir(state_path):
                    with open(state_path + file, 'r+') as state_file:
                        state = State.from_File(state_file)
                        if state.current_reference == self.message.data['best_state']:
                            best_state_found = True
                        elif best_state_found:
                            state_hashes.append(state.current_reference)
                        if count > 500:
                            break
                        state_file.close()
                        count += 1

                payload = {'count': len(state_hashes),
                           'inventory': state_hashes, }
            else:
                payload = {'count': 0, 'inventory': [], }

            self.peer_connection.send_data(
                'response', self.message.flag, payload)

    # ------------------------------------------------------------------------------
    def __handle_data_request(self) -> None:
        # --------------------------------------------------------------------------
        """"""
        pass

    # ------------------------------------------------------------------------------
    def __handle_heartbeat_request(self) -> None:
        # --------------------------------------------------------------------------
        """"""

        self.peer_connection.send_data(
            message_type='response', message_flag=self.message.flag, message_data='PONG')
        print('Heartbeat Sent!')


# end Request class
