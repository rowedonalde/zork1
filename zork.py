#!/usr/bin/env python3
"""
Zork I: The Great Underground Empire
Translated from ZIL (Zork Implementation Language) to Python

Original (c) Copyright 1983 Infocom, Inc. All Rights Reserved.
Python translation for educational purposes.
"""

import re
import sys
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
            'grate_open': False,
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


@dataclass
class BaseAction:
    """Abstract base class for an action that can be performed"""
    game: 'ZorkGame'
    direct_object: Optional[str] = None
    preposition: Optional[str] = None
    indirect_object: Optional[str] = None

    @staticmethod
    def from_command(command: str, game: 'ZorkGame') -> 'BaseAction':
        """
        Factory method to create action from command string

        `command` is the full user input command, e.g. "take sword from chest".

        Example:
            def from_command(command: str, game: 'ZorkGame') -> 'SomeAction':
                tokens = command.split()
                verb = tokens[0]
                direct_object = tokens[1] if len(tokens) > 1 else None
                preposition = tokens[2] if len(tokens) > 2 else None
                indirect_object = tokens[3] if len(tokens) > 3 else None
                return SomeAction(game, direct_object, preposition, indirect_object)
        """
        raise NotImplementedError

    def validate_direct_object(self) -> bool:
        """
        Confirm presence of direct object

        Extend this method for relevance of the direct object to the action:
            def validate_direct_object(self) -> bool:
                if not super().validate_direct_object():
                    return False
                # Additional validation logic here
                return True
        """
        if not self.direct_object:
            return True  # No direct object to validate
        if not self.game.find_item(self.direct_object):
            print(f"I don't see any {self.direct_object} here.")
            return False
        return True

    def validate_indirect_object(self) -> bool:
        """Confirm presence of indirect object"""
        if not self.indirect_object:
            return True  # No indirect object to validate
        if not self.game.find_item(self.indirect_object):
            print(f"I don't see any {self.indirect_object} here.")
            return False
        return True

    def validate_preposition(self) -> bool:
        """Confirm preposition is valid for this action"""
        return True  # Default implementation assumes any preposition is valid
    
    def effect(self):
        """Define side effects of the action"""
        raise NotImplementedError

    def __call__(self):
        """Execute the action"""
        if not self.validate_direct_object():
            return
        if not self.validate_indirect_object():
            return
        if not self.validate_preposition():
            return
        self.effect()


class TurnOnOffAction(BaseAction):
    """Action to turn light sources on or off"""

    def __init__(self, game: 'ZorkGame', direct_object: Optional[str], turn_on: bool):
        super().__init__(game, direct_object)
        self.turn_on = turn_on

    @staticmethod
    def from_command(command: str, game: 'ZorkGame', turn_on: bool) -> 'TurnOnOffAction':
        """Factory method to create TurnOnOffAction from command

        Args:
            command: Full command string (e.g., "turn on lantern")
            game: The game instance
            turn_on: True for "turn on", False for "turn off"
        """
        tokens = command.split()
        # Handle "turn on lantern" or "light lantern"
        if len(tokens) >= 3 and tokens[0] == 'turn':
            # "turn on/off lantern" - object is everything after on/off
            direct_object = ' '.join(tokens[2:])
        elif len(tokens) >= 2:
            # "light lantern" - object is everything after verb
            direct_object = ' '.join(tokens[1:])
        else:
            direct_object = None

        return TurnOnOffAction(game, direct_object, turn_on)

    def validate_direct_object(self) -> bool:
        """Validate object exists and can be toggled"""
        if not self.direct_object:
            print(f"Turn {'on' if self.turn_on else 'off'} what?")
            return False

        item = self.game.find_item(self.direct_object)
        if not item:
            print(f"I don't see any {self.direct_object} here.")
            return False

        if 'LIGHTBIT' not in item.flags:
            print(f"You can't turn that {'on' if self.turn_on else 'off'}.")
            return False

        return True

    def effect(self):
        """Toggle the light source and update room lighting"""
        item = self.game.find_item(self.direct_object)
        is_on = 'ONBIT' in item.flags

        if self.turn_on:
            if is_on:
                print("It is already on.")
                return
            item.flags.add('ONBIT')
            print(f"The {item.desc} is now on.")
        else:
            if not is_on:
                print("It is already off.")
                return
            item.flags.discard('ONBIT')
            print(f"The {item.desc} is now off.")

        # Update room lighting and react to light changes
        was_lit = self.game.state.lit
        self.game.state.lit = self.game.is_room_lit()

        if not was_lit and self.game.state.lit:
            # Room just became lit - show description
            print()
            self.game.do_look()
        elif was_lit and not self.game.state.lit:
            # Room just became dark
            print("It is now pitch black.")


class TakeAction(BaseAction):
    """Action to take/pick up an item from room or container"""

    @staticmethod
    def from_command(command: str, game: 'ZorkGame') -> 'TakeAction':
        """Factory method to create TakeAction from command

        Args:
            command: Full command string (e.g., "take sword" or "take sword from chest")
            game: The game instance
        """
        tokens = command.split()
        verb = tokens[0] if tokens else None

        # Check for "take X from Y" pattern
        if 'from' in tokens:
            from_idx = tokens.index('from')
            direct_object = ' '.join(tokens[1:from_idx])
            preposition = 'from'
            indirect_object = ' '.join(tokens[from_idx+1:])
        else:
            # Simple "take X"
            direct_object = ' '.join(tokens[1:]) if len(tokens) > 1 else None
            preposition = None
            indirect_object = None

        return TakeAction(game, direct_object, preposition, indirect_object)

    def validate_direct_object(self) -> bool:
        """Validate object exists and can be taken"""
        if not self.direct_object:
            if self.indirect_object:
                print("Take what from what?")
            else:
                print("Take what?")
            return False

        # If taking from container, find item in container
        if self.indirect_object:
            # Container validation happens in validate_indirect_object
            # Here we just check if item exists in the container
            container = self.game.find_item(self.indirect_object)
            if not container:
                return False  # Error already printed in validate_indirect_object

            # Find item in container
            item = None
            for item_name, potential_item in self.game.items.items():
                if potential_item.location == container.name and potential_item.matches(self.direct_object):
                    item = potential_item
                    break

            if not item:
                print(f"There's no {self.direct_object} in the {container.desc}.")
                return False

            return True
        else:
            # Simple take - find item in room or inventory
            item = self.game.find_item(self.direct_object)
            if not item:
                print(f"I don't see any {self.direct_object} here.")
                return False

            # Check if takeable
            if not item.takeable and 'TAKEBIT' not in item.flags:
                print(f"You can't take the {item.desc}.")
                return False

            # Check if already in inventory
            if item.name in self.game.state.inventory:
                print("You already have that.")
                return False

            return True

    def validate_indirect_object(self) -> bool:
        """Validate container if taking from container"""
        if not self.indirect_object:
            return True  # No container specified

        container = self.game.find_item(self.indirect_object)
        if not container:
            print(f"You don't see any {self.indirect_object} here.")
            return False

        if 'CONTBIT' not in container.flags:
            print(f"You can't take things from the {container.desc}.")
            return False

        return True

    def effect(self):
        """Take the item and add to inventory"""
        item = self.game.find_item(self.direct_object)

        if self.indirect_object:
            # Taking from container
            container = self.game.find_item(self.indirect_object)
            # Find the actual item in container (by location)
            for item_name, potential_item in self.game.items.items():
                if potential_item.location == container.name and potential_item.matches(self.direct_object):
                    item = potential_item
                    break

            self.game.state.add_item(item.name)
            item.location = 'inventory'
            print(f"You take the {item.desc} from the {container.desc}.")
        else:
            # Taking from room
            room = self.game.get_current_room()

            # Remove from current location
            if item.name in room.items:
                room.items.remove(item.name)
            elif item.location and item.location in self.game.items:
                # Item is in a container - don't remove from container's item list
                pass

            # Add to inventory
            self.game.state.add_item(item.name)
            item.location = 'inventory'
            print("Taken.")


