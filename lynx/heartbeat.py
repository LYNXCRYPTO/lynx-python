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
        print("CLIENT sending: PING")
        sock.sendto(msg_str.encode('utf-8'), addr)

        while True:
            try:
                response_bytes, server = sock.recvfrom(1024)
                end = time.time()
                response_str = response_bytes.decode('utf-8')
                print("CLIENT received:", response_str)
                if response_str == 'PONG':
                    # Return time elapsed in milliseconds
                    return int((end - start) * 1000)
                else:
                    # Update timeout
                    sock.settimeout(2.0 - (time.time() - start))
                    print("CLIENT continue listening...")
                    # Continue listening if 'PONG' not received
                    continue
            except socket.timeout:
                print("PONG Timeout")
                print("TIME ELAPSED:", int((time.time() - start) * 1000), "ms")
                break
        return -1
