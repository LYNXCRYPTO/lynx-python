from typing import (
    Tuple,
    Type,    
    Any,
)
from eth_typing import (BlockNumber)
from eth.chains.base import MiningChain
from eth.vm.forks.lynx import LynxVM
from eth.vm.forks.lynx.constants import (
    GENESIS_EPOCH,
    GENESIS_SLOT,
    GENESIS_EPOCH_BLOCK_NUMBER,
    GENESIS_EPOCH_SIZE,
    GENESIS_SLOT_SIZE,
)
from eth.vm.forks.lynx.blocks import LynxBlockHeader
from .constants import (LYNX_CHAIN_ID)
from eth.abc import (
    VirtualMachineAPI,
)
from eth.chains.base import (
    Chain,
)
from eth.constants import (
    ZERO_HASH32,
    BLANK_ROOT_HASH,
    GENESIS_BLOCK_NUMBER,
    ZERO_ADDRESS,
)
from eth.vm.base import (BlockHeader)
from eth.abc import (BlockAPI, BlockHeaderAPI, BlockAndMetaWitness)

LYNX_VM_CONFIGURATION = ((GENESIS_BLOCK_NUMBER, LynxVM),)

class BaseLynxChain:
    chain_id = LYNX_CHAIN_ID
    vm_configuration: Tuple[
        Tuple[BlockNumber, Type[VirtualMachineAPI]],
        ...
    ] = LYNX_VM_CONFIGURATION


class LynxChain(BaseLynxChain, MiningChain):

    # Forging
    def forge_block(self, *args: Any, **kwargs: Any) -> BlockAndMetaWitness:
        custom_header = self._custom_header(self.header, **kwargs)
        vm = self.get_vm(custom_header)
        current_block = vm.get_block()
        forge_result = vm.forge_block(current_block, *args, **kwargs)
        forged_block = forge_result.block

        self.validate_block(forged_block)

        self.chaindb.persist_block(forged_block)
        self.header = self.create_header_from_parent(forged_block.header)
        return forged_block

LYNX_GENESIS_HEADER = LynxBlockHeader(
    extra_data=b'',
    gas_used=0,
    bloom=0,
    block_number=0,
    parent_hash=ZERO_HASH32,
    receipt_root=BLANK_ROOT_HASH,
    state_root=BLANK_ROOT_HASH,
    timestamp=0,
    transaction_root=BLANK_ROOT_HASH,
    coinbase=ZERO_ADDRESS,
    epoch=GENESIS_EPOCH,
    slot=GENESIS_SLOT,
    epoch_block_number=GENESIS_EPOCH_BLOCK_NUMBER,
    slot_size=GENESIS_SLOT_SIZE,
    epoch_size=GENESIS_EPOCH_SIZE,
)