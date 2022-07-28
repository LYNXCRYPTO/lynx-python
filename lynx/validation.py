from typing import (
    Any,
    Dict,
)
from eth_utils.exceptions import ValidationError

ALLOWED_HEADER_FIELDS = {
    'coinbase',
    'difficulty',
    'gas_limit',
    'timestamp',
    'extra_data',
    'mix_hash',
    'nonce',
    'uncles_hash',
    'transaction_root',
    'receipt_root',
    'slot',
    'slot_leader',
    'epoch'
}


def validate_header_params_for_configuration(header_params: Dict[str, Any]) -> None:
    extra_fields = set(header_params.keys()).difference(ALLOWED_HEADER_FIELDS)
    if extra_fields:
        raise ValidationError(
            "The `configure_header` method may only be used with the fields "
            f"({', '.join(tuple(sorted(ALLOWED_HEADER_FIELDS)))}). "
            f"The provided fields ({', '.join(tuple(sorted(extra_fields)))}) are not supported"
        )