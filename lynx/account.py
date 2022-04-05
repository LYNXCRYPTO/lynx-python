# account.py
from message import Message, SignedMessage
from hashlib import sha3_256
from Crypto.PublicKey import RSA
import threading

import binascii
import mnemonic 
import bip32utils
import os,bip39



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
        """Generates a 1024-bit RSA key pair made up of a public and private key"""
        strength_bits = 128
        entropy = os.urandom(strength_bits // 8)
        wallet_generator = bip39.Mnemonic('english')
        mnemonic = wallet_generator.to_mnemonic(entropy)
        assert wallet_generator.to_entropy(mnemonic) == entropy  # see, bijective! check if the mnemonic is the same as the entropy

        self.__debug('Mnemonic: %s' % mnemonic)

        mobj = mnemonic.Mnemonic("english")
        seed = mobj.to_seed(mnemonic)

        bip32_root_key_obj = bip32utils.BIP32Key.fromEntropy(seed)
        bip32_child_key_obj = bip32_root_key_obj.ChildKey(44 + bip32utils.BIP32_HARDEN).ChildKey(0 + bip32utils.BIP32_HARDEN).ChildKey(0 + bip32utils.BIP32_HARDEN).ChildKey(0).ChildKey(0)
        
        self.__debug('Account Created!')
        self.__debug('Seed Phrase (%s)' % (seed))
        self.__debug('Public Key: (%s)' % (bip32_root_key_obj.ExtendedKey()))
        self.__debug('Private Key: (n: %s, d: %s)\n' % (bip32_child_key_obj.ExtendedKey()))
        self.__debug("Address: %s" % (bip32_child_key_obj.Address()))

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
    def sign_message(self, message: Message) -> SignedMessage:
        # --------------------------------------------------------------------------
        """Signs a message using the SHA3-256 signature scheme and returns 
        the signature with the message as a SignedMessage object.
        """

        message_JSON = message.to_JSON()
        message_binary = message_JSON.encode()
        message_hash = int.from_bytes(
            sha3_256(message_binary).digest(), byteorder='big')
        signature = pow(message_hash, self.key_pair.d, self.key_pair.n)
        signed_message = SignedMessage(message=message, signature=signature)
        self.__debug('Signature: %s' % hex(signed_message.signature))

        return signed_message

    # ------------------------------------------------------------------------------
    def verify_signature(self, signed_message: SignedMessage, sender_public_key) -> bool:
        # --------------------------------------------------------------------------
        """Verifies that the signature corresponding to the given message is a
        valid SHA3-256 signature.
        """
        if signed_message.is_signed:
            message_JSON = signed_message.message.to_JSON()
            message_binary = message_JSON.encode()
            message_hash = int.from_bytes(
                sha3_256(message_binary).digest(), byteorder='big')
            hash_from_signature = pow(
                signed_message.signature, sender_public_key[1], sender_public_key[0])

            if message_hash == hash_from_signature:
                self.__debug('Signature is valid')
            else:
                self.__debug('Signature is invalid')

            return message_hash == hash_from_signature

        self.__debug('Signature is of None value')

        return False


# end Account class
