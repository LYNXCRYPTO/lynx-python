

from multiprocessing.sharedctypes import Value


class Epoch:

    def __init__(self, start: int, slot_num: int, slot_length: int = 10):

        self.start = start
        self.end = start + (slot_num * slot_length)
        self.slot_num = slot_num
        self.slot_length = slot_length
