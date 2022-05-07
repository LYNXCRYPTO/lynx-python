from os.path import exists
from os import makedirs, listdir
from message import SignedMessage
from peer_connection import PeerConnection
from ipaddress import ip_address, IPv4Address
from hashlib import sha3_256
import json
import threading


class Utilities:

    @classmethod
    # ------------------------------------------------------------------------------
    def __debug(self, msg) -> None:
        # --------------------------------------------------------------------------
        """Prints a message to the screen with the name of the current thread"""
        print("[%s] %s" % (str(threading.currentThread().getName()), msg))

    @classmethod
    # ------------------------------------------------------------------------------
    def init_transactions(self) -> None:
        # --------------------------------------------------------------------------
        """Creates a transactions directory if it does not already exist."""

        try:
            if not exists('../transactions/'):
                makedirs('../transactions/')
        except:
            self.__debug('Unable to initialize transactions folder.')

    @classmethod
    # ------------------------------------------------------------------------------
    def get_transaction_count(self) -> int:
        # --------------------------------------------------------------------------
        """Opens and returns the number of transactions that exist locally. Returns
        None if unable to open transactions folder.
        """

        try:
            if exists('../transactions/'):
                transaction_list = listdir('../transactions/')
                transaction_count = len(transaction_list)
                return transaction_count
        except:
            self.__debug(
                'Unable to read transactions folder and return transaction count.')
            return None

    @classmethod
    # ------------------------------------------------------------------------------
    def is_valid_ip_address(self, IP: str) -> str:
        # --------------------------------------------------------------------------
        """Checks to see whether a given IP address is valid. Returns IPv4 or IPv6
        depending on which network the address corresponds to.
        """

        try:
            return 'IPv4' if type(ip_address(IP)) is IPv4Address else 'IPv6'
        except ValueError:
            return None

# end Utilities class
