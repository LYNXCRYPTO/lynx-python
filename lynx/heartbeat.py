import socket
import time

# Return -1 if connection timeout
# Currently using placeholder address 'localhost 8001'
def heartbeat(host='localhost', port=8001) -> int:
    # UDP socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        msg_str = 'PING'
        addr = (host, port)
        # Set timeout to 2 seconds
        sock.settimeout(2.0)
        start = time.time()
        sock.sendto(msg_str.encode('utf-8'), addr)

        # Exist loop if exceeds 2 seconds to prevent re-blocking of sock.recv()
        # in case something other than 'PONG' is received
        while time.time() - start <= 2.0:
            try:
                response_byte = sock.recv(1024)
                end = time.time()
                response_str = response_byte.decode('utf-8')
                if response_str == 'PONG':
                    # Return time elapsed in milliseconds
                    return int(end - start) * 1000
                else:
                    # Continue listening if 'PONG' not received
                    continue
            except socket.timeout:
                return -1
        return -1
