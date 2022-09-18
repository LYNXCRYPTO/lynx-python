from lynx.consensus.registry import Registry
from eth.constants import ZERO_ADDRESS
from web3._utils.contracts import encode_transaction_data
from web3 import Web3

def test_registry():
    validators = Registry.is_validator()
    print(validators)
    
if __name__ == "__main__":
    test_registry()