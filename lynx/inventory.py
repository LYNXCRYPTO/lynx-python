from typing import Callable
from peer import Peer


class InventoryItem:

    # ------------------------------------------------------------------------------
    def __init__(self, type: str, account: str = None, data: str = None) -> None:
        # --------------------------------------------------------------------------
        """Initializes an Inventory object"""

        self.type = type
        self.account = account
        self.data = data


class Inventory:

    # ------------------------------------------------------------------------------
    def __init__(self, inventory: list = [], on_extension: Callable[[int], None] = lambda: None) -> None:
        # --------------------------------------------------------------------------
        """Initializes an Inventory object"""

        self.inventory = inventory
        self.on_extension = on_extension

    # ------------------------------------------------------------------------------
    def __len__(self) -> int:
        # --------------------------------------------------------------------------
        """"""

        return len(self.inventory)

    # ------------------------------------------------------------------------------
    def append(self, new_inventory: InventoryItem) -> bool:
        # --------------------------------------------------------------------------
        """"""

        if new_inventory is not None and len(new_inventory) > 0:
            self.inventory.append(new_inventory)
            return True
        return False

    # ------------------------------------------------------------------------------
    def extend(self, new_inventory: list) -> bool:
        # --------------------------------------------------------------------------
        """"""

        if new_inventory is not None and len(new_inventory) > 0:
            self.inventory.extend(new_inventory)
            self.on_extension(4)
            return True
        return False

    # ------------------------------------------------------------------------------
    def get_batch(self, amount: int = 0) -> list:
        # --------------------------------------------------------------------------
        """"""

        inventory_batch = []

        if len(self.inventory) > 0:
            if len(self.inventory) >= amount:
                inventory_batch.extend(self.inventory[0:amount])
                del self.inventory[0:amount]
            else:
                inventory_batch.extend(self.inventory[0:])
                self.inventory.clear()

        return inventory_batch
