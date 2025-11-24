"""
Zork I - Action Classes

All action classes that handle player commands.
This package contains base classes and concrete action implementations.
"""

# Export base classes
from .base import (
    BaseAction,
    SingleObjectAction,
    TwoObjectAction,
    ToggleAction,
)

# Export action implementations
from .turn_on_off import TurnOnOffAction
from .take import TakeAction
from .drop import DropAction
from .examine import ExamineAction
from .give import GiveAction
from .attack import AttackAction
from .throw import ThrowAction
from .climb import ClimbAction
from .move import MoveAction
from .open_close import OpenCloseAction

__all__ = [
    # Base classes
    'BaseAction',
    'SingleObjectAction',
    'TwoObjectAction',
    'ToggleAction',
    # Action implementations
    'TurnOnOffAction',
    'TakeAction',
    'DropAction',
    'ExamineAction',
    'GiveAction',
    'AttackAction',
    'ThrowAction',
    'ClimbAction',
    'MoveAction',
    'OpenCloseAction',
]
