# from lynx.transaction import Transaction
from eth_keys import keys
from eth_typing import Address
from eth.chains.base import MiningChain
from eth.vm.forks.arrow_glacier import ArrowGlacierVM
from eth import constants
from eth.db.atomic import AtomicDB
from eth.chains.mainnet import MAINNET_GENESIS_HEADER
from lynx.wallet import Wallet
    

def test_transaction():
    wallet = Wallet()
    SENDER_PRIVATE_KEY = keys.PrivateKey(bytes.fromhex(wallet.priv_key))
    to_address = Address(b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x02')

    GENESIS_PARAMS = {'difficulty': 69, 'gas_limit': 3141592, 'timestamp': 1514764800,}

    klass = MiningChain.configure(
        __name__='TestChain',
        vm_configuration=(
    (   constants.GENESIS_BLOCK_NUMBER, ArrowGlacierVM),
    ))

    genesis_header = MAINNET_GENESIS_HEADER.copy(gas_limit=3141592)
    # print(f'Genesis Header: {genesis_header.as_dict()}')
    
    chain = klass.from_genesis(AtomicDB(), GENESIS_PARAMS) # pylint: disable=no-member
    vm = chain.get_vm()
    print(chain.get_block().header.as_dict())
    print('-')
    print(chain.get_block().header.as_dict())
    print('-')
    print(chain.get_canonical_head().as_dict())
    print('-')
    genesis = chain.get_canonical_block_header_by_number(0)
    print(genesis.as_dict())

    # tx = vm.create_unsigned_transaction(
    #         nonce=1,
    #         gas_price=10000000000,
    #         gas=100000,
    #         to=to_address,
    #         value=100,
    #         data=b'Aliens are real!',
    #     )
    
    # signed_tx = tx.as_signed_transaction(SENDER_PRIVATE_KEY)


if __name__ == "__main__":
    test_transaction()