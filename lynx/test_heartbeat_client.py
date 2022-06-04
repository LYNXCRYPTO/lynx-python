import argparse
from heartbeat import heartbeat

# Command Line Arguments
# host: target host to send PING
# port: target port to send PING

parser = argparse.ArgumentParser()
parser.add_argument('--host', type=str, required=True)
parser.add_argument('--port', type=int, required=True)
args = parser.parse_args()


def test_heartbeat():
    time = heartbeat(args.host, args.port)
    if time != -1:
        print("PONG received in ", time, "ms")
    else:
        print("Connection timeout, PONG not received within 2000 ms")



if __name__ == "__main__":
    test_heartbeat()
