from os.path import exists
from os import makedirs, listdir
from ipaddress import ip_address, IPv4Address
from hashlib import sha3_256
import json
import threading


class Utilities:

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
