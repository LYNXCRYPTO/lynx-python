from typing import (
    Any,
    Callable,
    List,
    Optional,
    Dict,
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
    GENESIS_GAS_LIMIT
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
    compute_gas_limit,
    new_timestamp_from_parent,
)
from eth.abc import (
    BlockHeaderAPI,
    BlockHeaderSedesAPI,
)
from eth.rlp.headers import BlockHeader

from eth.vm.forks.london.constants import (
    ELASTICITY_MULTIPLIER
)
from eth.vm.forks.london.headers import (
    calculate_expected_base_fee_per_gas
)
from .blocks import LynxBlock, LynxBlockHeader

@curry
def create_header_from_parent(parent_header: Optional[BlockHeaderAPI],
                              **header_params: Any) -> BlockHeaderAPI:

    if 'gas_limit' not in header_params:
        if False and (parent_header is not None and not hasattr(parent_header, 'base_fee_per_gas')):
            # If the previous block was not a London block,
            #   double the gas limit, so the new target is the old gas limit
            header_params['gas_limit'] = parent_header.gas_limit * ELASTICITY_MULTIPLIER
        else:
            # frontier rules
            header_params['gas_limit'] = compute_gas_limit(
                parent_header,
                genesis_gas_limit=GENESIS_GAS_LIMIT,
            )

    # byzantium
    if 'timestamp' not in header_params:
        header_params['timestamp'] = new_timestamp_from_parent(parent_header)

    # The general fill function doesn't recognize this custom field, so remove it
    configured_fee_per_gas = header_params.pop('base_fee_per_gas', None)

    all_fields = fill_header_params_from_parent(parent_header, **header_params)
    all_fields['difficulty'] = 1
    # all_fields['epoch'] = 1
    # all_fields['base_fee_per_gas'] = 0
    # calculated_fee_per_gas = calculate_expected_base_fee_per_gas(parent_header)
    # if configured_fee_per_gas is None:
    #     all_fields['base_fee_per_gas'] = calculated_fee_per_gas
    # else:
    #     # Must not configure an invalid base fee. So verify that either:
    #     #   1. This is the genesis header, or
    #     #   2. The configured value matches the calculated value from the parent
    #     if parent_header is None or configured_fee_per_gas == calculated_fee_per_gas:
    #         all_fields['base_fee_per_gas'] = configured_fee_per_gas
    #     else:
    #         raise ValidationError(
    #             f"Cannot select an invalid base_fee_per_gas of:"
    #             f" {configured_fee_per_gas}, expected: {calculated_fee_per_gas}"
    #         )
    new_header = LynxBlockHeader(**all_fields)  # type:ignore
    return new_header

def fill_header_params_from_parent(
        parent: BlockHeaderAPI,
        gas_limit: int,
        timestamp: int,
        difficulty: int = 1,
        coinbase: Address = ZERO_ADDRESS,
        nonce: bytes = None,
        extra_data: bytes = None,
        transaction_root: bytes = None,
        state_root: bytes = None,
        mix_hash: bytes = None,
        receipt_root: bytes = None,
        # epoch: int = 0,
        ) -> Dict[str, HeaderParams]:

        # block_number: BlockNumber,
        # gas_limit: int,
        # timestamp: int = None,
        # difficulty: int = 0,
        # coinbase: Address = ZERO_ADDRESS,
        # parent_hash: Hash32 = ZERO_HASH32,
        # uncles_hash: Hash32 = EMPTY_UNCLE_HASH,
        # state_root: Hash32 = BLANK_ROOT_HASH,
        # transaction_root: Hash32 = BLANK_ROOT_HASH,
        # receipt_root: Hash32 = BLANK_ROOT_HASH,
        # bloom: int = 0,
        # gas_used: int = 0,
        # extra_data: bytes = b'',
        # nonce: bytes = GENESIS_NONCE,
        # mix_hash: Hash32 = ZERO_HASH32,
        # base_fee_per_gas: int = 0,
        # slot: int = 0,
        # slot_leader : Address = ZERO_ADDRESS,
        # epoch : int = 0

    if parent is None:
        parent_hash = GENESIS_PARENT_HASH
        block_number = GENESIS_BLOCK_NUMBER
        if state_root is None:
            state_root = BLANK_ROOT_HASH
    else:
        parent_hash = parent.hash
        block_number = BlockNumber(parent.block_number + 1)

        if state_root is None:
            state_root = parent.state_root

    header_kwargs: Dict[str, HeaderParams] = {
        'parent_hash': parent_hash,
        'coinbase': coinbase,
        'state_root': state_root,
        'gas_limit': gas_limit,
        'block_number': block_number,
        'timestamp': timestamp,
    }
    if nonce is not None:
        header_kwargs['nonce'] = nonce
    if extra_data is not None:
        header_kwargs['extra_data'] = extra_data
    if transaction_root is not None:
        header_kwargs['transaction_root'] = transaction_root
    if receipt_root is not None:
        header_kwargs['receipt_root'] = receipt_root
    if mix_hash is not None:
        header_kwargs['mix_hash'] = mix_hash
    # if epoch is not None:
    #     header_kwargs['epoch'] = epoch

    return header_kwargs

@curry
def configure_header(vm: VirtualMachineAPI,
                     **header_params: Any) -> BlockHeaderAPI:
    validate_header_params_for_configuration(header_params)

    with vm.get_header().build_changeset(**header_params) as changeset:
        if 'timestamp' in header_params and changeset.block_number > 0:
            parent_header = get_parent_header(changeset.build_rlp(), vm.chaindb)

        header = changeset.commit()
    return header


class LynxBackwardsHeader(BlockHeaderSedesAPI):
    """
    An rlp sedes class for block headers.

    It can serialize and deserialize *both* Lynx and pre-Lynx headers.
    """

    @classmethod
    def serialize(cls, obj: BlockHeaderAPI) -> List[bytes]:
        return obj.serialize(obj)

    @classmethod
    def deserialize(cls, encoded: List[bytes]) -> LynxBlockHeader:
        num_fields = len(encoded)
        if num_fields == 16:
            return LynxBlockHeader.deserialize(encoded)
        elif num_fields == 15:
            return BlockHeader.deserialize(encoded)
        else:
            raise ValueError(
                "Lynx & earlier can only handle headers of 15 or 16 fields. "
                f"Got {num_fields} in {encoded!r}"
            )