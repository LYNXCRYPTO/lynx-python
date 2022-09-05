from __future__ import annotations
from typing import TYPE_CHECKING
from os import listdir
from os.path import exists
from lynx.state import State
from lynx.p2p.peer import Peer
from lynx.p2p.message import Message, MessageType, MessageFlag
from lynx.message_validation import MessageValidation
from lynx.constants import PROTOCOL_VERSION
from eth.vm.forks.lynx import LynxVM
from eth_typing import Address
if TYPE_CHECKING:
    from peer_connection import PeerConnection
    from lynx.p2p.node import Node
    

class Request:

    def __init__(self, node: Node, message: Message, peer_connection: PeerConnection) -> None:
        """"""

        self.node = node
        self.message = message
        self.peer_connection = peer_connection
        self.__request_selector()


    def __request_selector(self) -> None:
        """"""
        if self.message.flag is MessageFlag.HEARTBEAT:
            self.__handle_heartbeat()
        if self.message.flag is MessageFlag.VERSION:
            self.__handle_version()
        elif self.message.flag is MessageFlag.TRANSACTION:
            self.__handle_transaction()
        elif self.message.flag == 4:
            self.__handle_accounts_request()
        elif self.message.flag == 5:
            self.__handle_states_request()
        elif self.message.flag == 6:
            self.__handle_data_request()

    
    def __handle_heartbeat(self) -> None:
        """"""

        payload = 'PONG'

        self.peer_connection.send_data(message_type=MessageType.RESPONSE, message_flag=self.message.flag, message_data=payload)
        print('Heartbeat Sent!')


    def __handle_version(self) -> None:
        """"""
        if MessageValidation.validate_version_request(message=self.message):
            peer = Peer(**self.message.data)
            peer_added = self.node.add_peer(peer)

            if peer_added:
                payload = {"version": PROTOCOL_VERSION, "address": self.node.server.host, "port": self.node.server.port}

                self.peer_connection.send_data(message_type=MessageType.RESPONSE, message_flag=self.message.flag, message_data=payload)
            else:
                print("Max peers reached, unable to add peer...")
        else:
            print('Version request message is formatted incorrectly, unable to handle message...')


    def __handle_transaction(self) -> None:
        """"""
        
        if MessageValidation.validate_transaction_request(message=self.message):
            print('Transaction request received...')
            vm : LynxVM = self.node.blockchain.get_vm()
            raw_tx = self.message.data
            raw_tx['to'] = Address(raw_tx['to'].encode())
            raw_tx['data'] = raw_tx['data'].encode()
            #TODO FIX THIS
            tx = vm.create_transaction(**raw_tx)
            self.node.mempool_lock.acquire()
            self.node.mempool.add_transaction(tx)
            self.node.mempool_lock.release()
            print(self.node.mempool.transactions())


    def __handle_address_request(self) -> None:
        """"""

        if MessageValidation.validate_address_request(message=self.message):
            # for peer in self.server.peers:
            #     host, port = peer.split(':')
            # self.server.connect_and_send(
            #     host, port, self.message.type, self.message.flag, self.message.data, self.server.server.peers[peer].nonce)

            payload = {'address_count': len([]), 'address_list': ""}

            self.peer_connection.send_data(
                'response', self.message.flag, payload)


    def __handle_accounts_request(self) -> None:
        """"""

        account_hashes = []

        if MessageValidation.validate_accounts_request(message=self.message):
            account_path = '../accounts/'
            if exists(account_path):
                count = 1
                for account in listdir(account_path):
                    account_hashes.append(account)
                    if count > 500:
                        break
                    count += 1

        payload = {
            'count': len(account_hashes),
            'inventory': account_hashes, }

        self.peer_connection.send_data(
            'response', self.message.flag, payload)


    def __handle_states_request(self) -> None:
        """"""
        state_hashes = []

        if MessageValidation.validate_states_request(message=self.message):
            account_path = '../accounts/{}/'.format(
                self.message.data['account'])
            state_path = account_path + 'states/'
            if exists(account_path) and exists(state_path):
                count = 1
                best_state_found = self.message.data['best_state'] == '' or self.message.data['best_state'] is None
                for file in listdir(state_path):
                    with open(state_path + file, 'r+') as state_file:
                        state = State.from_file(state_file)
                        if best_state_found:
                            state_hashes.append(
                                f'{self.message.data["account"]}/{state.current_reference}')
                        elif state.current_reference == self.message.data['best_state']:
                            best_state_found = True
                        if count > 500:
                            break
                        state_file.close()
                        count += 1

        payload = {
            'count': len(state_hashes),
            'inventory': state_hashes, }

        self.peer_connection.send_data(
            'response', self.message.flag, payload)


    def __handle_data_request(self) -> None:
        """"""

        inventory_to_send = []
        if MessageValidation.validate_data_request(message=self.message):
            for item in self.message.data['inventory']:
                data = item.split('/')
                account_reference = data[0]
                state_reference = data[1]
                account_path = f'../accounts/{account_reference}/'
                state_path = account_path + 'states/'
                if exists(account_path) and exists(state_path):
                    for file in listdir(state_path):
                        with open(state_path + file, 'r+') as state_file:
                            state = State.from_file(state_file)
                            if state.current_reference == state_reference:
                                state_payload = {'account': account_reference, 'nonce': state.nonce, 'previous_reference': state.previous_reference,
                                                 'current_reference': state.current_reference, 'balance': state.balance, }
                                inventory_to_send.append(state_payload)

        payload = {'count': len(
            inventory_to_send), 'inventory': inventory_to_send}

        self.peer_connection.send_data(
            'response', self.message.flag, payload)





# end Request class
