from node import Node
from server import Server
from inventory import Inventory


def test_inventory():
    server = Server(nonce='12345')
    starting_inventory = [1, 2, 3, 4, 5]
    additive_inventory = [6, 7, 8, 9, 10]
    inventory = Inventory(inventory=starting_inventory,
                          on_extension=server.send_all_peers_request)
    print('INVENTORY')
    print('Inventory Before: {}'.format(starting_inventory))
    inventory.extend(additive_inventory)
    print('Inventory After: {}'.format(inventory.inventory))
    print('\nBatch Of 5: {}'.format(inventory.get_batch(5)))
    print('Batch Of 3: {}'.format(inventory.get_batch(3)))
    print('Only {} items are left in the inventory:\n{}'.format(
        len(inventory), inventory.inventory))


if __name__ == "__main__":
    test_inventory()
