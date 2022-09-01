# account.py
from eth.constants import EMPTY_SHA3, BLANK_ROOT_HASH
from lynx.p2p.message import Message
import threading
import binascii
from hashlib import sha3_256

def display_debug(msg):
    """Prints a message to the screen with the name of the current thread"""
    print(msg)


class Account:
    """Primary entry point for working with Lynx private keys.

    Does *NOT* require connection to node.
    """

    def __init__(self) -> None:
        """Generates a 160 bit private key and a public key to be used for 
        client testing and signing. In a lot of cases, private keys will
        be imported from a file."""

        self.nonce: int = 0
        self.balance: int = 0
        self.code_hash: bytes = EMPTY_SHA3
        self.storage: bytes = BLANK_ROOT_HASH

    def __debug(self, message) -> None:
        if self.__debug:
            display_debug(message)

    # def verify_signature(self, signed_message: SignedMessage, sender_public_key) -> bool:
    #     """Verifies that the signature corresponding to the given message is a
    #     valid SHA3-256 signature.
    #     """

    #     if signed_message.is_signed:
    #         message_JSON = signed_message.message.to_JSON()
    #         message_binary = message_JSON.encode()
    #         message_hash = int.from_bytes(
    #             sha3_256(message_binary).digest(), byteorder='little')
    #         hash_from_signature = pow(
    #             signed_message.signature, sender_public_key[1], sender_public_key[0])

    #         if message_hash == hash_from_signature:
    #             self.__debug('Signature is valid')
    #         else:
    #             self.__debug('Signature is invalid')

    #         return message_hash == hash_from_signature

    #     self.__debug('Signature is of None value')

    #     return False


# end Account class