class DropAction(BaseAction):
    """Action to drop an item in room or container"""

    @staticmethod
    def from_command(command: str, game: 'ZorkGame') -> 'DropAction':
        """Factory method to create DropAction from command

        Args:
            command: Full command string (e.g., "drop sword" or "put sword in case")
            game: The game instance
        """
        tokens = command.split()
        verb = tokens[0] if tokens else None

        # Check for "put X in Y" pattern
        if 'in' in tokens:
            in_idx = tokens.index('in')
            direct_object = ' '.join(tokens[1:in_idx])
            preposition = 'in'
            indirect_object = ' '.join(tokens[in_idx+1:])
        else:
            # Simple "drop X"
            direct_object = ' '.join(tokens[1:]) if len(tokens) > 1 else None
            preposition = None
            indirect_object = None

        return DropAction(game, direct_object, preposition, indirect_object)

    def validate_direct_object(self) -> bool:
        """Validate object exists and is in inventory"""
        if not self.direct_object:
            if self.indirect_object:
                print("Put what where?")
            else:
                print("Drop what?")
            return False

        item = self.game.find_item(self.direct_object)
        if not item:
            if self.indirect_object:
                print(f"You don't see any {self.direct_object} here.")
            else:
                print(f"You don't have that.")
            return False

        # Check if in inventory
        if not self.game.state.has_item(item.name):
            print(f"You aren't holding the {item.desc}.")
            return False

        return True

    def validate_indirect_object(self) -> bool:
        """Validate container if putting in container"""
        if not self.indirect_object:
            return True  # No container specified

        container = self.game.find_item(self.indirect_object)
        if not container:
            print(f"You don't see any {self.indirect_object} here.")
            return False

        if 'CONTBIT' not in container.flags:
            print(f"You can't put things in the {container.desc}.")
            return False

        return True

    def effect(self):
        """Drop the item in room or container"""
        item = self.game.find_item(self.direct_object)
        self.game.state.remove_item(item.name)

        if self.indirect_object:
            # Putting in container
            container = self.game.find_item(self.indirect_object)
            item.location = container.name

            # Trophy case scoring
            if container.name == 'trophy_case' and item.value > 0:
                points = item.value
                self.game.state.score += points
                print(f"You put the {item.desc} in the {container.desc}.")
                print(f"Your score has just gone up by {points} point{'s' if points != 1 else ''}!")
            else:
                print(f"You put the {item.desc} in the {container.desc}.")
        else:
            # Simple drop in room
            room = self.game.get_current_room()
            room.items.append(item.name)
            item.location = room.name
            print("Dropped.")


class SingleObjectAction(BaseAction):
    """Base class for actions that operate on a single object

    Examples: examine, climb, move, read

    Subclasses should implement:
    - from_command() - Parse command into direct_object
    - effect() - Define what happens when action succeeds
    - validate_direct_object() - Optional: add custom validation
    """

    def __init__(self, game: 'ZorkGame', direct_object: Optional[str],
                 require_object: bool = True, allow_missing: bool = False):
        """
        Args:
            game: The game instance
            direct_object: The object to act upon
            require_object: If True, prints error if no object specified
            allow_missing: If True, allows object to not exist (for fallback behavior)
        """
        super().__init__(game, direct_object)
        self.require_object = require_object
        self.allow_missing = allow_missing

    def validate_direct_object(self) -> bool:
        """Standard validation for single-object actions"""
        if not self.direct_object:
            if self.require_object:
                # Subclass should override to provide specific message
                print(f"{self.__class__.__name__} what?")
                return False
            return True  # Some actions have default behavior when no object

        item = self.game.find_item(self.direct_object)
        if not item:
            if self.allow_missing:
                return True  # Subclass will handle missing object
            print(f"You don't see any {self.direct_object} here.")
            return False

        return True


class TwoObjectAction(BaseAction):
    """Base class for actions with a direct object and indirect object

    Examples: give X to Y, throw X at Y, attack X with Y

    Subclasses should implement:
    - from_command() - Parse command into direct_object, preposition, indirect_object
    - effect() - Define what happens when action succeeds
    - validate_direct_object() - Optional: add custom validation
    - validate_indirect_object() - Optional: add custom validation
    """

    def __init__(self, game: 'ZorkGame', direct_object: Optional[str],
                 preposition: Optional[str], indirect_object: Optional[str],
                 require_direct: bool = True, require_indirect: bool = False):
        """
        Args:
            game: The game instance
            direct_object: The primary object (what is acted upon)
            preposition: The preposition (to, with, at, etc.)
            indirect_object: The secondary object (target, tool, etc.)
            require_direct: If True, direct_object must be specified
            require_indirect: If True, indirect_object must be specified
        """
        super().__init__(game, direct_object, preposition, indirect_object)
        self.require_direct = require_direct
        self.require_indirect = require_indirect

    def validate_direct_object(self) -> bool:
        """Standard validation for direct object"""
        if not self.direct_object:
            if self.require_direct:
                print(f"{self.__class__.__name__.replace('Action', '')} what?")
                return False
            return True

        item = self.game.find_item(self.direct_object)
        if not item:
            print(f"You don't see any {self.direct_object} here.")
            return False

        return True

    def validate_indirect_object(self) -> bool:
        """Standard validation for indirect object"""
        if not self.indirect_object:
            if self.require_indirect:
                print(f"{self.__class__.__name__.replace('Action', '')} what {self.preposition} what?")
                return False
            return True

        item = self.game.find_item(self.indirect_object)
        if not item:
            print(f"You don't see any {self.indirect_object} here.")
            return False

        return True


class ToggleAction(BaseAction):
    """Base class for paired on/off or open/close actions

    Examples: open/close, lock/unlock, light/extinguish

    Subclasses should implement:
    - from_command() - Parse command into direct_object and determine state
    - effect() - Define what happens when toggle succeeds
    - validate_direct_object() - Check if object can be toggled
    """

    def __init__(self, game: 'ZorkGame', direct_object: Optional[str],
                 new_state: bool, state_flag: str):
        """
        Args:
            game: The game instance
            direct_object: The object to toggle
            new_state: True for "on"/"open", False for "off"/"close"
            state_flag: The flag that tracks state (e.g., 'OPENBIT', 'ONBIT')
        """
        super().__init__(game, direct_object)
        self.new_state = new_state
        self.state_flag = state_flag

    def get_current_state(self, item: Item) -> bool:
        """Check if item is currently in the target state"""
        return self.state_flag in item.flags

    def set_state(self, item: Item, state: bool):
        """Set the item's state"""
        if state:
            item.flags.add(self.state_flag)
        else:
            item.flags.discard(self.state_flag)


