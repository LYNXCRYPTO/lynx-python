# message.py
from enum import Enum
from datetime import datetime
import json

class MessageType(Enum):
    """Enum for the different types of storage within the client's freezer"""

    REQUEST = 'request'
    RESPONSE = 'response'


class MessageFlag(Enum):
    HEARTBEAT = 1
    VERSION = 2


class Message:
    """Unsigned transactions with information regarding a message's type, flag,
    data, and timestamp.
    """

    def __init__(self, type: MessageType, flag: int, data) -> None:
        """Initializes a message object, does *not* check if information is None"""
        self.type = type
        self.flag = flag
        self.data = data
        self.timestamp = str(datetime.now())


    def validate(self) -> bool:
        """Checks to see whether a message has a valid type, flag, data, and timestamp"""

        is_valid_type = isinstance(self.type, MessageType) and self.type in [MessageType.REQUEST, MessageType.RESPONSE]
        is_valid_flag = isinstance(self.flag, int) and 0 < self.flag < 100
        is_valid_data = isinstance(self.data, dict)
        is_valid_timestamp = isinstance(self.timestamp, str)

        try:
            if not (is_valid_type and is_valid_flag and is_valid_timestamp):
                raise ValueError
        except ValueError:
            if not is_valid_type:
                print(f'Invalid message type, with type of {type(self.type)}')
            if not is_valid_flag:
                print(f'Invalid message flag, with type of: {type(self.flag)}')
            if not is_valid_data:
                print(f'Invalid message data, with type of: {type(self.data)}')
            if not is_valid_timestamp:
                print(f'Invalid message timestamp, with type of: {type(self.timestamp)}')
            return False

        return True


    def to_JSON(self) -> str:
        """Returns a serialized version of a Message object. This can be used with
        any function/method in which an encoded message is to be sent.
        """

        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True)


    @classmethod
    def from_JSON(self, JSON: str):

        """"Returns a Message object given a JSON input. If JSON is not formatted 
        correctly, this method will return None.
        """

        try:
            data = json.loads(JSON)
            if not isinstance(data, dict):
                raise ValueError

            message = Message(
                type=data['type'], flag=data['flag'], data=data['data'])
            return message
        except ValueError:
            print(self=self, message='Message data is not a "dict".')
            return None
        except KeyError:
            print(self=self, message='Message is not formatted correctly.')
            return None
        except:
            print(self=self, message='Unable to convert data in Message object.')
            return None

# end Message class

