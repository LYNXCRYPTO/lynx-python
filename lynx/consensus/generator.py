from __future__ import annotations
from typing import TYPE_CHECKING
import threading
from eth.vm.forks.lynx.blocks import LynxBlockHeader
from lynx.consensus.epoch_context import EpochContext
from lynx.p2p.message import MessageFlag
if TYPE_CHECKING:
    from lynx.p2p.node import Node


class Generator:

    def __init__(self, node: Node, epoch: EpochContext) -> None:
        """
        Initializes a object used to handle the flow of network operations
        on the Lynx Network. Given information regarding the blockchain's
        current epoch, a Generator object is able to manage timeouts for
        leader schedule generation and block proposals.
        """
        
        self.node : Node = node
        self.epoch : EpochContext = epoch
        # self.generator_lock = threading.Lock()

        self.is_campaigning : bool = False


    def start_generator(self, q) -> None:
        """
        Entry point for starting a generator. Given the epoch context of the
        current block, timeouts relating to generating leader schedules and 
        proposing blocks are automatically started. An information queue is provided
        to help communicate with different processes.
        """

        current_head : LynxBlockHeader = self.node.blockchain.get_canonical_head()

        leader_threshold : int = ((self.epoch.size * 3) // 4) + self.epoch.start
        leader_threshold_hit : bool = current_head.is_genesis or current_head.block_number == leader_threshold

        if current_head.is_genesis or leader_threshold_hit:
            print("Creating Leader Schedule...")

            # next_epoch : EpochContext = self.epoch.next_epoch
            # for block_number in range(next_epoch.start, next_epoch.end, next_epoch.slot_size):
            #     self.node.broadcast(MessageFlag.CAMPAIGN, payload=block_number)

            self.start_election_generator(q)

        else:
            print("Waiting For Incoming Blocks")

            self.start_block_generator()


    def start_election_generator(self, q) -> None:
        """
        Starts a timeout in which a node should be collecting camapigns
        from validators nodes. Uses the blockchain's current head as a source of
        randomness to determine the length of the timeout.
        """

        # self.generator_lock.acquire()
        # self.is_campaigning = True
        # self.generator_lock.release()

        header : LynxBlockHeader = self.node.blockchain.get_canonical_head()
        t : int = int(header.hash.hex()[-9:], 16)

        num = pow(2, t)
        q.get()
        print("DONE")
        # self.generator_lock.acquire()
        # self.is_campaigning = False
        # self.generator_lock.release()

        # print(f'Leader Schedule: {self.node.leader_schedule}')


    def start_block_generator(self) -> None:
        """
        Starts a timeout in which a node should be collecting block information
        from validators nodes. Uses the blockchain's current head as a source of
        randomness to determine the length of the timeout.
        """

        header : LynxBlockHeader = self.node.blockchain.get_canonical_block_header_by_number(self.epoch.start)
        t : int = int(header.hash.hex()[-9:], 16)

        num = pow(2, t)

        


    
