

class EpochContext:

    def __init__(self, start: int, slot_num: int, size: int = 100, slot_size: int = 10):

        self.start = start
        self.size = size
        self.end = start + size
        self.slot_num = slot_num
        self.slot_size = slot_size
