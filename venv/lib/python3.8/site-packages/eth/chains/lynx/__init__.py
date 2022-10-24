from typing import (
    Tuple,
    Type,    
    Any,
    Dict,
)
from eth.typing import (
    AccountState,
    HeaderParams,
    StaticMethod,
)
from eth._utils.db import (
    apply_state_dict,
)
from eth._warnings import catch_and_ignore_import_warning
with catch_and_ignore_import_warning():
    from eth_utils import (
        ValidationError,
    )
    from eth_utils.toolz import (
        assoc,
    )
from eth.vm.chain_context import ChainContext
from eth_typing import (BlockNumber)
from eth.chains.base import BaseChain, MiningChain
from eth.vm.forks.lynx import LynxVM
from eth.vm.forks.lynx.blocks import LynxBlock
from eth.vm.forks.lynx.transactions import LynxTransaction
from eth.constants import CREATE_CONTRACT_ADDRESS
from eth.abc import AtomicDatabaseAPI
from eth.vm.forks.lynx.constants import (
    GENESIS_EPOCH,
    GENESIS_SLOT,
    GENESIS_EPOCH_BLOCK_NUMBER,
    GENESIS_EPOCH_SIZE,
    GENESIS_SLOT_SIZE,
)
from eth.vm.forks.lynx.blocks import LynxBlockHeader
from .constants import LYNX_CHAIN_ID, SATOSHIS_PRIVATE_KEY
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

    # Genesis
    # @classmethod
    # def from_genesis(cls,
    #                  base_db: AtomicDatabaseAPI,
    #                  genesis_params: Dict[str, HeaderParams],
    #                  genesis_state: AccountState = None) -> 'BaseChain':
    #     genesis_vm_class = cls.get_vm_class_for_block_number(BlockNumber(0))

    #     pre_genesis_header = BlockHeader(difficulty=0, block_number=-1, gas_limit=0)
    #     chain_context = ChainContext(cls.chain_id)
    #     state = genesis_vm_class.build_state(base_db, pre_genesis_header, chain_context)

    #     if genesis_state is None:
    #         genesis_state = {}

    #     # mutation
    #     apply_state_dict(state, genesis_state)
    #     state.persist()

    #     if 'state_root' not in genesis_params:
    #         # If the genesis state_root was not specified, use the value
    #         # computed from the initialized state database.
    #         genesis_params = assoc(genesis_params, 'state_root', state.state_root)
    #     elif genesis_params['state_root'] != state.state_root:
    #         # If the genesis state_root was specified, validate that it matches
    #         # the computed state from the initialized state database.
    #         raise ValidationError(
    #             "The provided genesis state root does not match the computed "
    #             f"genesis state root.  Got {state.state_root!r}.  "
    #             f"Expected {genesis_params['state_root']!r}"
    #         )

    #     genesis_header = genesis_vm_class.create_genesis_header(**genesis_params)
    #     return cls.from_genesis_header(base_db, genesis_header)

    # @classmethod
    # def from_genesis_header(cls, base_db: AtomicDatabaseAPI, genesis_header: BlockHeaderAPI) -> BaseChain:
    #     chaindb = cls.get_chaindb_class()(base_db)
    #     vm : LynxVM = cls.get_vm_class_for_block_number(BlockNumber(0))

    #     tx = vm.create_unsigned_transaction(
    #         nonce=0,
    #         gas_price=0,
    #         gas=100000,
    #         to=CREATE_CONTRACT_ADDRESS,
    #         value=0,
    #         data=b''
    #     )
    #     signed_tx = tx.as_signed_transaction(SATOSHIS_PRIVATE_KEY)
        
    #     tx_root = chaindb.add_transaction(genesis_header, b'', signed_tx)
    #     gh = genesis_header.copy(transaction_root=tx_root)
    #     block = LynxBlock(header=gh, transactions=[signed_tx])

    #     chaindb.persist_header(gh)
    #     chain = cls(base_db)
    #     block = chain.apply_transaction(signed_tx)[0]
    #     print(block.as_dict())
    #     chain
    #     return cls(base_db)


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