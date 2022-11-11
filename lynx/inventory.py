from typing import Callable


class Inventory:

    # ------------------------------------------------------------------------------
    def __init__(self, inventory: list = None, on_extension: Callable[[int], None] = lambda: None, flag: int = 0) -> None:
        # --------------------------------------------------------------------------
        """Initializes an Inventory object"""

        if inventory is None:
            self.inventory = []
        else:
            self.inventory = inventory
        self.on_extension = on_extension
        self.flag = flag

    # ------------------------------------------------------------------------------
    def __len__(self) -> int:
        # --------------------------------------------------------------------------
        """"""

        return len(self.inventory)

    # ------------------------------------------------------------------------------
    def append(self, new_inventory) -> bool:
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
            self.on_extension(self.flag)
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
