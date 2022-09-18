from lynx.p2p.message import Message
import socket
import traceback


class PeerConnection:

    def __init__(self, host: str, port: str, sock:socket.socket=None, peer_id:str=None) -> None:
        """Any exceptions thrown upwards"""

        self.id = peer_id
        self.host = host
        self.port = port

        if sock is None:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, int(port)))
        else:
            self.socket = sock


    def __make_message(self, message_type, message_flag, message_data) -> Message:
        """Packs the message into a Message object and then signs it using the 
        provided Account object.

        For more information about packing visit: https://docs.python.org/3/library/struct.html
        """

        message = Message(type=message_type, flag=message_flag, data=message_data)
        return message


    def send_data(self, message_type: str, message_flag: int, message_data: dict = None) -> bool:
        """Send a message through a peer connection. Returns True on success or 
        False if there was an error.
        """

        try:
            host, port = self.socket.getpeername()

            message = self.__make_message(message_type, message_flag, message_data)
            message_JSON = message.to_JSON()
            message_binary = message_JSON.encode()
            self.socket.send(message_binary)
            print(f'Sent ({host}:{port}) a Message!')
            print(f'Message Information:\n\tType: {message_type}\n\tFlag: {message_flag}\n\tData: {message_data}\n')

        except Exception as e:
            print(e)
            print(f'Unable to send data: {message_data}')
            return False
        return True


    def receive_data(self) -> Message:
        """Receive a message from a peer connection. Returns an None if there was 
        any error.
        """

        message_JSON = self.socket.recv(4096).decode()
        if message_JSON and len(message_JSON) > 0:
            message = Message.from_JSON(message_JSON)
            return message

        return None


    def close(self) -> None:
        """Close the peer connection. The send and receive methods will not work
        after this call.
        """

        self.socket.close()
        self.socket = None


    def is_open(self) -> bool:
        """"""

        try:
            self.socket.send("lynx")
            return True

        except: 
            return False


    def is_closed(self) -> bool:
        """"""

        return not self.is_open()


    def reconnect(self) -> None:
        """"""
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, int(self.port)))
            

    def __str__(self) -> str:
        """"""

        return "|%s|" & id

# end PeerConnection class
