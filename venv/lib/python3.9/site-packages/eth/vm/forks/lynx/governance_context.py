class GovernanceContext:
    _slot_size = None
    _epoch_size = None
    
    def __init__(self, slot_size: int = 10, epoch_size: int = 10):
        self._slot_size = slot_size
        self._epoch_size = epoch_size

    @property
    def slot_size(self) -> int:
        return self._slot_size

    @property
    def epoch_size(self) -> int:
        return self._epoch_size