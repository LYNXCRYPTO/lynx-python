# message.py

from lynx.p2p.message import Message


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
    def validate_accounts_request(self, message: Message) -> bool:
        # --------------------------------------------------------------------------
        """Checks to see if incoming accounts request message is formatted according
        to our standards so node can handle the request without errors.
        """

        message_keys = {'count': False, 'inventory': False, }
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
    def validate_accounts_response(self, message: Message) -> bool:
        # --------------------------------------------------------------------------
        """Checks to see if incoming accounts response message is formatted according
        to our standards so node can handle the request without errors.
        """

        message_keys = {'count': False, 'inventory': False, }
        is_request_valid = True

        if message.type == 'response' and message.flag == 3 and isinstance(message.data, dict):
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
    def validate_states_request(self, message: Message) -> bool:
        # --------------------------------------------------------------------------
        """Checks to see if incoming states request message is formatted according
        to our standards so node can handle the request without errors.
        """

        message_keys = {'version': False,
                        'account': False, 'best_state': False, }
        is_request_valid = True

        if message.type == 'request' and message.flag == 4 and isinstance(message.data, dict):
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
    def validate_states_response(self, message: Message) -> bool:
        # --------------------------------------------------------------------------
        """Checks to see if incoming states response message is formatted according
        to our standards so node can handle the request without errors.
        """

        message_keys = {'count': False, 'inventory': False, }
        is_request_valid = True

        if message.type == 'response' and message.flag == 4 and isinstance(message.data, dict):
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
    def validate_data_request(self, message: Message) -> bool:
        # --------------------------------------------------------------------------
        """Checks to see if incoming data request message is formatted according
        to our standards so node can handle the request without errors.
        """

        message_keys = {'count': False, 'inventory': False}
        is_request_valid = True

        if message.type == 'request' and message.flag == 5 and isinstance(message.data, dict):
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
    def validate_data_response(self, message: Message) -> bool:
        # --------------------------------------------------------------------------
        """Checks to see if incoming data response message is formatted according
        to our standards so node can handle the request without errors.
        """

        message_keys = {'count': False, 'inventory': False}
        is_request_valid = True

        if message.type == 'response' and message.flag == 5 and isinstance(message.data, dict):
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
