from lynx.p2p.peer import Peer

def test_peer() -> None:
    peer_dict = {"address": "1234.1234.1234.12", "ipv4": True, "ipv6": False, "port": "6969", "last_send": "0", "last_recv": "0", "bytes_sent": "0", "bytes_recv": "0", "ping": "0", "starting_height": "0", "node_sync": False, "ban_score": "0"}

    peer = Peer(**peer_dict)

    print(peer.as_dict())

    print(peer.ipv4)
if __name__ == "__main__":
    test_peer()