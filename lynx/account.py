# account.py

import threading
from Crypto.PublicKey import RSA
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme
from Crypto.Hash import SHA256
import binascii


def display_debug(msg):
    """Prints a message to the screen with the name of the current thread"""
    print("[%s] %s" % (str(threading.currentThread().getName()), msg))


class Account:
    """Primary entry point for working with Lynx private keys.

    Does *NOT* require connection to node.
    """

    # ------------------------------------------------------------------------------
    def __init__(self) -> None:
        # --------------------------------------------------------------------------
        """Generates a 1024-bit RSA key_pair made up of a public and private key"""

        self.debug = 1

        self.key_pair = RSA.generate(bits=1024)
        self.public_key = self.key_pair.publickey()

        self.nonce = 0
        self.balance = 0
        self.contract_code = ''
        # self.storage = ?

    # ------------------------------------------------------------------------------
    def __debug(self, message) -> None:
        # --------------------------------------------------------------------------
        if self.debug:
            display_debug(message)

    # ------------------------------------------------------------------------------
    def sign_message(self, message) -> bytes:
        # --------------------------------------------------------------------------
        """Signs a message using the PKCS#1 v1.5 signature scheme (RSASP1)
        and returns the signature as binary data.
        """

        binary_message = message.encode('utf-8')
        message_hash = SHA256.new(binary_message)
        signer = PKCS115_SigScheme(self.key_pair)
        signature = signer.sign(message_hash)
        self.__debug('Signature: %s' % binascii.hexlify(signature))
        return signature

    # ------------------------------------------------------------------------------
    def verify_signature(self, message, sender_public_key, signature) -> bool:
        # --------------------------------------------------------------------------
        """Verifies that the signature corresponding to the given message is a 
        valid PKCS#1 v1.5 signature (RSAVP1)
        """

        binary_message = message.encode('utf-8')
        message_hash = SHA256.new(binary_message)
        verifier = PKCS115_SigScheme(sender_public_key)
        try:
            verifier.verify(message_hash, signature)
            self.__debug('Signature is valid')
        except:
            self.__debug("Signature is invalid.")
            return False

        return True


# end Account class
