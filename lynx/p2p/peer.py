from eth.rlp.sedes import (uint256)

class Peer:
    fields = [
        ('address', str), 
        ('ipv4', bool), 
        ('ipv6', bool), 
        ('port', str), 
        ('version', str),
        ("last_send", uint256), 
        ("last_recv", uint256), 
        ("bytes_sent", uint256), 
        ("bytes_recv", uint256), 
        ("ping", uint256), 
        ("last_alive", uint256),
        ("starting_height", uint256), 
        ("node_sync", bool), 
        ("ban_score", uint256),
    ]


    def __init__(self, **kwargs) -> None:
        """Initializes a Peer object with information pertaining to its IP address,
        port, network, and message logs.
        """

        for key, value in kwargs.items():
            for k in self.fields:
                if key == k[0]:
                    setattr(self, key, value)


    def __getattribute__(self, name):
        return object.__getattribute__(self, name)


    def as_dict(self) -> dict:
        return self.__dict__

    
    def __str__(self) -> str:
        return f'<Peer ({self.address}:{self.port})>'

# end Peer class
