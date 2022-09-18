from typing import (
    Any,
    List,
    Dict,
    TYPE_CHECKING
)

from eth_typing import (
    Address,
)
from eth.abc import (
    BlockHeaderAPI,
    VirtualMachineAPI,
)
from eth.constants import (
    BLANK_ROOT_HASH,
    GENESIS_BLOCK_NUMBER,
    GENESIS_PARENT_HASH,
    ZERO_ADDRESS,
)
from .constants import (
    GENESIS_EPOCH,
    GENESIS_EPOCH_BLOCK_NUMBER,
    GENESIS_SLOT,
    GENESIS_EPOCH_SIZE,
    GENESIS_SLOT_SIZE,
)
from eth.typing import (
    BlockNumber,
    HeaderParams,
)
from eth._utils.db import (
    get_parent_header,
)
from eth_utils import (
    ValidationError,
)
from eth.validation import (
    ALLOWED_HEADER_FIELDS,
    validate_header_params_for_configuration
)
from toolz.functoolz import curry

from eth._utils.headers import (
    new_timestamp_from_parent,
)
from eth.abc import (
    BlockHeaderAPI,
    BlockHeaderSedesAPI,
)
from eth.rlp.headers import BlockHeader
from .blocks import LynxBlock, LynxBlockHeader
from .governance_context import GovernanceContext
if TYPE_CHECKING:
    from eth.vm.forks.lynx import LynxVM    # noqa: F401


def fill_header_params_from_parent(
        parent: LynxBlockHeader,
        timestamp: int,
        coinbase: Address = ZERO_ADDRESS,
        extra_data: bytes = None,
        transaction_root: bytes = None,
        state_root: bytes = None,
        receipt_root: bytes = None) -> Dict[str, HeaderParams]:
    if parent is None:
        parent_hash = GENESIS_PARENT_HASH
        block_number = GENESIS_BLOCK_NUMBER
        epoch = GENESIS_EPOCH
        slot = GENESIS_SLOT
        slot_size = GENESIS_SLOT_SIZE
        epoch_size = GENESIS_EPOCH_SIZE
        epoch_block_number = GENESIS_EPOCH_BLOCK_NUMBER
        if state_root is None:
            state_root = BLANK_ROOT_HASH
    else:
        parent_hash = parent.hash
        block_number = BlockNumber(parent.block_number + 1)
        slot_size = parent.as_dict()['slot_size']
        epoch_size = parent.as_dict()['epoch_size']

        if parent.as_dict()['epoch_block_number'] > slot_size and slot == slot_size - 1:
            epoch = parent.as_dict()['epoch'] + 1
            slot = 1
            epoch_block_number = 1
        else:
            epoch = parent.as_dict()['epoch']
            slot = parent.as_dict()['slot'] + 1
            epoch_block_number = parent.as_dict()['epoch_block_number'] +  1

        if state_root is None:
            state_root = parent.state_root

    header_kwargs: Dict[str, HeaderParams] = {
        'parent_hash': parent_hash,
        'coinbase': coinbase,
        'state_root': state_root,
        'block_number': block_number,
        'timestamp': timestamp,
        'epoch': epoch,
        'slot': slot,
        'epoch_block_number': epoch_block_number,
        'slot_size': slot_size,
        'epoch_size': epoch_size,
    }

    if extra_data is not None:
        header_kwargs['extra_data'] = extra_data
    if transaction_root is not None:
        header_kwargs['transaction_root'] = transaction_root
    if receipt_root is not None:
        header_kwargs['receipt_root'] = receipt_root

    return header_kwargs


def create_lynx_header_from_parent(parent_header: BlockHeaderAPI, **header_params: Any) -> LynxBlockHeader:
    if 'timestamp' not in header_params:
        header_params['timestamp'] = new_timestamp_from_parent(parent_header)

    all_fields = fill_header_params_from_parent(parent_header, **header_params)
    return LynxBlockHeader(**all_fields)


def configure_lynx_header(vm: "LynxVM", **header_params: Any) -> LynxBlockHeader:
    validate_header_params_for_configuration(header_params)

    with vm.get_header().build_changeset(**header_params) as changeset:
        if 'timestamp' in header_params and vm.get_header().block_number > 0:
            parent_header = get_parent_header(changeset.build_rlp(), vm.chaindb)

        header = changeset.commit()
    return header
    