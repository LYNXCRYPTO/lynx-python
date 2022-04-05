from os.path import exists
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
    def __init_known_peers(self, unknown_peers={}) -> None:
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

# end Utilities class
