# message.py

from message import Message


class MessageValidation:

    @classmethod
    # ------------------------------------------------------------------------------
    def validate_version_request(self, message: Message) -> bool:
        # --------------------------------------------------------------------------
        """Checks to see if incoming version request message is formatted according
        to our standards so node can handle the request without errors.
        """
        message_keys = {'version': False, 'services': False, 'timestamp': False, 'nonce': False,
                        'address_from': False, 'address_receive': False, 'sub_version': False, 'start_accounts_count': False, 'relay': False}
        is_request_valid = True

        if message.type == 'request' and message.flag == 1 and isinstance(message.data, dict):
            for k in message.data:
                if k in message_keys:
                    del message_keys[k]
                else:
                    is_request_valid = False
                    break
            if is_request_valid and len(message_keys) > 0:
                is_request_valid = False

        return is_request_valid

    @classmethod
    # ------------------------------------------------------------------------------
    def validate_version_response(self, message: Message) -> bool:
        # --------------------------------------------------------------------------
        """Checks to see if incoming version reponse message is formatted according
        to our standards so node can handle the request without errors.
        """

        return message.type == 'response' and message.flag == 1 and message.data is None

    @classmethod
    # ------------------------------------------------------------------------------
    def validate_address_request(self, message: Message) -> bool:
        # --------------------------------------------------------------------------
        """Checks to see if incoming peer address request message is formatted according
        to our standards so node can handle the request without errors.
        """

        message_keys = {'address_count': False, 'address_list': False}
        is_request_valid = True

        if message.type == 'request' and message.flag == 2 and isinstance(message.data, dict):
            for k in message.data:
                if k in message_keys:
                    del message_keys[k]
                else:
                    is_request_valid = False
                    break
            if is_request_valid and len(message_keys) > 0:
                is_request_valid = False

        return is_request_valid

    @classmethod
    # ------------------------------------------------------------------------------
    def validate_address_response(self, message: Message) -> bool:
        # --------------------------------------------------------------------------
        """Checks to see if incoming peer address reponse message is formatted according
        to our standards so node can handle the request without errors.
        """

        message_keys = {'address_count': False, 'address_list': False}
        is_request_valid = True

        if message.type == 'response' and message.flag == 2 and isinstance(message.data, dict):
            for k in message.data:
                if k in message_keys:
                    del message_keys[k]
                else:
                    is_request_valid = False
                    break
            if is_request_valid and len(message_keys) > 0:
                is_request_valid = False

        return is_request_valid

    @classmethod
    # ------------------------------------------------------------------------------
    def validate_account_request(self, message: Message) -> bool:
        # --------------------------------------------------------------------------
        """Checks to see if incoming account request message is formatted according
        to our standards so node can handle the request without errors.
        """

        message_keys = {'version': False,
                        'account': False, 'best_state': False, }
        is_request_valid = True

        if message.type == 'request' and message.flag == 3 and isinstance(message.data, dict):
            for k in message.data:
                if k in message_keys:
                    del message_keys[k]
                else:
                    is_request_valid = False
                    break
            if is_request_valid and len(message_keys) > 0:
                is_request_valid = False

        return is_request_valid

    @classmethod
    # ------------------------------------------------------------------------------
    def validate_account_response(self, message: Message) -> bool:
        # --------------------------------------------------------------------------
        """Checks to see if incoming account reponse message is formatted according
        to our standards so node can handle the request without errors.
        """

        message_keys = {'version': False,
                        'account': False, 'best_state': False, }
        is_request_valid = True

        if message.type == 'response' and message.flag == 2 and isinstance(message.data, dict):
            for k in message.data:
                if k in message_keys:
                    del message_keys[k]
                else:
                    is_request_valid = False
                    break
            if is_request_valid and len(message_keys) > 0:
                is_request_valid = False

        return is_request_valid

# end MessageValidation class
