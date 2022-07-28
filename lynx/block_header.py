# from eth.abc import ABC
# from eth.vm.forks.arrow_glacier.blocks import ArrowGlacierBlockHeader
# from eth_typing import (
#     BlockNumber,
# )
# from eth_typing.evm import (
#     Address,
#     Hash32
# )
# from eth.constants import (
#     ZERO_ADDRESS,
#     ZERO_HASH32,
#     EMPTY_UNCLE_HASH,
#     GENESIS_NONCE,
#     GENESIS_PARENT_HASH,
#     BLANK_ROOT_HASH,
# )
# from eth._utils.headers import (
#     new_timestamp_from_parent,
# )

# class LynxBlockHeader(ArrowGlacierBlockHeader, ABC):

#     def __init__(self,
#                  block_number: BlockNumber,
#                  gas_limit: int,
#                  timestamp: int = None,
#                  difficulty: int = 0,
#                  coinbase: Address = ZERO_ADDRESS,
#                  parent_hash: Hash32 = ZERO_HASH32,
#                  uncles_hash: Hash32 = EMPTY_UNCLE_HASH,
#                  state_root: Hash32 = BLANK_ROOT_HASH,
#                  transaction_root: Hash32 = BLANK_ROOT_HASH,
#                  receipt_root: Hash32 = BLANK_ROOT_HASH,
#                  bloom: int = 0,
#                  gas_used: int = 0,
#                  extra_data: bytes = b'',
#                  nonce: bytes = GENESIS_NONCE,
#                  mix_hash: Hash32 = ZERO_HASH32,
#                  base_fee_per_gas: int = 0,
#                  slot: int = 0,
#                  slot_leader : Address = ZERO_ADDRESS,
#                  epoch : int = 0) -> None:
#         super().__init__(
#             parent_hash=parent_hash,
#             uncles_hash=uncles_hash,
#             coinbase=coinbase,
#             state_root=state_root,
#             transaction_root=transaction_root,
#             receipt_root=receipt_root,
#             bloom=bloom,
#             difficulty=difficulty,
#             block_number=block_number,
#             gas_limit=gas_limit,
#             gas_used=gas_used,
#             timestamp=timestamp,
#             extra_data=extra_data,
#             mix_hash=mix_hash,
#             nonce=nonce,
#             base_fee_per_gas=base_fee_per_gas,
#         )
#         self.slot : int = slot
#         self.slot_leader : Address = slot_leader
#         self.epoch : int = epoch

        

#     def __str__(self) -> str:
#         return f'<LynxBlockHeader #{self.block_number} {self.hash.hex()}>'
