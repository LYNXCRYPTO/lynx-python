from os.path import exists
from os import makedirs, listdir
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
    def init_known_peers(self, unknown_peers={}) -> None:
        # --------------------------------------------------------------------------
        """"""

        try:
            if exists('../known_peers.json'):
                known_peers_file = open('../known_peers.json', 'r+')
                data = json.load(known_peers_file)
                if not isinstance(data, dict):
                    raise ValueError
            else:
                raise FileNotFoundError
        except ValueError:
            known_peers_file.seek(0)
            known_peers_file.write(json.dumps(unknown_peers))
            known_peers_file.truncate()
        except FileNotFoundError:
            known_peers_file = open('../known_peers.json', 'w')
            known_peers_file.write(json.dumps(unknown_peers))
        except:
            self.__debug('Unable to initialize "known_peers.json".')
        finally:
            known_peers_file.close()

    @classmethod
    # ------------------------------------------------------------------------------
    def is_known_peers_valid(self) -> bool:
        # --------------------------------------------------------------------------
        """Checks to see if known_peers.json file exist. If exists, peers will be 
        added to self.known_peers. If the file is formatted incorrectly, 
        or the file does not exist, then create/re-initialize the file.
        """

        try:
            if exists('../known_peers.json'):
                known_peers_file = open('../known_peers.json', 'r+')
                data = json.load(known_peers_file)
                if data and isinstance(data, dict):
                    if len(data) < 12:
                        self.__debug('Less than 12 known peers (%i).' %
                                     len(data))
                else:
                    self.__debug('"known_peers.json" is empty.')
            else:
                raise FileNotFoundError
        except ValueError:
            self.__debug(
                '"known_peers.json" is formatted incorrectly or empty, Re-initializing...')
            return False
        except FileNotFoundError:
            self.__debug('"known_peers.json" not found. Creating new file...')
            return False
        except:
            self.__debug('ERROR: Unable to read/write to "known_peers.json".')
            return False
        finally:
            known_peers_file.close()

        return True

    @classmethod
    # ------------------------------------------------------------------------------
    def get_known_peers(self) -> dict:
        # --------------------------------------------------------------------------
        """"""

        if self.is_known_peers_valid():
            with open('../known_peers.json', 'r+') as known_peers_file:
                data = json.load(known_peers_file)
                known_peers_file.close()
                return data

        self.init_known_peers()
        return {}

    @classmethod
    # ------------------------------------------------------------------------------
    def add_unknown_peer(self, host, port) -> bool:
        # --------------------------------------------------------------------------
        """"""

        peer_id = int.from_bytes(
            sha3_256(str((host, int(port))).encode()).digest(), byteorder='little')
        unknown_peer = {peer_id: (host, int(port))}
        if self.is_known_peers_valid():
            with open('../known_peers.json', 'r+') as known_peers_file:
                data = json.load(known_peers_file)
                if peer_id not in data:
                    data.update(unknown_peer)
                    known_peers_file.seek(0)
                    known_peers_file.write(json.dumps(data))
                    known_peers_file.truncate()
                else:
                    return False
            known_peers_file.close()
        else:
            self.init_known_peers(unknown_peers=unknown_peer)

        return True

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

# end Utilities class
