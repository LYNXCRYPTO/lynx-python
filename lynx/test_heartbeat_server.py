import argparse
import socket
import time

# Command Line Arguemnts
# host: this server's host
# port: this server's property
# msg: message to send to client (optional, defaults to 'PONG')
# wait: time in seconds to wait before sending response (optional,
#                                                        defaults to 0)

parser = argparse.ArgumentParser()
parser.add_argument('--host', type=str, required=True)
parser.add_argument('--port', type=int, required=True)
parser.add_argument('--msg', type=str)
parser.add_argument('--wait', type=float)
args = parser.parse_args()

def test_heartbeat_server():
    wait = 0
    if args.wait:
        wait = args.wait
    response_str = 'PONG'
    if args.msg:
        response_str = args.msg

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((args.host, args.port))
        sock.settimeout(1)
        while True:
            try:
                msg_bytes, sender_addr = sock.recvfrom(1024)
            except socket.timeout:
                continue
            msg_str = msg_bytes.decode('utf-8')
            if msg_str == 'PING':
                print("SERVER received:", msg_str)
                print("SERVER sending:", response_str)
                response = response_str.encode('utf-8')
                time.sleep(wait)
                sock.sendto(response, sender_addr)
            else:
                continue

if __name__ == "__main__":
    test_heartbeat_server()
