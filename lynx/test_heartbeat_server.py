import socket


def test_heartbeat_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("localhost", 8001))
        sock.settimeout(1)
        while True:
            try:
                msg_bytes, sender_addr = sock.recvfrom(1024)
            except socket.timeout:
                continue
            msg_str = msg_bytes.decode('utf-8')
            if msg_str == 'PING':
                response = 'PONG'.encode('utf-8')
                sock.sendto(response, sender_addr)
            else:
                continue

if __name__ == "__main__":
    test_heartbeat_server()
