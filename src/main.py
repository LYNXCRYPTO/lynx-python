
from node.node import Node


def hello(peer_connection, message_data):
    print(message_data)


def main():
    node = Node(max_peers=12, server_port="6969",
                node_id="12345", server_host="10.0.0.59")
    node.add_handler(message_type="HELL", handler=hello)
    node.start_server_listen()


if __name__ == "__main__":
    main()
