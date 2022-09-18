from __future__ import annotations
from typing import TYPE_CHECKING
import time
from typing import Tuple
from lynx.p2p.message import MessageFlag
from lynx.constants import BOOTSTRAP_PEERS
if TYPE_CHECKING:
    from lynx.p2p.node import Node
    from lynx.p2p.peer import Peer


class Bootstrap:

    @classmethod
    def from_seeds(cls, node: Node) -> None:
        """"""

        node.broadcast(flag=MessageFlag.VERSION, peers=BOOTSTRAP_PEERS)
        cls.__start_bootstrap_timeout(node)

        if not node.max_peers_reached() and len(node.peers) > 0:
            node.broadcast(flag=MessageFlag.ADDRESS)
            cls.__start_bootstrap_timeout(node)


    @classmethod 
    def from_peers(cls, node: Node, peers: Tuple[Peer]) -> None:
        """"""

        node.broadcast(flag=MessageFlag.VERSION, peers=peers)
        cls.__start_bootstrap_timeout(node)

        if not node.max_peers_reached() and len(node.peers) > 0:
            node.broadcast(flag=MessageFlag.ADDRESS)
            cls.__start_bootstrap_timeout(node)        

    
    @classmethod 
    def __start_bootstrap_timeout(cls, node: Node, timeout: int = 5) -> None:
        """"""

        start_time = time.time()
        while not node.max_peers_reached() and (time.time() - start_time) <= timeout:
            time.sleep(3)

