

class EpochContext:

    def __init__(self, start: int, slot: int, size: int, slot_size: int):
        """Initializes an object dedicated to providing information about an epoch.
        An epoch is time period in which a predetermined event or actions should take
        place. In regards to Lynx, an EpochContext object provides information about
        an epoch's initial block number (start), current slot number (slot), number
        of slots (size), and the number of block's within each slot (slot_size).
        """

        self.start = start
        self.size = size
        self.end = start + (size * slot_size)
        self.slot = slot
        self.slot_size = slot_size


    @property
    def next_epoch(self) -> 'EpochContext':
        """A property of an EpochContext object that returns the context of the next
        epoch.
        """

        if self.start == 0:
            return EpochContext(1, 1, self.size, self.slot_size)

        return EpochContext(self.end + 1, 1, self.size, self.slot_size)