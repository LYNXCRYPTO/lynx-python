# message.py

from datetime import datetime
import json
from multiprocessing.sharedctypes import Value
import threading
from hashlib import sha3_256


class Message:
    """Unsigned transactions with information regarding a message's type, flag,
    data, and timestamp.
    """

    # ------------------------------------------------------------------------------
    def __init__(self, type: str, flag: int, data) -> None:
        # --------------------------------------------------------------------------
        """Initializes a message object, does *not* check if information is None"""

        self.debug = 1

        self.type = type
        self.flag = flag
        self.data = data
        self.timestamp = str(datetime.now())

    # ------------------------------------------------------------------------------
    def __debug(self, message) -> None:
        # --------------------------------------------------------------------------
        """Prints a message to the screen with the name of the current thread"""
        if self.debug:
            print("[%s] %s" %
                  (str(threading.currentThread().getName()), message))

    # ------------------------------------------------------------------------------

    def validate(self) -> bool:
        # --------------------------------------------------------------------------
        """Checks to see whether a message has a valid type, flag, data, and timestamp"""

        is_valid_type = isinstance(self.type, str) and self.type in [
            'response', 'request']
        is_valid_flag = isinstance(self.flag, int) and 0 < self.flag < 100
        is_valid_data = isinstance(self.data, str)
        is_valid_timestamp = isinstance(self.timestamp, str)

        try:
            if not (is_valid_type and is_valid_flag and is_valid_data and is_valid_timestamp):
                raise ValueError
        except ValueError:
            if not is_valid_type:
                self.__debug('Invalid message type, with type of: %s' %
                             type(self.type))
            if not is_valid_flag:
                self.__debug('Invalid message flag, with type of: %s' %
                             type(self.flag))
            if not is_valid_data:
                self.__debug('Invalid message data, with type of: %s' %
                             type(self.data))
            if not is_valid_timestamp:
                self.__debug('Invalid message timestamp, with type of: %s' %
                             type(self.timestamp))
            return False

        self.__debug('Message is valid!')
        return True

    # ------------------------------------------------------------------------------
    def to_JSON(self) -> str:
        # --------------------------------------------------------------------------
        """Returns a serialized version of a Message object. This can be used with
        any function/method in which an encoded message is to be sent.
        """

        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

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

            message = Message(
                type=data['message']['type'], flag=data['message']['flag'], data=data['message']['data'])
            return message
        except ValueError:
            self.__debug('Message data is not a "dict".')
            return None
        except KeyError:
            self.__debug('Message is not formatted correctly.')
            return None
        except:
            self.__debug('Unable to convert data in Message object.')
            return None

# end Message class


class SignedMessage:
    """Manages any actions made with a signed message. Inherits attributes from
    the Message class.
    """

    # ------------------------------------------------------------------------------
    def __init__(self, message: Message, signature=None) -> None:
        # --------------------------------------------------------------------------
        """Initializes a the signature of a SignedMesage"""

        self.debug = 1

        self.message = message
        self.signature = signature

    # ------------------------------------------------------------------------------
    def __debug(self, message) -> None:
        # --------------------------------------------------------------------------
        if self.debug:
            print("[%s] %s" %
                  (str(threading.currentThread().getName()), message))

    # ------------------------------------------------------------------------------
    def is_signed(self) -> bool:
        # --------------------------------------------------------------------------

        return self.signature is not None

    # ------------------------------------------------------------------------------
    def to_JSON(self) -> str:
        # --------------------------------------------------------------------------
        """Returns a serialized version of a SignedMessage object. This can be used
        with any function/method in which an encoded message is to be sent.
        """

        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    @classmethod
    # ------------------------------------------------------------------------------
    def from_JSON(self, JSON: str):
        # --------------------------------------------------------------------------
        """"Returns a SignedMessage object given a JSON input. If JSON is not formatted 
        correctly, this method will return None.
        """

        try:
            data = json.loads(JSON)
            message = Message.from_JSON(JSON)
            if not isinstance(data, dict) or message is None:
                raise ValueError

            signed_message = SignedMessage(
                message=message, signature=data['signature'])
            return signed_message
        except ValueError:
            if not isinstance(data, dict):
                self.__debug('Message data is not a "dict".')
            return None
        except KeyError:
            self.__debug('Message is not formatted correctly.')
            return None
        except:
            self.__debug(
                'Unable to convert JSON data into SignedMessage object.')
            return None

# end SignedMessage class
