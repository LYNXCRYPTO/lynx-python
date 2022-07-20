from base58 import BITCOIN_ALPHABET
from lynx.message import Message, SignedMessage
from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet, BitcoinMainnet
from hdwallet.derivations import BIP44Derivation
from hdwallet.utils import generate_mnemonic
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from pycoin.ecdsa import Generator, Curve
from hashlib import sha256
from typing import Optional


class Wallet:

    def __init__(self):
        MNEMONIC: str = generate_mnemonic(language="english", strength=256)
        PASSPHRASE: Optional[str] = None

        bip44_hdwallet: BIP44HDWallet = BIP44HDWallet(
            cryptocurrency=EthereumMainnet)
        bip44_hdwallet.from_mnemonic(
            mnemonic=MNEMONIC, language="english", passphrase=PASSPHRASE)
        bip44_hdwallet.clean_derivation()

        print("Mnemonic:", bip44_hdwallet.mnemonic())
        print("Base HD Path:  m/44'/60'/0'/0/0")

        bip44_derivation: BIP44Derivation = BIP44Derivation(cryptocurrency=EthereumMainnet)
        bip44_hdwallet.from_path(path=bip44_derivation)

        self.pub_key = bip44_hdwallet.public_key()
        self.priv_key = bip44_hdwallet.private_key()
        self.signing_key = bytes.fromhex(self.priv_key)
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


    def sha256_hash(self, msg: str) -> bytes:
        return sha256(msg.encode("utf8")).digest()


    def sign(self, msg: str) -> str:
        """Signs a message using ECDSA and returns the 
        signature with the message as a string representing
        the signature.
        """

        msg_hash_bytes : bytes = self.sha256_hash(msg)
        signing_key : SigningKey = SigningKey.from_string(self.signing_key, curve=SECP256k1, hashfunc=sha256)
        signature_bytes = signing_key.sign_deterministic(msg_hash_bytes)
        print(f'Signature: {signature_bytes.hex()}')
        
        verifying_key : VerifyingKey = VerifyingKey.from_string(bytes.fromhex(self.pub_key), curve=SECP256k1, hashfunc=sha256)
        print(verifying_key.verify(signature=signature_bytes, data=msg_hash_bytes, hashfunc=sha256))
        pass
