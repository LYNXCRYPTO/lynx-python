from inspect import Signature
from lynx.message import Message, SignedMessage
from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet
from hdwallet.derivations import BIP44Derivation
from hdwallet.utils import generate_mnemonic
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from typing import Optional


class Wallet:

    def __init__(self):
        MNEMONIC: str = generate_mnemonic(language="english", strength=160)
        PASSPHRASE: Optional[str] = None

        bip44_hdwallet: BIP44HDWallet = BIP44HDWallet(
            cryptocurrency=EthereumMainnet)
        bip44_hdwallet.from_mnemonic(
            mnemonic=MNEMONIC, language="english", passphrase=PASSPHRASE)
        bip44_hdwallet.clean_derivation()

        print("Mnemonic:", bip44_hdwallet.mnemonic())
        print("Base HD Path:  m/44'/60'/0'/0/0")

        bip44_derivation: BIP44Derivation = BIP44Derivation(
            cryptocurrency=EthereumMainnet, account=0, change=False, address=0)
        bip44_hdwallet.from_path(path=bip44_derivation)

        self.pub_key = bip44_hdwallet.public_key()
        self.priv_key = bip44_hdwallet.private_key()
        self.signing_key = bytearray.fromhex(self.priv_key)
        self.address = bip44_hdwallet.address()

        print('Account Created!')
        print('Seed Phrase (%s)' % (MNEMONIC))
        print("Path: %s" % bip44_hdwallet.path())
        print("Public Key: 0x%s" % self.pub_key)
        print("Address: %s" % self.address)
        print("Private Key: 0x%s" % self.priv_key)
        print(f"Extended Private Key: {bip44_hdwallet.xprivate_key()}")
        print("Signing Key: %s" % self.signing_key)
        bip44_hdwallet.clean_derivation()

    def sign_message(self, message: Message) -> SignedMessage:
        """Signs a message using ECDSA and returns 
        the signature with the message as a SignedMessage object.
        """

        message_JSON = message.to_JSON()
        message_binary = message_JSON.encode()

        signing_key = SigningKey.from_string(bytes.fromhex(self.priv_key), curve=SECP256k1)
        signature_bytes = signing_key.sign(message_JSON)
        signature = signature_bytes.decode()
        self.__debug('Signature: %s' % hex(signature))

        # return signed_message
        pass
