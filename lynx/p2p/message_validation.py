from eth_typing import BlockNumber, Hash32
from curses.ascii import isdigit
from typing import List, Dict, Tuple
from lynx.p2p.message import Message, MessageType, MessageFlag


class MessageValidation:

    # Requests
    VERSION_REQUEST_FIELDS = {'version': str, 'address': str, 'port': str}
    TRANSACTION_REQUEST_FIELDS = {'nonce': int, 'gas_price': int, 'gas': int, 'to': bytes, 'value': int, 'data': bytes, 'v': int, 'r': int, 's': int}
    BLOCK_REQUEST_FIELDS = {'best_block': int}
    QUERY_REQUEST_FIELDS = {'block_number': BlockNumber}

    # Responses
    VERSION_RESPONSE_FIELDS = {'version': str, 'address': str, 'port': str}
    ADDRESS_RESPONSE_FIELDS = {'peers': list}
    BLOCK_RESPONSE_FIELDS = {'blocks': list}
    QUERY_RESPONSE_FIELDS = {'block_hash': Hash32}


    @classmethod
    def __validate_fields(cls, data: dict, fields: dict) -> bool:
        """
        """

        assert(isinstance(data, dict))
        assert(isinstance(fields, dict))
        assert(len(data) == len(fields))

        is_valid = True

        for key in fields:
            if key not in data or not isinstance(data[key], fields[key]):
                is_valid = False
                break

        if not is_valid:
            return False

        return True


    @classmethod
    def validate_message(cls, message: Message) -> bool:
        """
        """

        if message.type is MessageType.REQUEST:
            if message.flag is MessageFlag.VERSION:
                return cls.__validate_fields(message.data, cls.VERSION_REQUEST_FIELDS)
            elif message.flag is MessageFlag.ADDRESS:
                return True # No data validation necessary
            elif message.flag is MessageFlag.TRANSACTION:
                return cls.__validate_fields(message.data, cls.TRANSACTION_REQUEST_FIELDS)
            elif message.flag is MessageFlag.BLOCK:
                return cls.__validate_fields(message.data, cls.BLOCK_REQUEST_FIELDS)
            elif message.flag is MessageFlag.CAMPAIGN:
                return True # No data validation necessary
            elif message.flag is MessageFlag.QUERY:
                return cls.__validate_fields(message.data, cls.QUERY_REQUEST_FIELDS)
            elif message.flag is MessageFlag.HEARTBEAT:
                return True # No data validation necessary

        elif message.type is MessageType.RESPONSE:
            if message.flag is MessageFlag.VERSION:
                return cls.__validate_fields(message.data, cls.VERSION_RESPONSE_FIELDS)
            elif message.flag is MessageFlag.ADDRESS:
                return cls.__validate_fields(message.data, cls.ADDRESS_RESPONSE_FIELDS)
            elif message.flag is MessageFlag.TRANSACTION:
                return True # No data validation necessary
            elif message.flag is MessageFlag.BLOCK:
                return cls.__validate_fields(message.data, cls.BLOCK_RESPONSE_FIELDS)
            elif message.flag is MessageFlag.CAMPAIGN:
                return True # No data validation necessary
            elif message.flag is MessageFlag.QUERY:
                return True # No data validation necessary
            elif message.flag is MessageFlag.HEARTBEAT:
                return True # No data validation necessary

        return False