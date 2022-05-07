from peer_connection import PeerConnection
from utilities import Utilities
from os.path import exists
import json
import threading


class Peer:
    """Implements functionality to help manage known and unknown peers.
    Responsible for reading and writing to "known_peers.json" file.

    "id" : n,                               (numeric) Peer index
    "address" : "str",                      (string) (host:port) The IP address and port of the peer
    "address_bind" : "str",                 (string) (ip:port) Bind address of the connection to the peer
    "address_local" : "str",                (string) (ip:port) Local address as reported by the peer
    "network" : "str",                      (string) Network (ipv4, ipv6, or onion) the peer connected through
    "mapped_as" : n,                        (numeric) The AS in the BGP route to the peer used for diversifying
                                            peer selection (only available if the asmap config flag is set)
    "services" : "hex",                     (string) The services offered
    "services_names" : [                    (json array) the services offered, in human-readable form
        "str",                                (string) the service name if it is recognised
        ...
    ],
    "relay_transactions" : True|False,      (boolean) Whether peer has asked us to relay transactions to it
    "last_send" : xxx,                      (numeric) The UNIX epoch time of the last send
    "last_recv" : xxx,                      (numeric) The UNIX epoch time of the last receive
    "last_transaction" : xxx,               (numeric) The UNIX epoch time of the last valid transaction received from this peer
    "last_block" : xxx,                     (numeric) The UNIX epoch time of the last block received from this peer
    "bytes_sent" : n,                       (numeric) The total bytes sent
    "bytes_recv" : n,                       (numeric) The total bytes received
    "connection_time" : xxx,                (numeric) The UNIX epoch time of the connection
    "time_offset" : n,                      (numeric) The time offset in seconds
    "ping_time" : n,                        (numeric) ping time (if available)
    "min_ping" : n,                         (numeric) minimum observed ping time (if any at all)
    "ping_wait" : n,                        (numeric) ping wait (if non-zero)
    "version" : n,                          (numeric) The peer version, such as 70001
    "sub_version" : "str",                  (string) The string version
    "inbound" : True|False,                 (boolean) Inbound (true) or Outbound (false)
    "add_node" : True|False,                (boolean) Whether connection was due to addnode/-connect or if it was an automatic/inbound connection
                                            (DEPRECATED, returned only if the config option -deprecatedrpc=getpeerinfo_addnode is passed)
    "connection_type" : "str",              (string) Type of connection:
                                            outbound-full-relay (default automatic connections),
                                            block-relay-only (does not relay transactions or addresses),
                                            inbound (initiated by the peer),
                                            manual (added via addnode RPC or -addnode/-connect configuration options),
                                            addr-fetch (short-lived automatic connection for soliciting addresses),
                                            feeler (short-lived automatic connection for testing addresses).
                                            Please note this output is unlikely to be stable in upcoming releases as we iterate to
                                            best capture connection behaviors.
    "total_checkpoints" : n,                (numeric) The starting number of checkpoints known by the peer
    "ban_score" : n,                        (numeric) The ban score (DEPRECATED, returned only if config option -deprecatedrpc=banscore is passed)
    "synced_headers" : n,                   (numeric) The last header we have in common with this peer
    "synced_checkpoints" : n,               (numeric) The last block we have in common with this peer
    "inflight" : [                          (json array)
        n,                                    (numeric) The heights of blocks we're currently asking from this peer
        ...
    ],
    "white_listed" : True|False,            (boolean, optional) Whether the peer is whitelisted with default permissions
                                            (DEPRECATED, returned only if config option -deprecatedrpc=whitelisted is passed)
    "permissions" : [                       (json array) Any special permissions that have been granted to this peer
        "str",                                (string) bloomfilter (allow requesting BIP37 filtered blocks and transactions),
                                                noban (do not ban for misbehavior; implies download),
                                                forcerelay (relay transactions that are already in the mempool; implies relay),
                                                relay (relay even in -blocksonly mode, and unlimited transaction announcements),
                                                mempool (allow requesting BIP35 mempool contents),
                                                download (allow getheaders during IBD, no disconnect after maxuploadtarget limit),
                                                addr (responses to GETADDR avoid hitting the cache and contain random records with the most up-to-date info).

        ...
    ],
    "min_fee_filter" : n,                   (numeric) The minimum fee rate for transactions this peer accepts
    "bytes_sent_per_msg" : {                (json object)
        "msg" : n,                            (numeric) The total bytes sent aggregated by message type
                                                When a message type is not listed in this json object, the bytes sent are 0.
                                                Only known message types can appear as keys in the object.
        ...
    },
    "bytes_recv_per_msg" : {                (json object)
        "msg" : n                             (numeric) The total bytes received aggregated by message type
                                                When a message type is not listed in this json object, the bytes received are 0.
                                                Only known message types can appear as keys in the object and all bytes received
                                                of unknown message types are listed under '*other*'.
    }
    """

    # ------------------------------------------------------------------------------
    def __init__(self, peer_info: dict) -> None:
        # --------------------------------------------------------------------------
        """Initializes a Peer object with information pertaining to its IP address,
        port, network, and message logs.
        """

        self.debug = 1

        self.id = self.get_number_of_known_peers() + 1
        self.address = peer_info['address_from']
        self.address_local = peer_info['address_from']
        self.network = Utilities.is_valid_ip_address(
            peer_info['address_from'].split(':')[0])
        self.services = peer_info['services']
        self.version = peer_info['version']
        self.sub_version = peer_info['user_agent']
        self.timestamp = peer_info['timestamp']
        self.nonce = peer_info['nonce']
        self.start_account_count = peer_info['start_accounts_known']
        self.relay = peer_info['relay']

        host, port = peer_info['address_from'].split(':')

        if not self.is_peer_known(host, port):
            self.add_peer(peer_info=peer_info)
        else:
            print('Update existing peer"s information')

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

    @classmethod
    # ------------------------------------------------------------------------------
    def is_peer_known(self, host: str, port: str) -> bool:
        # --------------------------------------------------------------------------
        """"""

        known_peers = self.get_known_peers()
        peer_address = '{}:{}'.format(host, port)
        return peer_address in known_peers

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

    @classmethod
    # ------------------------------------------------------------------------------
    def add_peer(self, peer_info: dict) -> bool:
        # --------------------------------------------------------------------------
        """"""

        host, port = peer_info['address_from'].split(':')
        known_peer_data = self.get_known_peers()
        if not self.is_peer_known(host, port):
            with open('../known_peers.json', 'r+') as known_peers_file:
                known_peer_data.update({'{}:{}'.format(host, port): peer_info})
                known_peers_file.seek(0)
                known_peers_file.write(json.dumps(known_peer_data))
                known_peers_file.truncate()
            known_peers_file.close()
        else:
            self.init_peers_file(
                unknown_peers={'{}:{}'.format(host, port): self})

        return True

    @classmethod
    # ------------------------------------------------------------------------------
    def __debug(self, msg) -> None:
        # --------------------------------------------------------------------------
        """Prints a message to the screen with the name of the current thread"""

        # if self.debug:
        print("[%s] %s" % (str(threading.currentThread().getName()), msg))


# end Peer class
