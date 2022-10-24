from lynx.consensus.registry import Registry
from eth.vm.forks.lynx.computation import LynxComputation
from lynx.p2p.node import Node
from eth.constants import ZERO_ADDRESS, CREATE_CONTRACT_ADDRESS
from lynx.constants import REGISTRY_CONTRACT_ADDRESS
from eth_typing import Address
from eth_utils import keccak
from eth_keys import keys
from eth_abi import encode, decode_abi
from eth_account import Account
from web3._utils.contracts import encode_transaction_data
from web3 import Web3
from eth.db.atomic import AtomicDB

def test_registry():
    SENDER_PRIVATE_KEY = keys.PrivateKey(bytes.fromhex('45a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d8'))
    SENDER_ADDRESS = Address(SENDER_PRIVATE_KEY.public_key.to_canonical_address())
    account : Account = Account.create()

    node : Node = Node()

    vm = node.blockchain.get_vm()

    data = Registry.get_bytecode()

    tx = vm.create_unsigned_transaction(
            nonce=0,
            gas_price=0,
            gas=1000000,
            to=CREATE_CONTRACT_ADDRESS,
            value=0,
            data=data,
        )

    signed_tx = tx.as_signed_transaction(private_key=SENDER_PRIVATE_KEY)

    block, receipt, computation = node.blockchain.apply_transaction(signed_tx)

    meta = node.blockchain.forge_block()

    fdata = keccak("isValidator()".encode())
    fnsig = fdata[0:4]
    adata = encode(['address'], [SENDER_ADDRESS])
    data = fnsig + adata

    vm = node.blockchain.get_vm()

    # computation : LynxComputation = vm.execute_bytecode(origin=REGISTRY_CONTRACT_ADDRESS, gas_price=0, gas=10000, to=REGISTRY_CONTRACT_ADDRESS, sender=REGISTRY_CONTRACT_ADDRESS, value=0, data=data, code=Registry.get_deployed_bytecode(), code_address=REGISTRY_CONTRACT_ADDRESS)

    contract_address = Address(bytes.fromhex(Registry.mk_contract_address(sender=SENDER_ADDRESS.hex(), nonce=0)[2:]))

    vm = node.blockchain.get_vm()

    tx = vm.create_unsigned_transaction(
            nonce=1,
            gas_price=0,
            gas=1000000,
            to=REGISTRY_CONTRACT_ADDRESS,
            value=0,
            data=data
        )

    signed_tx = tx.as_signed_transaction(private_key=SENDER_PRIVATE_KEY)

    block, receipt, computation = node.blockchain.apply_transaction(signed_tx)

    vm = node.blockchain.get_vm()

    print(computation.error)

    

if __name__ == "__main__":
    test_registry()