
from node.node import Node


def main():
    node = Node(max_peers=12, server_port="6969",
                node_id="12345", server_host="127.0.0.1")
    node.start_server_listen()


if __name__ == "__main__":
    main()
