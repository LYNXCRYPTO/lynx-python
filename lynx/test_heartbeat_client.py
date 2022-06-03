from heartbeat import heartbeat


def test_heartbeat():
    time = heartbeat()
    if time != -1:
        print("PONG received in ", time, "ms")
    else:
        print("Connection timeout, PONG not received within 2000 ms")



if __name__ == "__main__":
    test_heartbeat()
