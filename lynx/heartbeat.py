import socket
import threading
import time


# Currently using placeholder address 'localhost 8001'
def heartbeat(host='localhost', port=8001) -> None:
    # UDP socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        addr = (host, port)
        signals = {
            'start_time': None,
            'time_left': 2.0,
            'wake_sender': threading.Event(),
            'wake_listener': threading.Event(),
            'shutdown': False
        }
        ping_thread = threading.Thread(target=send_ping,
                                       args=(sock, addr, signals,))

        # Start PING sender thread
        ping_thread.start()
        # Wait until PING sender thread has sent
        signals['wake_listener'].wait()
        # PONG listener
        while True:
            try:
                response_bytes, server = sock.recvfrom(1024)
                end_time = time.time()
                response_str = response_bytes.decode('utf-8')
                print("CLIENT received:", response_str)
                if response_str == 'PONG':
                    print("RECEIVED PONG in", int((end_time - signals['start_time']) * 1000), "ms")
                    # Wait until sender wakes up
                    signals['wake_listener'].clear()
                    signals['wake_listener'].wait()
                    continue

                else:
                    # Update timeout
                    signals['time_left'] -= end_time - signals['start_time']
                    if signals['time_left'] <= 0:
                        raise socket.timeout
                    sock.settimeout(signals['time_left'])
                    print("CLIENT continue listening...")
                    # Continue listening if 'PONG' not received
                    continue
            except socket.timeout:
                end_time = time.time()
                signals['shutdown'] = True
                print("PONG Timeout")
                print("TIME ELAPSED:", int((end_time - signals['start_time']) * 1000), "ms")
                # Interrupt sender wait on timeout
                signals['wake_sender'].set()
                # Join ping sender thread before exit
                ping_thread.join()
                break



def send_ping(sock, addr, signals) -> None:
    while not signals['shutdown']:
        signals['start_time'] = time.time()
        # Set socket timeout to 2 seconds
        signals['time_left'] = 2.0
        sock.settimeout(signals['time_left'])
        # Wake the listener
        signals['wake_listener'].set()
        print("CLIENT sending PING")

        sock.sendto('PING'.encode('utf-8'), addr)

        # Wait 20 seconds to send again
        signals['wake_sender'].clear()
        signals['wake_sender'].wait(20.0)
