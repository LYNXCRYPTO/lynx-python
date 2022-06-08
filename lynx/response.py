from __future__ import annotations
from peer import Peer
from message import Message
from message_validation import MessageValidation
from state import State
from utilities import Utilities
from os import listdir
from os.path import exists
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
            self.__handle_accounts_response()
        elif self.message.flag == 4:
            self.__handle_states_response()
        elif self.message.flag == 5:
            self.__handle_data_response()
        elif self.message.flag == 6:
            self.__handle_heartbeat_response()

    # ------------------------------------------------------------------------------
    def __handle_version_response(self) -> None:
        # --------------------------------------------------------------------------
        """Checks to see if verack message is valid, if so, node will send their
        IP address and port to the newly connected node in an attempt to become
        more well known and better connected.
        """

        if MessageValidation.validate_version_request(message=self.message):
            if not self.server.max_peers_reached():
                host, port = self.peer_connection.s.getpeername()

                # TODO self.server.send_address_request(host, port)
        else:
            print('Unable to handle address request')

    # ------------------------------------------------------------------------------
    def __handle_address_response(self) -> None:
        # --------------------------------------------------------------------------
        """"""

        if MessageValidation.validate_address_response(message=self.message):
            if not self.server.max_peers_reached():
                host, port = self.peer_connection.s.getpeername()
                for peer in self.message.data['address_list']:
                    if peer not in self.server.peers and peer != '{}:{}'.format(self.server.host, self.server.host):
                        self.server.send_version_request(host, port)
        else:
            print('Unable to handle address response')

    # ------------------------------------------------------------------------------
    def __handle_accounts_response(self) -> None:
        # --------------------------------------------------------------------------
        """"""

        if MessageValidation.validate_accounts_response(message=self.message):
            self.server.account_inventory_lock.acquire()
            self.server.account_inventory.extend(
                self.message.data['inventory'])
            self.server.account_inventory_lock.release()
        else:
            print('Unable to handle accounts response')

    # ------------------------------------------------------------------------------
    def __handle_states_response(self) -> None:
        # --------------------------------------------------------------------------
        """"""

        if MessageValidation.validate_states_response(message=self.message):
            self.server.state_inventory_lock.acquire()
            self.server.state_inventory.extend(self.message.data['inventory'])
            self.server.state_inventory_lock.release()
        else:
            print('Unable to handle states response')

    # ------------------------------------------------------------------------------
    def __handle_data_response(self) -> None:
        # --------------------------------------------------------------------------
        """"""

        if MessageValidation.validate_data_response(message=self.message):
            for data in self.message.data['inventory']:
                account_path = f'../accounts/{data["account"]}/'
                state_path = account_path + 'states/'
                new_state = State(nonce=data['nonce'], previous_reference=data['previous_reference'],
                                  current_reference=data['current_reference'], balance=data['balance'])
                if exists(account_path) and exists(state_path):
                    for file in listdir(state_path):
                        with open(state_path + file, 'r+') as state_file:
                            state = State.from_file(state_file)
                            if state.current_reference == data['previous_reference']:
                                file_name: str = file.split('.')[0]
                                new_state_height = int(
                                    file_name[5:len(file_name)]) + 1
                                with open(f'{state_path}/state{new_state_height}.dat', 'w+') as new_state_file:
                                    new_state_file.write(new_state.to_JSON())

    # ------------------------------------------------------------------------------

    def __handle_heartbeat_response(self) -> None:
        # --------------------------------------------------------------------------
        """"""
        pass


# end Request class
