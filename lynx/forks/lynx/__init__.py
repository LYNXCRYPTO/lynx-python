from email.header import Header
from typing import (
    Type,
)

from eth.rlp.blocks import BaseBlock
from eth.vm.state import BaseState

from lynx.forks.lynx.headers import (create_header_from_parent, configure_header)

from .blocks import LynxBackwardsHeader, LynxBlock
from .state import LynxState
from eth.vm.forks.berlin import BerlinVM
from eth.vm.forks.frontier import FrontierVM

class LynxVM(FrontierVM):
    # Fork Name
    fork = 'lynx'

    # Classes
    block_class: Type[BaseBlock] = LynxBlock
    _state_class: Type[BaseState] = LynxState


    # Methods
    create_header_from_parent = create_header_from_parent

    # configure_header = configure_header


    