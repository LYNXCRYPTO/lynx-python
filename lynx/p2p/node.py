# node.py
from lynx.p2p.server import Server
from lynx.p2p.peer import Peer
from lynx.p2p.peer_connection import PeerConnection
from lynx.p2p.request import Request
from lynx.p2p.response import Response
from lynx.p2p.message import Message, MessageType, MessageFlag
from lynx.utilities import Utilities
import uuid
import threading
from lynx.constants import *


class Node:
    """Implements the core functionality of a node on the Lynx network."""

    def __init__(self, host=None, port=6969, max_peers=12) -> None:
        """Initializes a node with the ability to receive requests, store information, and
        handle responses.
        """

        self.max_peers = int(max_peers)
        self.peers = [Peer(address='10.8.242.172', port='6969')]

        # TODO: Make nonce the SHA256 of host
        self.nonce = uuid.uuid4().hex + uuid.uuid1().hex

        print('\nConfiguring Node...')

        print('\nConfiguring Server...')
        self.server = Server(host=host, port=port, nonce=self.nonce)


    def connect_and_send(self, peer: Peer, message_type: str, message_flag: int, message_data, peer_id=None, retry: bool = True) -> list:
        """Connects and sends a message to the specified host:port. The host's
        reply, if expected, will be returned as a list.
        """

        message_replies = []

        try:
            peer_connection = PeerConnection(host=peer.address, port=peer.port, peer_id=peer_id)
            peer_connection.send_data(message_type, message_flag, message_data)

            if message_type is MessageType.REQUEST:
                print(f'Attempting to receive a response from ({peer_id})...')
                reply : Message = peer_connection.receive_data()

                while reply is not None:
                    message_replies.append(reply)
                    print('Received a reply!')
                    reply = peer_connection.receive_data()

                for i, r in enumerate(message_replies):
                    print(f'Reply #{i + 1} Contents:\n\tType: {r.type}\n\tFlag: {r.flag}\n\tData: {r.data}\n')

                    if r.type is MessageType.REQUEST:
                        Request(self, r, peer_connection)
                    elif r.type is MessageType.RESPONSE:
                        Response(self, r, peer_connection)
                    else:
                        print(f'Unable to handle message type of "{r.type}"')

            peer_connection.close()

        except:
            print(f'Unable to send message to peer ({peer.address} : {peer.port}).')
            if retry:
                print('Retrying...')

        if not message_replies and retry:
            return self.connect_and_send(peer, message_type, message_flag, message_data, peer_id, retry=False)
            
        return message_replies


    def broadcast(self, flag: MessageFlag):
        """Broadcasts a message to all known peers."""

        for peer in self.peers:
            if flag is MessageFlag.HEARTBEAT:
                print("hello")
                self.send_heartbeat_request(peer)
            elif flag == MessageFlag.VERSION.value:
                # self.send_version_request()
                pass


    def send_heartbeat_request(self, peer: Peer):
        """"""

        heartbeat_thread = threading.Thread(target=self.connect_and_send, args=[peer, MessageType.REQUEST, MessageFlag.HEARTBEAT, "PING"], name=f'Heartbeat Thread ({peer.address})')
        heartbeat_thread.start()
        print('Heartbeat request sent!')


    # def add_peer(self, peer: Peer) -> bool:
    #     """Adds a peer name and host:port mapping to the known list of peers."""

    #     peer_id = '{}:{}'.format(peer.host, peer.port)
    #     if peer_id not in self.peers and (self.max_peers == 0 or len(self.peers) < self.max_peers):
    #         self.peer_lock.acquire()
    #         self.peers[peer_id] = peer
    #         self.peer_lock.release()
    #         self.__debug('Peer added: (%s)' % peer_id)
    #         return True

    #     return False


    def get_peer(self, peer_id) -> tuple:
        """Returns the (host, port) tuple for the given peer name."""

        assert(peer_id in self.peers)  # maybe make this just return NULL
        return self.peers[peer_id]


    # def remove_peer(self, peer_id) -> None:
    #     """Removes peer information from the know list of peers."""

    #     if peer_id in self.peers:
    #         self.peer_lock.acquire()
    #         del self.peers[peer_id]
    #         self.peer_lock.release()


    # def insert_peer_at(self, index, peer_id, host, port) -> None:
    #     """Inserts a peer's information at a specific position in the list of peers.
    #     The functions insert_peer_at, get_peer_at, and remove_peer_at should not be
    #     used concurrently with add_peer, get_peer, and/or remove_peer.
    #     """

    #     self.peer_lock.acquire()
    #     self.peers[index] = (peer_id, host, int(port))
    #     self.peer_lock.release()


    def get_peer_at(self, index) -> tuple:

        if index not in self.peers:
            return None
        return self.peers[index]

    # # ------------------------------------------------------------------------------
    # def remove_peer_at(self, index) -> None:
    #     # --------------------------------------------------------------------------

    #     self.remove_peer(self, self.peers[index])


    def number_of_peers(self) -> int:
        """Return the number of known peer's."""

        return len(self.peers)


    def max_peers_reached(self) -> bool:
        """Returns whether the maximum limit of names has been added to the list of
        known peers. Always returns True if max_peers is set to 0
        """

        assert(self.max_peers == 0 or len(self.peers) <= self.max_peers)
        return self.max_peers > 0 and len(self.peers) == self.max_peers


# end Node class
