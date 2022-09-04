# message.py
from enum import Enum
from datetime import datetime
import json

class MessageType(Enum):
    """Enum for the different types of storage within the client's freezer"""

    REQUEST = 'REQUEST'
    RESPONSE = 'RESPONSE'


class MessageFlag(Enum):
    HEARTBEAT = 1
    VERSION = 2
    TRANSACTION = 3

    @classmethod
    def from_int(cls, i: int) -> 'MessageFlag':
        for flag in MessageFlag:
            if flag.value == i:
                return flag

        raise ValueError(f'No MessageFlag with value of {i} exists')


class Message:
    """Unsigned transactions with information regarding a message's type, flag,
    data, and timestamp.
    """

    def __init__(self, type: MessageType, flag: MessageFlag, data) -> None:
        """Initializes a message object, does *not* check if information is None"""
        self.type = type
        self.flag = flag
        self.data = data
        self.timestamp = str(datetime.now())


    def validate(self) -> bool:
        """Checks to see whether a message has a valid type, flag, data, and timestamp"""

        is_valid_type = isinstance(self.type, MessageType) and self.type.value in ['REQUEST', 'RESPONSE']
        is_valid_flag = isinstance(self.flag, MessageFlag) and 0 < self.flag.value < 100
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
        try:
            m = {"type": self.type.value, "flag": self.flag.value, "data": self.data, "timestamp": self.timestamp}

            return json.dumps(m)
        except Exception as e:
            print(e)
            return None


    @classmethod
    def from_JSON(self, JSON: str):

        """"Returns a Message object given a JSON input. If JSON is not formatted 
        correctly, this method will return None.
        """

        try:
            data = json.loads(JSON)
            if not isinstance(data, dict):
                raise ValueError
            message_type = MessageType.REQUEST if data['type'] == MessageType.REQUEST.value else MessageType.RESPONSE
            message_flag = MessageFlag.from_int(data['flag'])
            message = Message(type=message_type, flag=message_flag, data=data['data'])
            return message
        except ValueError:
            print('Message data is not a "dict".')
            return None
        except KeyError:
            print('Message is not formatted correctly.')
            return None
        except Exception as e:
            print(e)
            print('Unable to convert data in Message object.')
            return None

# end Message class