class ExamineAction(SingleObjectAction):
    """Action to examine an object"""

    def __init__(self, game: 'ZorkGame', direct_object: Optional[str]):
        # Allow missing object (will default to look command)
        super().__init__(game, direct_object, require_object=False, allow_missing=True)

    @staticmethod
    def from_command(command: str, game: 'ZorkGame') -> 'ExamineAction':
        """Factory method to create ExamineAction from command"""
        tokens = command.split()
        direct_object = ' '.join(tokens[1:]) if len(tokens) > 1 else None
        return ExamineAction(game, direct_object)

    def validate_direct_object(self) -> bool:
        """Validate object - but allow missing for fallback to look"""
        if not self.direct_object:
            return True  # Will trigger look command in effect()

        # For examine, we allow objects not found (special cases handled in effect)
        return True

    def effect(self):
        """Examine the object or look around"""
        if not self.direct_object:
            # No object specified - default to look
            self.game.do_look()
            return

        item = self.game.find_item(self.direct_object)
        if not item:
            print(f"You don't see any {self.direct_object} here.")
            return

        # Special descriptions
        if item.name == 'leaflet':
            print("\"WELCOME TO ZORK!")
            print()
            print("ZORK is a game of adventure, danger, and low cunning. In it you will")
            print("explore some of the most amazing territory ever seen by mortals. No")
            print("computer should be without one!\"")
        elif item.name == 'mailbox':
            if 'leaflet' in [i.name for i in self.game.items.values() if i.location == 'mailbox']:
                print("The small mailbox is closed.")
                print("The leaflet is inside.")
            else:
                print("The small mailbox is empty.")
        else:
            print(f"You see nothing special about the {item.desc}.")


class GiveAction(TwoObjectAction):
    """Action to give an item to an NPC"""

    def __init__(self, game: 'ZorkGame', direct_object: Optional[str],
                 preposition: Optional[str], indirect_object: Optional[str]):
        super().__init__(game, direct_object, preposition, indirect_object,
                        require_direct=True, require_indirect=True)

    @staticmethod
    def from_command(command: str, game: 'ZorkGame') -> 'GiveAction':
        """Factory method to create GiveAction from command"""
        tokens = command.split()

        if 'to' in tokens:
            to_idx = tokens.index('to')
            direct_object = ' '.join(tokens[1:to_idx])
            preposition = 'to'
            indirect_object = ' '.join(tokens[to_idx+1:])
        else:
            # Fallback parsing
            direct_object = tokens[1] if len(tokens) > 1 else None
            preposition = None
            indirect_object = tokens[2] if len(tokens) > 2 else None

        return GiveAction(game, direct_object, preposition, indirect_object)

    def validate_direct_object(self) -> bool:
        """Validate item exists and is in inventory"""
        if not self.direct_object:
            print("Give what to whom?")
            return False

        item = self.game.find_item(self.direct_object)
        if not item:
            print(f"You don't have any {self.direct_object}.")
            return False

        if not self.game.state.has_item(item.name):
            print(f"You aren't holding the {item.desc}.")
            return False

        return True

    def validate_indirect_object(self) -> bool:
        """Validate target exists and is an actor"""
        if not self.indirect_object:
            print("Give what to whom?")
            return False

        target = self.game.find_item(self.indirect_object)
        if not target:
            print(f"You don't see any {self.indirect_object} here.")
            return False

        if 'ACTORBIT' not in target.flags:
            item = self.game.find_item(self.direct_object)
            print(f"You can't give a {item.desc} to a {target.desc}!")
            return False

        return True

    def effect(self):
        """Give the item to the NPC"""
        item = self.game.find_item(self.direct_object)
        target = self.game.find_item(self.indirect_object)

        # Default behavior - NPC refuses (can be overridden for specific NPCs later)
        print(f"The {target.desc} refuses it politely.")


class AttackAction(TwoObjectAction):
    """Action to attack an NPC with a weapon"""

    def __init__(self, game: 'ZorkGame', direct_object: Optional[str],
                 preposition: Optional[str], indirect_object: Optional[str]):
        super().__init__(game, direct_object, preposition, indirect_object,
                        require_direct=True, require_indirect=False)

    @staticmethod
    def from_command(command: str, game: 'ZorkGame') -> 'AttackAction':
        """Factory method to create AttackAction from command"""
        tokens = command.split()

        if 'with' in tokens:
            with_idx = tokens.index('with')
            direct_object = ' '.join(tokens[1:with_idx])
            preposition = 'with'
            indirect_object = ' '.join(tokens[with_idx+1:])
        else:
            # Just "attack troll" without weapon
            direct_object = ' '.join(tokens[1:]) if len(tokens) > 1 else None
            preposition = None
            indirect_object = None

        return AttackAction(game, direct_object, preposition, indirect_object)

    def validate_direct_object(self) -> bool:
        """Validate target exists and is attackable"""
        if not self.direct_object:
            print("Attack what?")
            return False

        target = self.game.find_item(self.direct_object)
        if not target:
            print(f"You don't see any {self.direct_object} here.")
            return False

        if 'ACTORBIT' not in target.flags:
            print(f"You can't attack the {target.desc}.")
            return False

        return True

    def validate_indirect_object(self) -> bool:
        """Validate weapon if specified"""
        if not self.indirect_object:
            return True  # Weapon is optional (validated in effect)

        weapon = self.game.find_item(self.indirect_object)
        if not weapon:
            print(f"You don't have any {self.indirect_object}.")
            return False

        if not self.game.state.has_item(weapon.name):
            print(f"You aren't holding the {weapon.desc}.")
            return False

        if 'WEAPONBIT' not in weapon.flags:
            print(f"The {weapon.desc} isn't much of a weapon.")
            return False

        return True

    def effect(self):
        """Perform the attack"""
        import random

        target = self.game.find_item(self.direct_object)
        weapon = self.game.find_item(self.indirect_object) if self.indirect_object else None

        # Handle troll specifically
        if target.name == 'troll':
            if not weapon:
                print("With what? Your bare hands?")
                return

            # Simple combat - 50% chance of killing troll
            if random.random() < 0.5:
                print(f"You swing the {weapon.desc} at the troll.")
                print("The troll is struck by your blow and falls dead!")
                print("The troll's body dissolves into a cloud of greasy black smoke.")

                # Remove troll
                room = self.game.get_current_room()
                if target.name in room.items:
                    room.items.remove(target.name)

                # Set troll flag to open passages
                self.game.state.flags['troll_flag'] = True

                # Drop the axe
                room.items.append('axe')
                if 'axe' not in self.game.items:
                    self.game.items['axe'] = Item(
                        name='axe',
                        desc='bloody axe',
                        synonyms=['weapon'],
                        adjectives=['bloody'],
                        location=room.name,
                        takeable=True,
                        flags={'TAKEBIT', 'WEAPONBIT'},
                        size=25
                    )
                else:
                    self.game.items['axe'].location = room.name
            else:
                print(f"You swing the {weapon.desc} at the troll.")
                print("The troll deftly parries your blow and grins menacingly.")
                print("The troll doesn't look amused.")
        else:
            print(f"You can't attack the {target.desc}.")


