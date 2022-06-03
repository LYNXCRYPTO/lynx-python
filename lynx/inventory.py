
class Inventory:

    # ------------------------------------------------------------------------------
    def __init__(self, inventory: list = [], on_extension=lambda: None) -> None:
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
    def extend(self, new_inventory: list) -> bool:
        # --------------------------------------------------------------------------
        """"""

        if new_inventory is not None and len(new_inventory) > 0:
            self.inventory.extend(new_inventory)
            self.on_extension()
            return True
        return False
