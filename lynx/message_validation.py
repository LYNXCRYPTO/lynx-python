# message.py
from eth_typing import BlockNumber
from curses.ascii import isdigit
from typing import List, Dict, Tuple
from lynx.p2p.message import Message, MessageType, MessageFlag


class MessageValidation:

    @classmethod
    def __validate_fields(cls, data: dict, fields: dict) -> bool:
        """"""

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
    def validate_version_request(cls, message: Message) -> bool:
        """Checks to see if incoming version request message is formatted according
        to our standards so node can handle the request without errors.
        """
        fields = {'version': str, 'address': str, 'port': str}

        is_type_valid : bool = message.type is MessageType.REQUEST
        is_flag_valid : bool = message.flag is MessageFlag.VERSION
        is_data_valid : bool = cls.__validate_fields(message.data, fields)

        return is_type_valid and is_flag_valid and is_data_valid


    @classmethod
    def validate_version_response(cls, message: Message) -> bool:
        """Checks to see if incoming version reponse message is formatted according
        to our standards so node can handle the request without errors.
        """

        fields = {'version': str, 'address': str, 'port': str}

        is_type_valid : bool = message.type is MessageType.RESPONSE
        is_flag_valid : bool = message.flag is MessageFlag.VERSION
        is_data_valid : bool = cls.__validate_fields(message.data, fields)

        return is_type_valid and is_flag_valid and is_data_valid


    @classmethod
    def validate_transaction_request(cls, message: Message) -> bool:
        """"""

        fields = {'nonce': int, 
                    'gas_price': int, 
                    'gas': int, 
                    "to": bytes, 
                    "value": int, 
                    "data": bytes,
                    "v": int, 
                    "r": int, 
                    "s": int}
                        
        is_type_valid : bool = message.type is MessageType.RESPONSE
        is_flag_valid : bool = message.flag is MessageFlag.TRANSACTION
        is_data_valid : bool = cls.__validate_fields(message.data, fields)

        return is_type_valid and is_flag_valid and is_data_valid


    @classmethod
    def validate_address_response(cls, message: Message) -> bool:
        """"""

        fields = {'peers': List[dict]}

        is_type_valid : bool = message.type is MessageType.RESPONSE
        is_flag_valid : bool = message.flag is MessageFlag.ADDRESS
        is_data_valid : bool = cls.__validate_fields(message.data, fields)

        return is_type_valid and is_flag_valid and is_data_valid

    
    @classmethod
    def validate_block_request(cls, message: Message) -> bool:
        """"""
        
        fields = {'header': dict, 'transactions': list}

        is_type_valid : bool = message.type is MessageType.REQUEST
        is_flag_valid : bool = message.flag is MessageFlag.BLOCK
        is_data_valid : bool = cls.__validate_fields(message.data, fields)

        return is_type_valid and is_flag_valid and is_data_valid

    @classmethod
    def validate_campaign_request(cls, message: Message) -> bool:
        """"""

        is_type_valid : bool = message.type is MessageType.REQUEST
        is_flag_valid : bool = message.flag is MessageFlag.CAMPAIGN
        is_data_valid : bool = True

        for key, value in message.data.items():
            if isinstance(key, int) or not isinstance(value, dict):
                is_data_valid = False

        return is_type_valid and is_flag_valid and is_data_valid


# end MessageValidation class