class ThrowAction(TwoObjectAction):
    """Action to throw an item at a target"""

    def __init__(self, game: 'ZorkGame', direct_object: Optional[str],
                 preposition: Optional[str], indirect_object: Optional[str]):
        super().__init__(game, direct_object, preposition, indirect_object,
                        require_direct=True, require_indirect=False)

    @staticmethod
    def from_command(command: str, game: 'ZorkGame') -> 'ThrowAction':
        """Factory method to create ThrowAction from command"""
        tokens = command.split()

        if 'at' in tokens:
            at_idx = tokens.index('at')
            direct_object = ' '.join(tokens[1:at_idx])
            preposition = 'at'
            indirect_object = ' '.join(tokens[at_idx+1:])
        else:
            # Just "throw sword" without target
            direct_object = ' '.join(tokens[1:]) if len(tokens) > 1 else None
            preposition = None
            indirect_object = None

        return ThrowAction(game, direct_object, preposition, indirect_object)

    def validate_direct_object(self) -> bool:
        """Validate item exists and is in inventory"""
        if not self.direct_object:
            print("Throw what?")
            return False

        item = self.game.find_item(self.direct_object)
        if not item:
            print(f"You don't have any {self.direct_object}.")
            return False

        if not self.game.state.has_item(item.name):
            print(f"You aren't holding the {item.desc}.")
            return False

        return True

    def validate_indirect_object(self) -> bool:
        """Validate target if specified"""
        if not self.indirect_object:
            return True  # Target is optional

        target = self.game.find_item(self.indirect_object)
        if not target:
            print(f"You don't see any {self.indirect_object} here.")
            return False

        return True

    def effect(self):
        """Throw the item"""
        item = self.game.find_item(self.direct_object)

        if self.indirect_object:
            # Throwing at target
            target = self.game.find_item(self.indirect_object)
            print(f"You throw the {item.desc} at the {target.desc}.")
            print("It bounces harmlessly off.")
        else:
            # Just throwing (no target)
            print("Thrown.")

        # Drop the item either way
        self.game.state.remove_item(item.name)
        room = self.game.get_current_room()
        room.items.append(item.name)
        item.location = room.name


class ClimbAction(SingleObjectAction):
    """Action to climb an object"""

    def __init__(self, game: 'ZorkGame', direct_object: Optional[str]):
        super().__init__(game, direct_object, require_object=True, allow_missing=False)

    @staticmethod
    def from_command(command: str, game: 'ZorkGame') -> 'ClimbAction':
        """Factory method to create ClimbAction from command"""
        tokens = command.split()
        direct_object = ' '.join(tokens[1:]) if len(tokens) > 1 else None
        return ClimbAction(game, direct_object)

    def validate_direct_object(self) -> bool:
        """Validate object exists"""
        if not self.direct_object:
            print("Climb what?")
            return False

        item = self.game.find_item(self.direct_object)
        if not item:
            print(f"You don't see any {self.direct_object} here.")
            return False

        return True

    def effect(self):
        """Climb the object"""
        item = self.game.find_item(self.direct_object)

        # Special case for tree in forest path
        if item.name == 'tree' and self.game.state.current_room == 'path':
            self.game.state.current_room = 'up_a_tree'
            self.game.state.moves += 1
            self.game.do_look()
        else:
            print(f"You can't climb the {item.desc}.")


class MoveAction(SingleObjectAction):
    """Action to move/push an object"""

    def __init__(self, game: 'ZorkGame', direct_object: Optional[str]):
        super().__init__(game, direct_object, require_object=True, allow_missing=False)

    @staticmethod
    def from_command(command: str, game: 'ZorkGame') -> 'MoveAction':
        """Factory method to create MoveAction from command"""
        tokens = command.split()
        direct_object = ' '.join(tokens[1:]) if len(tokens) > 1 else None
        return MoveAction(game, direct_object)

    def validate_direct_object(self) -> bool:
        """Validate object exists"""
        if not self.direct_object:
            print("Move what?")
            return False

        item = self.game.find_item(self.direct_object)
        if not item:
            print(f"You don't see any {self.direct_object} here.")
            return False

        return True

    def effect(self):
        """Move the object"""
        item = self.game.find_item(self.direct_object)

        # Special case for rug - reveals trap door
        if item.name == 'rug':
            print("With a great effort, the rug is moved to one side of the room, revealing the dusty cover of a closed trap door.")
            trap_door = self.game.items.get('trap_door')
            if trap_door:
                trap_door.flags.discard('NDESCBIT')
        else:
            print(f"You can't move the {item.desc}.")


