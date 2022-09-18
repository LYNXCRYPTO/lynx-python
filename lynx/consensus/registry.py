from pathlib import Path
from web3 import Web3
from web3.eth import Contract
from web3._utils.contracts import encode_transaction_data
from eth.vm.forks.lynx import LynxVM
from eth_utils import keccak

from eth.constants import ZERO_ADDRESS
from eth_typing import Address
import json

class Registry:

    def __init__(self, vm: LynxVM) -> None:
        """"""
        ...
        


    @classmethod
    def get_contract_path(cls) -> Path:
        """"""

        current_working_directory = Path.cwd()
        registry_path = Path(current_working_directory / 'contracts' / 'Registry.json')

        if registry_path.exists():
            return registry_path
        else:
            raise FileNotFoundError


    @classmethod
    def get_contract(cls) -> Contract:
        
        bytecode : str = cls.get_bytecode()
        abi : list = cls.get_abi()

        return Web3().eth.contract(abi=abi, bytecode=bytecode)


    @classmethod
    def get_bytecode(cls) -> bytes:
        """"""
        
        path = cls.get_contract_path()

        with open(path, 'r') as file:
            contract : dict = json.load(file)
            file.close()
            return bytes.fromhex(contract['bytecode'][2:])

    
    @classmethod
    def get_deployed_bytecode(cls) -> bytes:
        """"""

        path = cls.get_contract_path()

        with open(path, 'r') as file:
            contract : dict = json.load(file)
            file.close()
            return bytes.fromhex(contract['deployedBytecode'][2:])


    @classmethod
    def get_abi(cls) -> list:
        """"""

        path = cls.get_contract_path()

        with open(path, 'r') as file:
            contract : dict = json.load(file)
            file.close()
            return contract['abi']

    
    @classmethod
    def is_validator(cls):
        """"""

        # LynxVM.execute_bytecode(origin=ZERO_ADDRESS, gas_price=0, gas=100000, to=ZERO_ADDRESS, sender=ZERO_ADDRESS, value=0, data=)

        # contract = cls.get_contract()
        # fn = contract.functions.isValidator(address)


        # tx_data = encode_transaction_data(web3=Web3(), fn_identifier=fn.fn_name, contract_abi=contract.abi, fn_abi=fn.abi, args=[address])[2:]

