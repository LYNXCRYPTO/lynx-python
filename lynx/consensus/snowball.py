from typing import Dict, List
from eth_typing import BlockNumber, Hash32
from eth.vm.forks.lynx.blocks import LynxBlockHeader


class SnowballDecision:
    """"""

    def init(self, header : LynxBlockHeader, chit : bool = False, confidence : int = 0, consecutive_successes : int = 0) -> None:
        """
        Initializes a SnowballDecision object which is responsible determining the status and finality
        of a block. Each decision contains information regarding the block's header (header), a 
        boolean representing if a majority response was received for the block when the network was
        queried (chit), a integer representing the sum of chits for the current block being decided
        upon and its ancestors (confidence), and an integer representing the number of consecutive
        times a block and its ancestors received a majority response (consecutive_successes).
        """

        self.block_header : LynxBlockHeader = header
        self.chit : bool = chit
        self.confidence : int = confidence
        self.consecutive_successess : int = consecutive_successes


    def increment_confidence(self) -> None:
        """
        Increments the confidence counter by 1
        """

        self.confidence += 1

    
    def decrement_confidence(self) -> None:
        """
        Decrements the confidence counter by 1
        """

        self.confidence -= 1


    def increment_consecutive_successes(self) -> None:
        """
        Increments the consecutive successes counter by 1
        """

        self.consecutive_successess += 1


    def decrement_consecutive_successes(self) -> None:
        """
        Decrements the consecutive successes counter by 1
        """

        self.consecutive_successess -= 1


class SnowballConsensus:
    """
    A consensus algorithm used to check for the largest
    random number produced by a validator during block
    leader scheduling.
    """

    def init(self) -> None:
        """
        Initializes an instance of the SnowballConsensus engine which includes
        a information relating to undecided blocks and the decision of their blocks.
        """

        self.undecided_blocks : Dict[BlockNumber, List[Hash32]] = {}
        self.decisions : Dict[Hash32, SnowballDecision] = {}


    def add_block(self, block_header : LynxBlockHeader) -> bool:
        """
        Adds an undecided block header into the Snowball Consensus Engine and
        stages the block for querying. 
        """

        if block_header.hash not in self.decisions:
            decision = SnowballDecision(block_header)
            self.decisions[block_header.hash] = decision

            if block_header.block_number in self.undecided_blocks:
                self.undecided_blocks[block_header.block_number].append(block_header.hash)
            else:
                self.undecided_blocks[block_header.block_number] = [block_header.hash]

            return True
        
        return False


    def remove_block(self, block_hash : Hash32) -> bool:
        """
        Removes an undecided block header from the Snowball Consensus Engine. Usually,
        blocks are removed because the network has decided that the block was incorrect
        and shouldn't be included in the finalized blockchain.
        """

        try:
            block_number : int = self.decisions[block_hash].block_header.block_number

            del self.decisions[block_hash]
            self.undecided_blocks[block_number].remove(block_hash)

            return True

        except KeyError:
            return False
            
        except ValueError:
            return False


    def update_chit(self, block_hash : Hash32, chit : bool) -> bool:
        """
        Updates the chit to the boolean value provided (chit) given the block's
        hash. If the hash's corresponding block does not exist, then this function
        will return False.
        """

        if block_hash in self.decisions:
            self.decisions[block_hash].chit = chit
            return True

        return False


    def increment_confidence(self, block_hash : Hash32) -> bool:
        """
        Increments the confidence of a block given the its
        hash. If the hash's corresponding block does not exist, then this function
        will return False.
        """

        if block_hash in self.decisions:
            self.decisions[block_hash].increment_confidence()
            return True
            
        return False

    
    def decrement_confidence(self, block_hash : Hash32) -> bool:
        """
        Decrements the confidence of a block given the its
        hash. If the hash's corresponding block does not exist, then this function
        will return False.
        """

        if block_hash in self.decisions:
            self.decisions[block_hash].decrement_confidence()
            return True
            
        return False


    def increment_consecutive_successes(self, block_hash : Hash32) -> bool:
        """
        Increments the consecutive successes counter of a block given the its
        hash. If the hash's corresponding block does not exist, then this function
        will return False.
        """

        if block_hash in self.decisions:
            self.decisions[block_hash].increment_consecutive_successes()
            return True
            
        return False

    
    def decrement_consecutive_successes(self, block_hash : Hash32) -> bool:
        """
        Decrements the consecutive successes counter of a block given the its
        hash. If the hash's corresponding block does not exist, then this function
        will return False.
        """

        if block_hash in self.decisions:
            self.decisions[block_hash].decrement_consecutive_successes()
            return True
            
        return False