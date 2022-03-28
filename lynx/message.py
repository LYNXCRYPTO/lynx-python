# message.py

from datetime import datetime
from msilib.schema import Class
from node import display_debug


class Message:
    """Unsigned transactions with information regarding a message's type, flag,
    data, and timestamp
    """

    # ------------------------------------------------------------------------------
    def __init__(self, message_type, flag, message_data) -> None:
        # --------------------------------------------------------------------------
        """Initializes a message object, does *not* check if information is None"""
        self.debug = 1

        self.message_type = message_type
        self.flag = flag
        self.message_data = message_data
        self.timestamp = str(datetime.now())

    # ------------------------------------------------------------------------------
    def __debug(self, message) -> None:
        # --------------------------------------------------------------------------
        if self.debug:
            display_debug(message)

    # ------------------------------------------------------------------------------
    def validate(self) -> bool:
        # --------------------------------------------------------------------------
        """Checks to see whether a message has a valid type, flag, data, and timestamp"""

        is_valid_message_type = isinstance(self.message_type, str)
        is_valid_flag = isinstance(self.flag, int)
        is_valid_message_data = isinstance(self.message_data, str)
        is_valid_timestamp = isinstance(self.timestamp, str)

        try:
            if not (is_valid_message_type and is_valid_flag and is_valid_message_data and is_valid_timestamp):
                raise ValueError
        except ValueError:
            if not is_valid_message_type:
                self.__debug('Invalid message type, with type of: %s' %
                             type(self.message_type))
            if not is_valid_flag:
                self.__debug('Invalid message flag, with type of: %s' %
                             type(self.flag))
            if not is_valid_message_data:
                self.__debug('Invalid message data, with type of: %s' %
                             type(self.message_data))
            if not is_valid_timestamp:
                self.__debug('Invalid message timestamp, with type of: %s' %
                             type(self.timestamp))
            return False

        self.__debug('Message is valid!')
        return True

# end Message class

#signMessage class

from account import Account

class SignedMessage:
    """
    Verifys and signs message content
    """
    # ------------------------------------------------------------------------------
    def __init__(self,message: Message,signature) -> None:
    # ------------------------------------------------------------------------------
        """
        Init message object
        """
        self.message = message
        self.signature = signature

    # ------------------------------------------------------------------------------
    def is_signed(self) -> bool:
    # ------------------------------------------------------------------------------
        """
        Returns if message is signed
        """
        return self.signature is not None

#end signMessage class
            
            
