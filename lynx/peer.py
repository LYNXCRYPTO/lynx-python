from peer_connection import PeerConnection
from utilities import Utilities
from os.path import exists
import json
import threading


class Peer:

    # ------------------------------------------------------------------------------
    def __init__(self, address: str = None, host: str = None, port: str = None, services: list = None, version: str = None, sub_version: str = None, timestamp: str = None, nonce: str = None, start_accounts_count: int = None, max_states_in_transit: int = 10, relay: bool = None, peer_info=None) -> None:
        # --------------------------------------------------------------------------
        """Initializes a Peer object with information pertaining to its IP address,
        port, network, and message logs.
        """

        self.debug = 1
        self.id = self.get_number_of_known_peers() + 1
        if peer_info is None:
            self.host = host
            self.port = port
            self.address = '{}:{}'.format(host, port)
            self.network = Utilities.is_valid_ip_address(host)
            self.services = services
            self.version = version
            self.sub_version = sub_version
            self.timestamp = timestamp
            self.nonce = nonce
            self.start_accounts_count = start_accounts_count
            self.relay = relay
            self.max_states_in_transit = max_states_in_transit
        else:
            self.address = peer_info['address_from']
            self.host, self.port = peer_info['address_from'].split(':')
            self.network = Utilities.is_valid_ip_address(
                peer_info['address_from'].split(':')[0])
            self.services = peer_info['services']
            self.version = peer_info['version']
            self.sub_version = peer_info['sub_version']
            self.timestamp = peer_info['timestamp']
            self.nonce = peer_info['nonce']
            self.start_accounts_count = peer_info['start_accounts_count']
            self.relay = peer_info['relay']
            self.max_states_in_transit = peer_info['max_states_in_transit']

        self.states_requested = []

        if not self.is_peer_known():
            self.add_peer()
        else:
            pass
            # TODO UPDATE EXISTING PEER INFORMATION HERE
            # print('UPDATE EXISTING PEER INFORMATION HERE')

    @classmethod
    # ------------------------------------------------------------------------------
    def init_peers_file(self, peers={}) -> None:
        # --------------------------------------------------------------------------
        """"""

        try:
            known_peers_file = None
            if exists('../known_peers.json'):
                known_peers_file = open('../known_peers.json', 'r+')
                data = json.load(known_peers_file)
                if not isinstance(data, dict):
                    raise ValueError
            else:
                raise FileNotFoundError
        except ValueError:
            known_peers_file.seek(0)
            known_peers_file.write(json.dumps(peers))
            known_peers_file.truncate()
        except FileNotFoundError:
            known_peers_file = open('../known_peers.json', 'w')
            known_peers_file.write(json.dumps(peers))
        except:
            self.__debug('Unable to initialize "known_peers.json".')
        finally:
            if exists('../known_peers.json') and known_peers_file is not None:
                known_peers_file.close()

    @classmethod
    # ------------------------------------------------------------------------------
    def is_peers_file_valid(self) -> bool:
        # --------------------------------------------------------------------------
        """Checks to see if known_peers.json file exist. If exists, peers will be
        added to self.known_peers. If the file is formatted incorrectly,
        or the file does not exist, then create/re-initialize the file.
        """

        try:
            known_peers_file = None
            if exists('../known_peers.json'):
                known_peers_file = open('../known_peers.json', 'r+')
                data = json.load(known_peers_file)
                if data is None or not isinstance(data, dict):
                    self.__debug('"known_peers.json" is empty.')
            else:
                raise FileNotFoundError
        except ValueError:
            self.__debug(
                '"known_peers.json" is formatted incorrectly or empty, try re-initializing...')
            return False
        except FileNotFoundError:
            self.__debug(
                '"known_peers.json" not found. try creating a new file...')
            return False
        except:
            self.__debug('ERROR: Unable to read/write to "known_peers.json".')
            return False
        finally:
            if exists('../known_peers.json') and known_peers_file is not None:
                known_peers_file.close()

        return True

    # ------------------------------------------------------------------------------
    def is_peer_known(self) -> bool:
        # --------------------------------------------------------------------------
        """"""

        known_peers = self.get_known_peers()
        return self.address in known_peers

    @classmethod
    # ------------------------------------------------------------------------------
    def get_known_peers(self) -> dict:
        # --------------------------------------------------------------------------
        """"""

        if self.is_peers_file_valid():
            with open('../known_peers.json', 'r+') as known_peers_file:
                data = json.load(known_peers_file)
                known_peers_file.close()
                return data

        self.init_peers_file()
        return {}

    @classmethod
    # ------------------------------------------------------------------------------
    def get_number_of_known_peers(self) -> int:
        # --------------------------------------------------------------------------
        """"""

        return len(self.get_known_peers())

    # ------------------------------------------------------------------------------
    def add_peer(self) -> bool:
        # --------------------------------------------------------------------------
        """"""

        known_peer_data = self.get_known_peers()
        if self.is_peers_file_valid():
            with open('../known_peers.json', 'r+') as known_peers_file:
                known_peer_data.update(
                    {self.address: json.loads(self.to_JSON())})
                known_peers_file.seek(0)
                known_peers_file.write(json.dumps(known_peer_data))
                known_peers_file.truncate()
            known_peers_file.close()
        else:
            self.init_peers_file(
                peers={self.address: json.loads(self.to_JSON())})

        return True

    # ------------------------------------------------------------------------------
    def to_JSON(self) -> str:
        # --------------------------------------------------------------------------
        """Returns a serialized version of a Peer object"""

        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    @classmethod
    # ------------------------------------------------------------------------------
    def from_JSON(self, JSON: str):
        # --------------------------------------------------------------------------
        """"Returns a Message object given a JSON input. If JSON is not formatted
        correctly, this method will return None.
        """

        try:
            data = json.loads(JSON)
            if not isinstance(data, dict):
                raise ValueError

            peer = Peer(
                address=data['address'], services=data['services'], version=data['version'], sub_version=data['sub_version'], timestamp=float(data['timestamp']), nonce=data['nonce'], start_accounts_count=int(data['start_account_count']), relay=data['relay'])
            return peer
        except ValueError:
            print('Peer data is not a "dict".')
            return None
        except KeyError:
            print('Peer is not formatted correctly.')
            return None
        except:
            print('Unable to convert data in Peer object.')
            return None

    @ classmethod
    # ------------------------------------------------------------------------------
    def __debug(self, msg) -> None:
        # --------------------------------------------------------------------------
        """Prints a message to the screen with the name of the current thread"""

        # if self.debug:
        print("[%s] %s" % (str(threading.currentThread().getName()), msg))


# end Peer class
