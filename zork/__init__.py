"""
Zork I: The Great Underground Empire
Translated from ZIL (Zork Implementation Language) to Python

Original (c) Copyright 1983 Infocom, Inc. All Rights Reserved.
Python translation for educational purposes.

This package is organized into modules:
- models: Core data structures (Item, Room, GameState, etc.)
- actions: All action classes for handling commands
- world: Room and item definitions (initialize_world)
- game: Main ZorkGame class and game loop
"""

# Export everything for backward compatibility
from .models import (
    Direction,
    DIRECTION_ALIASES,
    GameObject,
    Item,
    Exit,
    Room,
    GameState,
)

from .actions import (
    BaseAction,
    SingleObjectAction,
    TwoObjectAction,
    ToggleAction,
    TurnOnOffAction,
    TakeAction,
    DropAction,
    ExamineAction,
    GiveAction,
    AttackAction,
    ThrowAction,
    ClimbAction,
    MoveAction,
    OpenCloseAction,
)

from .world import initialize_world
from .game import ZorkGame

__all__ = [
    # Models
    'Direction',
    'DIRECTION_ALIASES',
    'GameObject',
    'Item',
    'Exit',
    'Room',
    'GameState',
    # Actions
    'BaseAction',
    'SingleObjectAction',
    'TwoObjectAction',
    'ToggleAction',
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
    # World
    'initialize_world',
    # Game
    'ZorkGame',
]
