from account import Account
from message import Message, SignedMessage
import socket
import traceback
import threading


def display_debug(msg):
    """Prints a message to the screen with the name of the current thread"""
    print("[%s] %s" % (str(threading.currentThread().getName()), msg))


class PeerConnection:

    # ------------------------------------------------------------------------------
    def __init__(self, peer_id, host, port, sock=None, account: Account = None, debug=False) -> None:
        # --------------------------------------------------------------------------
        """Any exceptions thrown upwards"""

        self.account = account

        self.id = peer_id
        self.debug = debug

        if sock is None:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((host, int(port)))
        else:
            self.s = sock

    # ------------------------------------------------------------------------------
    def __debug(self, message) -> None:
        # --------------------------------------------------------------------------
        if self.debug:
            display_debug(message)

    # ------------------------------------------------------------------------------
    def __make_message(self, message_type, message_flag, message_data) -> SignedMessage:
        # --------------------------------------------------------------------------
        """Packs the message into a Message object and then signs it using the 
        provided Account object.

        For more information about packing visit: https://docs.python.org/3/library/struct.html
        """

        message = Message(type=message_type,
                          flag=message_flag, data=message_data)
        signed_message = self.account.sign_message(message=message)
        return signed_message

    # ------------------------------------------------------------------------------
    def send_data(self, message_type, message_flag, message_data) -> bool:
        # --------------------------------------------------------------------------
        """Send a message through a peer connection. Returns True on success or 
        False if there was an error.
        """

        try:
            signed_message = self.__make_message(
                message_type, message_flag, message_data)
            signed_message_JSON = signed_message.to_JSON()
            signed_message_binary = signed_message_JSON.encode()
            self.s.send(signed_message_binary)
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                self.__debug('Unable to send data: {}'.format(message_data))
                traceback.print_exc()
            return False
        return True

    # ------------------------------------------------------------------------------
    def receive_data(self) -> SignedMessage:
        # --------------------------------------------------------------------------
        """Receive a message from a peer connection. Returns an None if there was 
        any error.
        """
        self.__debug('Attempting to receive data...')

        try:
            signed_message_JSON = self.s.recv(1024).decode()
            signed_message = SignedMessage.from_JSON(signed_message_JSON)
            return signed_message
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                # traceback.print_exc()
                print()
            return None

    # ------------------------------------------------------------------------------
    def close(self) -> None:
        # --------------------------------------------------------------------------
        """Close the peer connection. The send and receive methods will not work
        after this call.
        """

        self.__debug('Closing peer connection with %s' % self.id)
        self.s.close()
        self.s = None
        self.sd = None

    # ------------------------------------------------------------------------------
    def __str__(self) -> str:
        # --------------------------------------------------------------------------
        """"""

        return "|%s|" & id

# end PeerConnection class
