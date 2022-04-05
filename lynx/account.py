# account.py
from message import Message, SignedMessage
import threading

from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet
from hdwallet.derivations import BIP44Derivation
from hdwallet.utils import generate_mnemonic
from typing import Optional



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
        MNEMONIC: str = generate_mnemonic(language="english", strength=128)
        PASSPHRASE: Optional[str] = None  # "meherett
        bip44_hdwallet: BIP44HDWallet = BIP44HDWallet(cryptocurrency=EthereumMainnet)
        bip44_hdwallet.from_mnemonic(
        mnemonic=MNEMONIC, language="english", passphrase=PASSPHRASE
        )
        bip44_hdwallet.clean_derivation()
        print("Mnemonic:", bip44_hdwallet.mnemonic())
        print("Base HD Path:  m/44'/60'/0'/0/0")
        bip44_derivation: BIP44Derivation = BIP44Derivation(
        cryptocurrency=EthereumMainnet, account=0, change=False, address=0
        )
        bip44_hdwallet.from_path(path=bip44_derivation)
        self.__debug('Account Created!')
        self.__debug('Seed Phrase (%s)' % (MNEMONIC))
        self.__debug("Path: %s" % bip44_hdwallet.path())
        self.__debug("Public Key: %s" % bip44_hdwallet.public_key())
        self.__debug("Address: %s" % bip44_hdwallet.address())
        self.__debug("Private key: %s" % bip44_hdwallet.private_key())
        bip44_hdwallet.clean_derivation()
    

        # self.__debug('Public Key: (%s)' % (bip32_root_key_obj.ExtendedKey()))
        # self.__debug('Private Key: (n: %s, d: %s)\n' % (bip32_child_key_obj.ExtendedKey()))
        # self.__debug("Address: %s" % (bip32_child_key_obj.Address()))

        self.nonce = 0
        self.balance = 0
        self.contract_code = ''
        # self.storage = ?

    # ------------------------------------------------------------------------------
    def __debug(self, message) -> None:
        # --------------------------------------------------------------------------
        if self.__debug:
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