class ZorkGame:
    """Main game engine"""

    def __init__(self):
        self.state = GameState()
        self.rooms: Dict[str, Room] = {}
        self.items: Dict[str, Item] = {}
        self.initialize_world()

    def initialize_world(self):
        """Initialize all rooms and items"""

        # Create rooms
        self.rooms['west_of_house'] = Room(
            name='west_of_house',
            short_desc='West of House',
            desc='You are standing in an open field west of a white house, with a boarded front door.',
            exits=[
                Exit(Direction.NORTH, 'north_of_house'),
                Exit(Direction.SOUTH, 'south_of_house'),
                Exit(Direction.NE, 'north_of_house'),
                Exit(Direction.SE, 'south_of_house'),
                Exit(Direction.WEST, 'forest_1'),
                Exit(Direction.EAST, None, "The door is boarded and you can't remove the boards."),
            ],
            flags={'ONBIT', 'SACREDBIT'}
        )

        self.rooms['north_of_house'] = Room(
            name='north_of_house',
            short_desc='North of House',
            desc='You are facing the north side of a white house. There is no door here, '
                 'and all the windows are boarded up. To the north a narrow path winds through the trees.',
            exits=[
                Exit(Direction.NORTH, 'path'),
                Exit(Direction.SOUTH, None, "The windows are all boarded."),
                Exit(Direction.EAST, 'east_of_house'),
                Exit(Direction.WEST, 'west_of_house'),
                Exit(Direction.SE, 'east_of_house'),
                Exit(Direction.SW, 'west_of_house'),
            ],
            flags={'ONBIT', 'SACREDBIT'}
        )

        self.rooms['south_of_house'] = Room(
            name='south_of_house',
            short_desc='South of House',
            desc='You are facing the south side of a white house. There is no door here, '
                 'and all the windows are boarded.',
            exits=[
                Exit(Direction.NORTH, None, "The windows are all boarded."),
                Exit(Direction.EAST, 'east_of_house'),
                Exit(Direction.WEST, 'west_of_house'),
                Exit(Direction.NE, 'east_of_house'),
                Exit(Direction.NW, 'west_of_house'),
                Exit(Direction.SOUTH, 'forest_3'),
            ],
            flags={'ONBIT', 'SACREDBIT'}
        )

        self.rooms['east_of_house'] = Room(
            name='east_of_house',
            short_desc='Behind House',
            desc='You are behind the white house. A path leads into the forest to the east. '
                 'In one corner of the house there is a small window which is slightly ajar.',
            exits=[
                Exit(Direction.NORTH, 'north_of_house'),
                Exit(Direction.SOUTH, 'south_of_house'),
                Exit(Direction.NW, 'north_of_house'),
                Exit(Direction.SW, 'south_of_house'),
                Exit(Direction.EAST, 'clearing'),
                Exit(Direction.WEST, 'kitchen', condition=lambda: self.state.flags['kitchen_window_open']),
                Exit(Direction.IN, 'kitchen', condition=lambda: self.state.flags['kitchen_window_open']),
            ],
            flags={'ONBIT', 'SACREDBIT'}
        )

        self.rooms['kitchen'] = Room(
            name='kitchen',
            short_desc='Kitchen',
            desc='You are in the kitchen of the white house. A table seems to have been used recently '
                 'for the preparation of food. A passage leads to the west and a dark staircase can be '
                 'seen leading upward. A dark chimney leads down and to the north is a small window which is open.',
            exits=[
                Exit(Direction.WEST, 'living_room'),
                Exit(Direction.EAST, 'east_of_house', condition=lambda: self.state.flags['kitchen_window_open']),
                Exit(Direction.OUT, 'east_of_house', condition=lambda: self.state.flags['kitchen_window_open']),
                Exit(Direction.UP, 'attic'),
                Exit(Direction.DOWN, None, "Only Santa Claus climbs down chimneys."),
            ],
            flags={'ONBIT', 'SACREDBIT'}
        )

        self.rooms['attic'] = Room(
            name='attic',
            short_desc='Attic',
            desc='This is the attic. The only exit is a stairway leading down.',
            exits=[
                Exit(Direction.DOWN, 'kitchen'),
            ],
            flags={'SACREDBIT'}
        )

        self.rooms['living_room'] = Room(
            name='living_room',
            short_desc='Living Room',
            desc='You are in the living room. There is a doorway to the east, a wooden door with strange '
                 'gothic lettering to the west, which appears to be nailed shut, a trophy case, and a large '
                 'oriental rug in the center of the room.',
            exits=[
                Exit(Direction.EAST, 'kitchen'),
                Exit(Direction.WEST, None, "The door is nailed shut."),
                Exit(Direction.DOWN, 'cellar', condition=lambda: self.state.flags['trap_door_open']),
            ],
            flags={'ONBIT', 'SACREDBIT'}
        )

        self.rooms['cellar'] = Room(
            name='cellar',
            short_desc='Cellar',
            desc='You are in a dark and damp cellar with a narrow passageway leading north, '
                 'and a crawlway to the south. On the west is the bottom of a steep metal ramp '
                 'which is unclimbable.',
            exits=[
                Exit(Direction.NORTH, 'troll_room'),
                Exit(Direction.SOUTH, 'east_of_chasm'),
                Exit(Direction.UP, 'living_room', condition=lambda: self.state.flags['trap_door_open']),
                Exit(Direction.WEST, None, "You try to ascend the ramp, but it is impossible, and you slide back down."),
            ]
        )

        self.rooms['troll_room'] = Room(
            name='troll_room',
            short_desc='Troll Room',
            desc='This is a small room with passages to the east and south and a forbidding hole leading west. '
                 'Bloodstains and deep scratches (perhaps made by an axe) mar the walls.',
            exits=[
                Exit(Direction.SOUTH, 'cellar'),
                Exit(Direction.EAST, 'east_of_chasm', condition=lambda: self.state.flags['troll_flag']),
                Exit(Direction.WEST, 'east_of_chasm', condition=lambda: self.state.flags['troll_flag']),
            ]
        )

        self.rooms['east_of_chasm'] = Room(
            name='east_of_chasm',
            short_desc='East of Chasm',
            desc='You are on the east edge of a chasm, the bottom of which cannot be seen. '
                 'A narrow passage goes north, and the path you are on continues to the east.',
            exits=[
                Exit(Direction.NORTH, 'cellar'),
                Exit(Direction.EAST, 'gallery'),
                Exit(Direction.DOWN, None, "The chasm probably leads straight to the infernal regions."),
            ]
        )

        self.rooms['gallery'] = Room(
            name='gallery',
            short_desc='Gallery',
            desc='This is an art gallery. Most of the paintings have been stolen by vandals with '
                 'exceptional taste. The vandals left through either the north or west exits.',
            exits=[
                Exit(Direction.WEST, 'east_of_chasm'),
                Exit(Direction.NORTH, 'studio'),
            ],
            flags={'ONBIT'}
        )

        self.rooms['studio'] = Room(
            name='studio',
            short_desc='Studio',
            desc='This appears to have been an artist\'s studio. The walls and floors are splattered '
                 'with paints of 69 different colors. Strangely enough, nothing of value is hanging here. '
                 'At the south end of the room is an open door (also covered with paint).',
            exits=[
                Exit(Direction.SOUTH, 'gallery'),
            ]
        )

        self.rooms['clearing'] = Room(
            name='clearing',
            short_desc='Forest Clearing',
            desc='You are in a small clearing in a well marked forest path that extends to the east and west.',
            exits=[
                Exit(Direction.WEST, 'east_of_house'),
                Exit(Direction.EAST, 'canyon_view'),
                Exit(Direction.NORTH, 'forest_2'),
                Exit(Direction.SOUTH, 'forest_3'),
            ],
            flags={'ONBIT', 'SACREDBIT'}
        )

        self.rooms['forest_1'] = Room(
            name='forest_1',
            short_desc='Forest',
            desc='This is a forest, with trees in all directions. To the east, there appears to be sunlight.',
            exits=[
                Exit(Direction.EAST, 'path'),
                Exit(Direction.SOUTH, 'forest_3'),
                Exit(Direction.WEST, None, "You would need a machete to go further west."),
            ],
            flags={'ONBIT', 'SACREDBIT'}
        )

        self.rooms['forest_2'] = Room(
            name='forest_2',
            short_desc='Forest',
            desc='This is a dimly lit forest, with large trees all around.',
            exits=[
                Exit(Direction.NORTH, None, "The forest becomes impenetrable to the north."),
                Exit(Direction.SOUTH, 'clearing'),
                Exit(Direction.WEST, 'path'),
            ],
            flags={'ONBIT', 'SACREDBIT'}
        )

        self.rooms['forest_3'] = Room(
            name='forest_3',
            short_desc='Forest',
            desc='This is a dimly lit forest, with large trees all around.',
            exits=[
                Exit(Direction.NORTH, 'clearing'),
                Exit(Direction.WEST, 'forest_1'),
                Exit(Direction.NW, 'south_of_house'),
                Exit(Direction.EAST, None, "The rank undergrowth prevents eastward movement."),
                Exit(Direction.SOUTH, None, "Storm-tossed trees block your way."),
            ],
            flags={'ONBIT', 'SACREDBIT'}
        )

        self.rooms['path'] = Room(
            name='path',
            short_desc='Forest Path',
            desc='This is a path winding through a dimly lit forest. The path heads north-south here. '
                 'One particularly large tree with some low branches stands at the edge of the path.',
            exits=[
                Exit(Direction.NORTH, 'north_of_house'),
                Exit(Direction.SOUTH, 'south_of_house'),
                Exit(Direction.EAST, 'forest_2'),
                Exit(Direction.WEST, 'forest_1'),
                Exit(Direction.UP, 'up_a_tree'),
            ],
            flags={'ONBIT', 'SACREDBIT'}
        )

        self.rooms['up_a_tree'] = Room(
            name='up_a_tree',
            short_desc='Up a Tree',
            desc='You are about 10 feet above the ground nestled among some large branches. '
                 'The nearest branch above you is above your reach.',
            exits=[
                Exit(Direction.DOWN, 'path'),
            ],
            flags={'ONBIT', 'SACREDBIT'}
        )

        self.rooms['canyon_view'] = Room(
            name='canyon_view',
            short_desc='Canyon View',
            desc='You are at the top of the Great Canyon on its west wall. From here there is a '
                 'marvelous view of the canyon and parts of the Frigid River upstream. Across the '
                 'canyon, the walls of the White Cliffs join the mighty ramparts of the Flathead Mountains '
                 'to the east. Following the canyon upstream to the north, Aragain Falls may be seen, '
                 'complete with rainbow.',
            exits=[
                Exit(Direction.WEST, 'clearing'),
                Exit(Direction.NORTH, None, "The canyon is too wide to cross."),
                Exit(Direction.SOUTH, None, "The canyon is too wide to cross."),
                Exit(Direction.EAST, None, "The canyon is too wide to cross."),
            ],
            flags={'ONBIT', 'SACREDBIT'}
        )

        # Create items
        self.items['mailbox'] = Item(
            name='mailbox',
            desc='small mailbox',
            synonyms=['box', 'mail'],
            adjectives=['small'],
            location='west_of_house',
            flags={'CONTBIT'}
        )

        self.items['leaflet'] = Item(
            name='leaflet',
            desc='leaflet',
            synonyms=['booklet', 'pamphlet'],
            location='mailbox',
            takeable=True,
            flags={'TAKEBIT'}
        )

        self.items['sword'] = Item(
            name='sword',
            desc='elvish sword',
            synonyms=['blade', 'weapon'],
            adjectives=['elvish', 'elven'],
            location='living_room',
            takeable=True,
            flags={'TAKEBIT', 'WEAPONBIT'},
            value=10,
            size=25
        )

        self.items['lantern'] = Item(
            name='lantern',
            desc='brass lantern',
            synonyms=['lamp', 'light'],
            adjectives=['brass'],
            location='living_room',
            takeable=True,
            flags={'TAKEBIT', 'LIGHTBIT'},  # Can provide light
            size=15
        )

        self.items['rug'] = Item(
            name='rug',
            desc='large rug',
            synonyms=['carpet'],
            adjectives=['large', 'oriental'],
            location='living_room',
            flags={'TRYTAKEBIT'}
        )

        self.items['trap_door'] = Item(
            name='trap_door',
            desc='trap door',
            synonyms=['door', 'trapdoor', 'trap door'],
            adjectives=['trap'],
            location='living_room',
            flags={'DOORBIT', 'NDESCBIT'}
        )

        self.items['trophy_case'] = Item(
            name='trophy_case',
            desc='trophy case',
            synonyms=['case'],
            adjectives=['trophy'],
            location='living_room',
            flags={'CONTBIT', 'NDESCBIT', 'TRYTAKEBIT'}
        )

        # Treasures
        self.items['painting'] = Item(
            name='painting',
            desc='beautiful painting',
            synonyms=['picture'],
            adjectives=['beautiful'],
            location='gallery',
            takeable=True,
            flags={'TAKEBIT'},
            value=4,
            size=20
        )

        self.items['jewels'] = Item(
            name='jewels',
            desc='jewel-encrusted egg',
            synonyms=['egg', 'jewel'],
            adjectives=['jeweled', 'jewel-encrusted'],
            location='living_room',  # Put in living room for easy testing
            takeable=True,
            flags={'TAKEBIT'},
            value=5,
            size=10
        )

        # NPCs
        self.items['troll'] = Item(
            name='troll',
            desc='nasty troll',
            synonyms=['monster'],
            adjectives=['nasty'],
            location='troll_room',
            flags={'ACTORBIT', 'TRYTAKEBIT'}
        )

        # Scenery/climbable objects
        self.items['tree'] = Item(
            name='tree',
            desc='large tree',
            synonyms=['oak', 'branch', 'branches'],
            adjectives=['large', 'tall'],
            location='path',
            flags={'TRYTAKEBIT'}
        )

        # Add items to rooms
        self.rooms['west_of_house'].items.append('mailbox')
        self.rooms['living_room'].items.extend(['sword', 'lantern', 'rug', 'trap_door', 'trophy_case', 'jewels'])
        self.rooms['gallery'].items.append('painting')
        self.rooms['troll_room'].items.append('troll')
        self.rooms['path'].items.append('tree')

    def get_current_room(self) -> Room:
        """Get the current room object"""
        return self.rooms[self.state.current_room]

    def is_room_lit(self) -> bool:
        """Check if the current room is lit

        Room is lit if:
        1. Room has ONBIT flag (naturally lit), OR
        2. Player has a light source that's on (LIGHTBIT + ONBIT)
        """
        room = self.get_current_room()

        # Check if room is naturally lit
        if 'ONBIT' in room.flags:
            return True

        # Check if player has an active light source
        for item_name in self.state.inventory:
            item = self.items.get(item_name)
            if item and 'LIGHTBIT' in item.flags and 'ONBIT' in item.flags:
                return True

        # Check if there's a light source in the room
        for item_name in room.items:
            item = self.items.get(item_name)
            if item and 'LIGHTBIT' in item.flags and 'ONBIT' in item.flags:
                return True

        return False

    def find_item(self, word: str, include_hidden: bool = True) -> Optional[Item]:
        """Find an item by name in current room or inventory"""
        room = self.get_current_room()

        # Check inventory
        for item_name in self.state.inventory:
            item = self.items.get(item_name)
            if item and item.matches(word):
                return item

        # Check current room (including hidden items if requested)
        for item_name in room.items:
            item = self.items.get(item_name)
            if item and item.matches(word):
                return item

        # Check items inside containers in room
        for item_name in room.items:
            container = self.items.get(item_name)
            if container and 'CONTBIT' in container.flags:
                # Check inside container
                for other_name, other_item in self.items.items():
                    if other_item.location == item_name and other_item.matches(word):
                        return other_item

        return None

    def parse_command(self, command: str) -> tuple:
        """Parse user command into verb and objects"""
        words = command.lower().strip().split()
        if not words:
            return None, None, None

        verb = words[0]
        obj1 = words[1] if len(words) > 1 else None
        obj2 = None

        # Special handling for "turn on/off object"
        if verb == 'turn' and len(words) >= 3 and words[1] in ['on', 'off']:
            obj1 = words[1]  # 'on' or 'off'
            obj2 = ' '.join(words[2:])  # object name
            return verb, obj1, obj2

        # Special handling for multi-word commands with prepositions
        if len(words) > 3:
            if verb == 'put' and 'in' in words:
                in_idx = words.index('in')
                obj1 = ' '.join(words[1:in_idx])  # item to put
                obj2 = ' '.join(words[in_idx+1:])  # container
                return 'put_in', obj1, obj2
            elif verb == 'take' and 'from' in words:
                from_idx = words.index('from')
                obj1 = ' '.join(words[1:from_idx])  # item to take
                obj2 = ' '.join(words[from_idx+1:])  # container
                return 'take_from', obj1, obj2
            elif verb == 'give' and 'to' in words:
                to_idx = words.index('to')
                obj1 = ' '.join(words[1:to_idx])  # item to give
                obj2 = ' '.join(words[to_idx+1:])  # target
                return 'give_to', obj1, obj2
            elif verb == 'throw' and 'at' in words:
                at_idx = words.index('at')
                obj1 = ' '.join(words[1:at_idx])  # item to throw
                obj2 = ' '.join(words[at_idx+1:])  # target
                return verb, obj1, obj2

        # Handle "verb obj1 with/using obj2" or "verb obj1 in/on obj2"
        if len(words) > 2:
            if words[2] in ['with', 'using', 'in', 'on', 'to', 'at', 'under']:
                obj2 = words[3] if len(words) > 3 else None
            else:
                obj1 = ' '.join(words[1:])

        return verb, obj1, obj2

    def do_look(self, _=None, __=None):
        """Look around the current room"""
        room = self.get_current_room()

        # Update light status
        self.state.lit = self.is_room_lit()

        if not self.state.lit:
            print("\nIt is pitch black. You are likely to be eaten by a grue.")
            return

        print(f"\n{room.short_desc}")

        if self.state.verbose_mode or not room.visited:
            print(room.desc)
            room.visited = True

        # List items in room
        visible_items = []
        for item_name in room.items:
            item = self.items.get(item_name)
            if item and 'NDESCBIT' not in item.flags:
                visible_items.append(item)

        if visible_items:
            print()
            for item in visible_items:
                print(f"There is a {item.desc} here.")

    def do_go(self, direction_word: str, _=None):
        """Move in a direction"""
        direction = DIRECTION_ALIASES.get(direction_word)
        if not direction:
            print("I don't understand that direction.")
            return

        room = self.get_current_room()
        exit = room.get_exit(direction)

        if not exit:
            print("You can't go that way.")
            return

        if exit.message:
            print(exit.message)
            return

        if exit.condition and not exit.condition():
            # Check if troll is blocking
            if self.state.current_room == 'troll_room' and direction in [Direction.EAST, Direction.WEST]:
                print("The troll fends you off with a menacing gesture.")
            elif direction in [Direction.WEST, Direction.IN] and self.state.current_room == 'east_of_house':
                print("The window is closed.")
            else:
                print("You can't go that way.")
            return

        if not exit.destination:
            print("You can't go that way.")
            return

        self.state.current_room = exit.destination
        self.state.moves += 1
        self.do_look()

    def do_take(self, obj_name: str, _=None):
        """Take an item"""
        action = TakeAction(self, obj_name)
        action()

    def do_drop(self, obj_name: str, _=None):
        """Drop an item"""
        action = DropAction(self, obj_name)
        action()

    def find_and_validate_container(self, container_name: str) -> Optional[Item]:
        """Find a container and validate it's actually a container

        Returns the container Item if valid, None otherwise.
        Prints appropriate error messages.
        """
        if not container_name:
            return None

        container = self.find_item(container_name)
        if not container:
            print(f"You don't see any {container_name} here.")
            return None

        if 'CONTBIT' not in container.flags:
            print(f"You can't put things in the {container.desc}.")
            return None

        return container

    def do_put_in(self, obj_name: str, container_name: str):
        """Put an item in a container"""
        action = DropAction(self, obj_name, 'in', container_name)
        action()

    def do_take_from(self, obj_name: str, container_name: str):
        """Take an item from a container"""
        action = TakeAction(self, obj_name, 'from', container_name)
        action()

    def do_inventory(self, _=None, __=None):
        """Show inventory"""
        if not self.state.inventory:
            print("You are empty-handed.")
        else:
            print("You are carrying:")
            for item_name in self.state.inventory:
                item = self.items.get(item_name)
                if item:
                    print(f"  A {item.desc}")

    def do_examine(self, obj_name: str, _=None):
        """Examine an item"""
        action = ExamineAction(self, obj_name)
        action()

    def do_open(self, obj_name: str, _=None):
        """Open an object"""
        if not obj_name:
            print("Open what?")
            return

        item = self.find_item(obj_name)

        if not item:
            # Check for special cases
            if 'window' in obj_name and self.state.current_room == 'east_of_house':
                if self.state.flags['kitchen_window_open']:
                    print("It's already open.")
                else:
                    print("With great effort, you open the window far enough to allow entry.")
                    self.state.flags['kitchen_window_open'] = True
                return
            print(f"I don't see any {obj_name} here.")
            return

        if item.name == 'mailbox':
            # Move leaflet into mailbox (if not already taken)
            leaflet = self.items.get('leaflet')
            if leaflet and leaflet.location == 'mailbox':
                print("Opening the small mailbox reveals a leaflet.")
            else:
                print("The mailbox is empty.")
        elif item.name == 'trap_door':
            if self.state.flags['trap_door_open']:
                print("It's already open.")
            else:
                print("The door reluctantly opens to reveal a rickety staircase descending into darkness.")
                self.state.flags['trap_door_open'] = True
        elif 'window' in item.synonyms:
            if self.state.flags['kitchen_window_open']:
                print("It's already open.")
            else:
                print("With great effort, you open the window far enough to allow entry.")
                self.state.flags['kitchen_window_open'] = True
        else:
            print(f"You can't open the {item.desc}.")

    def do_read(self, obj_name: str, _=None):
        """Read an object"""
        if obj_name in ['leaflet', 'booklet', 'pamphlet']:
            self.do_examine('leaflet')
        else:
            print(f"I don't know how to read that.")

    def do_move(self, obj_name: str, _=None):
        """Move an object"""
        action = MoveAction(self, obj_name)
        action()

    def do_turn_on(self, obj_name: str, _=None):
        """Turn on a light source"""
        action = TurnOnOffAction(self, obj_name, turn_on=True)
        action()

    def do_turn_off(self, obj_name: str, _=None):
        """Turn off a light source"""
        action = TurnOnOffAction(self, obj_name, turn_on=False)
        action()

    def handle_turn_command(self, obj_name: str, modifier: str):
        """Handle 'turn on' and 'turn off' commands

        Handles both:
        - "turn on lantern" -> obj_name="on", modifier="lantern"
        - "turn lantern on" -> obj_name="lantern", modifier="on"
        """
        # Check if first word is on/off
        if obj_name in ['on', 'off']:
            if modifier:
                # "turn on lantern"
                action = TurnOnOffAction(self, modifier, turn_on=(obj_name == 'on'))
                action()
            else:
                print(f"Turn {obj_name} what?")
        # Check if second word is on/off
        elif modifier and modifier in ['on', 'off']:
            # "turn lantern on"
            action = TurnOnOffAction(self, obj_name, turn_on=(modifier == 'on'))
            action()
        else:
            print("You want to turn what on or off?")

    def do_quit(self, _=None, __=None):
        """Quit the game"""
        print(f"\nYour score is {self.state.score} (total of 350 points), in {self.state.moves} moves.")
        print("Do you wish to leave the game? (yes/no)")
        response = input("> ").strip().lower()
        if response in ['yes', 'y']:
            self.state.game_over = True
            print("\nThank you for playing Zork!")

    def do_score(self, _=None, __=None):
        """Show score"""
        print(f"Your score is {self.state.score} (total of 350 points), in {self.state.moves} moves.")
        rank = "Beginner"
        if self.state.score > 50:
            rank = "Amateur Adventurer"
        if self.state.score > 100:
            rank = "Novice Adventurer"
        if self.state.score > 200:
            rank = "Experienced Adventurer"
        if self.state.score > 300:
            rank = "Master"
        print(f"This gives you the rank of {rank}.")

    def do_verbose(self, _=None, __=None):
        """Enable verbose mode"""
        self.state.verbose_mode = True
        print("Maximum verbosity.")

    def do_brief(self, _=None, __=None):
        """Enable brief mode"""
        self.state.verbose_mode = False
        print("Brief descriptions.")

    def do_attack(self, target_name: str, weapon_name: str):
        """Attack an NPC with a weapon"""
        action = AttackAction(self, target_name, 'with', weapon_name)
        action()

    def do_debug(self, _=None, __=None):
        """Show debug information about game state"""
        print("\n" + "="*60)
        print("DEBUG: GAME STATE")
        print("="*60)

        # Current location
        room = self.get_current_room()
        print(f"\nCURRENT ROOM: {self.state.current_room}")
        print(f"  Short desc: {room.short_desc}")
        print(f"  Flags: {room.flags}")
        print(f"  Visited: {room.visited}")

        # Light status
        print(f"\nLIGHT STATUS:")
        print(f"  Room lit: {self.state.lit}")
        print(f"  Room naturally lit: {'ONBIT' in room.flags}")
        print(f"  Lamp battery: {self.state.lamp_battery} turns")
        print(f"  Lamp warned: {self.state.lamp_warned}")

        # Inventory
        print(f"\nINVENTORY ({len(self.state.inventory)} items):")
        for item_name in self.state.inventory:
            item = self.items.get(item_name)
            if item:
                flags_str = ', '.join(item.flags) if item.flags else 'none'
                print(f"  - {item_name:15s} flags: {flags_str}")

        # Items in current room
        print(f"\nITEMS IN ROOM ({len(room.items)} items):")
        for item_name in room.items:
            item = self.items.get(item_name)
            if item:
                flags_str = ', '.join(item.flags) if item.flags else 'none'
                hidden = ' (HIDDEN)' if 'NDESCBIT' in item.flags else ''
                print(f"  - {item_name:15s} flags: {flags_str}{hidden}")

        # Exits
        print(f"\nAVAILABLE EXITS ({len(room.exits)} exits):")
        for exit in room.exits:
            dest = exit.destination if exit.destination else "(blocked)"
            cond = " [conditional]" if exit.condition else ""
            print(f"  {exit.direction.name:10s} -> {dest}{cond}")

        # Game flags
        print(f"\nGAME FLAGS:")
        for flag, value in sorted(self.state.flags.items()):
            print(f"  {flag:25s}: {value}")

        # Score/stats
        print(f"\nGAME STATS:")
        print(f"  Score: {self.state.score}/350")
        print(f"  Moves: {self.state.moves}")
        print(f"  Verbose mode: {self.state.verbose_mode}")

        print("="*60 + "\n")

    def do_wait(self, _=None, __=None):
        """Wait - pass time"""
        print("Time passes...")
        self.state.moves += 1

    def do_close(self, obj_name: str, _=None):
        """Close a door, window, or container"""
        if not obj_name:
            print("Close what?")
            return

        # Special handling for kitchen window
        if 'window' in obj_name and self.state.current_room in ['east_of_house', 'kitchen']:
            if not self.state.flags['kitchen_window_open']:
                print("It's already closed.")
            else:
                print("The window is now closed.")
                self.state.flags['kitchen_window_open'] = False
            return

        item = self.find_item(obj_name)
        if not item:
            print(f"You don't see any {obj_name} here.")
            return

        # Check if it's closeable (container or door)
        if 'CONTBIT' not in item.flags and 'DOORBIT' not in item.flags:
            print(f"You can't close the {item.desc}.")
            return

        # Check if already closed
        if 'OPENBIT' not in item.flags:
            print("It is already closed.")
            return

        # Close it
        item.flags.discard('OPENBIT')

        if 'DOORBIT' in item.flags:
            print(f"The {item.desc} is now closed.")
        else:
            print("Closed.")

        # Check if room became dark
        was_lit = self.state.lit
        self.state.lit = self.is_room_lit()
        if was_lit and not self.state.lit:
            print("It is now pitch black.")

    def do_give(self, obj_name: str, target_name: str):
        """Give an item to an NPC"""
        action = GiveAction(self, obj_name, 'to', target_name)
        action()

    def do_climb(self, obj_name: str, _=None):
        """Climb something"""
        action = ClimbAction(self, obj_name)
        action()

    def do_throw(self, obj_name: str, target_name: str):
        """Throw an item"""
        action = ThrowAction(self, obj_name, 'at', target_name)
        action()

    def do_lock(self, obj_name: str, key_name: str):
        """Lock something with a key"""
        if not obj_name:
            print("Lock what?")
            return

        # Find the object to lock
        item = self.find_item(obj_name)
        if not item:
            print(f"You don't see any {obj_name} here.")
            return

        # Check if it's lockable (door or container)
        if 'DOORBIT' not in item.flags and 'CONTBIT' not in item.flags:
            print(f"You can't lock the {item.desc}.")
            return

        # Default behavior - most things can't be locked
        # (Specific items like grate can override this later)
        print("It doesn't seem to work.")

    def do_unlock(self, obj_name: str, key_name: str):
        """Unlock something with a key"""
        if not obj_name:
            print("Unlock what?")
            return

        # Find the object to unlock
        item = self.find_item(obj_name)
        if not item:
            print(f"You don't see any {obj_name} here.")
            return

        # Check if it's lockable (door or container)
        if 'DOORBIT' not in item.flags and 'CONTBIT' not in item.flags:
            print(f"You can't unlock the {item.desc}.")
            return

        # Default behavior - most things can't be unlocked
        # (Specific items like grate can override this later)
        print("It doesn't seem to work.")

    def execute_command(self, command: str):
        """Execute a parsed command"""
        verb, obj1, obj2 = self.parse_command(command)

        if not verb:
            return

        # Movement commands
        if verb in DIRECTION_ALIASES:
            self.do_go(verb, None)
            return

        # Map verbs to methods
        verb_map = {
            'look': self.do_look,
            'l': self.do_look,
            'examine': self.do_examine,
            'x': self.do_examine,
            'take': self.do_take,
            'get': self.do_take,
            'pick': self.do_take,
            'drop': self.do_drop,
            'put': self.do_drop,
            'put_in': self.do_put_in,  # Special parsed command
            'take_from': self.do_take_from,  # Special parsed command
            'inventory': self.do_inventory,
            'i': self.do_inventory,
            'open': self.do_open,
            'read': self.do_read,
            'move': self.do_move,
            'push': self.do_move,
            'turn': self.handle_turn_command,
            'light': self.do_turn_on,
            'attack': self.do_attack,
            'kill': self.do_attack,
            'fight': self.do_attack,
            'close': self.do_close,
            'wait': self.do_wait,
            'z': self.do_wait,
            'give': self.do_give,
            'give_to': self.do_give,  # Special parsed command
            'climb': self.do_climb,
            'throw': self.do_throw,
            'lock': self.do_lock,
            'unlock': self.do_unlock,
            'quit': self.do_quit,
            'q': self.do_quit,
            'score': self.do_score,
            'verbose': self.do_verbose,
            'brief': self.do_brief,
            'debug': self.do_debug,  # Debug command for development
        }

        action = verb_map.get(verb)
        if action:
            action(obj1, obj2)
        else:
            print("I don't understand that command.")

    def show_intro(self):
        """Show game introduction"""
        print("\n" + "="*70)
        print("ZORK I: The Great Underground Empire")
        print("Infocom interactive fiction - a fantasy story")
        print("Copyright (c) 1981, 1982, 1983, 1984, 1985, 1986 Infocom, Inc.")
        print("All rights reserved.")
        print("Python translation for educational purposes.")
        print("="*70)
        print()

    def run(self):
        """Main game loop"""
        self.show_intro()
        self.do_look()

        while not self.state.game_over:
            try:
                command = input("\n> ").strip()
                if command:
                    self.execute_command(command)
            except KeyboardInterrupt:
                print("\n\nInterrupted.")
                self.do_quit()
            except EOFError:
                print()
                self.do_quit()


def main():
    """Entry point"""
    game = ZorkGame()
    game.run()


if __name__ == '__main__':
    main()
