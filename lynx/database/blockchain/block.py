
class Block:
    """A blueprint for a Block object which represents the link between data
    in the blockchain. Each block contains a unique id (mix_hash), a reference
    to its parent's hash, and data field containing transactional information
    and other relevant information."""

    def __init__(self, block_number, mix_hash, parent_hash):
        self.block_number = block_number
        self.mix_hash = mix_hash
        self.parent_hash = parent_hash
        self.transactions = []
