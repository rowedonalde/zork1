"""
Zork I - Data Models

Core data structures for the game:
- Direction enum and aliases
- GameObject base class
- Item, Room, Exit, GameState classes
"""

from typing import Dict, List, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum, auto


class Direction(Enum):
    NORTH = auto()
    SOUTH = auto()
    EAST = auto()
    WEST = auto()
    NE = auto()
    NW = auto()
    SE = auto()
    SW = auto()
    UP = auto()
    DOWN = auto()
    IN = auto()
    OUT = auto()


# Direction aliases for parsing
DIRECTION_ALIASES = {
    'n': Direction.NORTH, 'north': Direction.NORTH,
    's': Direction.SOUTH, 'south': Direction.SOUTH,
    'e': Direction.EAST, 'east': Direction.EAST,
    'w': Direction.WEST, 'west': Direction.WEST,
    'ne': Direction.NE, 'northeast': Direction.NE,
    'nw': Direction.NW, 'northwest': Direction.NW,
    'se': Direction.SE, 'southeast': Direction.SE,
    'sw': Direction.SW, 'southwest': Direction.SW,
    'u': Direction.UP, 'up': Direction.UP,
    'd': Direction.DOWN, 'down': Direction.DOWN,
    'in': Direction.IN, 'enter': Direction.IN,
    'out': Direction.OUT, 'exit': Direction.OUT,
}


@dataclass
class GameObject:
    """Base class for all game objects"""
    name: str
    desc: str
    synonyms: List[str] = field(default_factory=list)
    adjectives: List[str] = field(default_factory=list)
    flags: Set[str] = field(default_factory=set)
    action: Optional[Callable] = None

    def matches(self, word: str) -> bool:
        """Check if word matches this object"""
        word_lower = word.lower()
        return (word_lower == self.name.lower() or
                word_lower in [s.lower() for s in self.synonyms] or
                word_lower in [a.lower() for a in self.adjectives])


@dataclass
class Item(GameObject):
    """Represents a takeable or interactive item"""
    location: Optional[str] = None  # Room name or 'inventory'
    size: int = 5
    takeable: bool = False
    value: int = 0

    def __post_init__(self):
        if 'TAKEBIT' in self.flags:
            self.takeable = True


@dataclass
class Exit:
    """Represents an exit from a room"""
    direction: Direction
    destination: Optional[str] = None  # Room name
    message: Optional[str] = None  # Message if blocked
    condition: Optional[Callable] = None  # Function to check if passable


@dataclass
class Room:
    """Represents a location in the game"""
    name: str
    desc: str
    short_desc: str
    exits: List[Exit] = field(default_factory=list)
    items: List[str] = field(default_factory=list)  # Item names
    visited: bool = False
    flags: Set[str] = field(default_factory=set)
    action: Optional[Callable] = None

    def get_exit(self, direction: Direction) -> Optional[Exit]:
        """Get exit in given direction"""
        for exit in self.exits:
            if exit.direction == direction:
                return exit
        return None


class GameState:
    """Manages the game state"""

    def __init__(self):
        self.current_room: str = 'west_of_house'
        self.inventory: List[str] = []
        self.score: int = 0
        self.moves: int = 0
        self.game_over: bool = False
        self.lit: bool = True  # Is current room lit?
        self.lamp_battery: int = 330  # Turns of light remaining
        self.lamp_warned: bool = False  # Has low battery warning been shown?
        self.flags: Dict[str, bool] = {
            'kitchen_window_open': False,
            'trap_door_open': False,
            'grate_revealed': False,
            'grating_open': False,
            'grating_unlocked': False,
            'troll_flag': False,
            'won_flag': False,
            'magic_flag': False,
        }
        self.verbose_mode: bool = True

    def has_item(self, item_name: str) -> bool:
        """Check if player has an item"""
        return item_name in self.inventory

    def add_item(self, item_name: str):
        """Add item to inventory"""
        if item_name not in self.inventory:
            self.inventory.append(item_name)

    def remove_item(self, item_name: str):
        """Remove item from inventory"""
        if item_name in self.inventory:
            self.inventory.remove(item_name)
