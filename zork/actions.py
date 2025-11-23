"""
Zork I - Action Classes

All action classes that handle player commands:
- BaseAction and specialized base classes
- Concrete action implementations (TurnOnOffAction, TakeAction, etc.)
"""

from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass

from .models import Item

if TYPE_CHECKING:
    from .game import ZorkGame

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


class OpenCloseAction(BaseAction):
    """Action to open or close doors, windows, and containers"""

    def __init__(self, game: 'ZorkGame', direct_object: Optional[str], is_opening: bool):
        super().__init__(game, direct_object)
        self.is_opening = is_opening

    @staticmethod
    def from_command(command: str, game: 'ZorkGame', is_opening: bool) -> 'OpenCloseAction':
        """Factory method to create OpenCloseAction from command"""
        tokens = command.split()
        direct_object = ' '.join(tokens[1:]) if len(tokens) > 1 else None
        return OpenCloseAction(game, direct_object, is_opening)

    def validate_direct_object(self) -> bool:
        """Validate object exists or is a special case"""
        if not self.direct_object:
            action_word = "open" if self.is_opening else "close"
            print(f"{action_word.capitalize()} what?")
            return False

        # Special case: window can be referenced without being a found item
        if 'window' in self.direct_object:
            return True

        item = self.game.find_item(self.direct_object)
        if not item:
            print(f"{'I don' if self.is_opening else 'You don'}\'t see any {self.direct_object} here.")
            return False

        return True

    def effect(self):
        """Open or close the object"""
        item = self.game.find_item(self.direct_object)

        # Special case: Kitchen window (at east_of_house or in kitchen)
        if 'window' in self.direct_object:
            if self.is_opening:
                # Opening window
                if self.game.state.current_room == 'east_of_house' or (item and 'window' in item.synonyms):
                    if self.game.state.flags['kitchen_window_open']:
                        print("It's already open.")
                    else:
                        print("With great effort, you open the window far enough to allow entry.")
                        self.game.state.flags['kitchen_window_open'] = True
                else:
                    if item:
                        print(f"You can't open the {item.desc}.")
                    else:
                        print(f"I don't see any {self.direct_object} here.")
            else:
                # Closing window
                if self.game.state.current_room in ['east_of_house', 'kitchen']:
                    if not self.game.state.flags['kitchen_window_open']:
                        print("It's already closed.")
                    else:
                        print("The window is now closed.")
                        self.game.state.flags['kitchen_window_open'] = False
                elif item:
                    print(f"You can't close the {item.desc}.")
                else:
                    print(f"You don't see any {self.direct_object} here.")
            return

        if not item:
            return

        # Special case: Mailbox
        if item.name == 'mailbox':
            if self.is_opening:
                leaflet = self.game.items.get('leaflet')
                if leaflet and leaflet.location == 'mailbox':
                    print("Opening the small mailbox reveals a leaflet.")
                else:
                    print("The mailbox is empty.")
            else:
                # Closing mailbox
                if 'OPENBIT' not in item.flags:
                    print("It is already closed.")
                else:
                    item.flags.discard('OPENBIT')
                    print("Closed.")
            return

        # Special case: Trap door
        if item.name == 'trap_door':
            if self.is_opening:
                if self.game.state.flags['trap_door_open']:
                    print("It's already open.")
                else:
                    print("The door reluctantly opens to reveal a rickety staircase descending into darkness.")
                    self.game.state.flags['trap_door_open'] = True
            else:
                if not self.game.state.flags['trap_door_open']:
                    print("It's already closed.")
                else:
                    print("The trap door is now closed.")
                    self.game.state.flags['trap_door_open'] = False
            return

        # Generic items - check if they can be opened/closed
        if self.is_opening:
            # Opening generic item
            if 'CONTBIT' not in item.flags and 'DOORBIT' not in item.flags:
                print(f"You can't open the {item.desc}.")
                return

            if 'OPENBIT' in item.flags:
                print("It's already open.")
                return

            item.flags.add('OPENBIT')
            if 'DOORBIT' in item.flags:
                print(f"The {item.desc} is now open.")
            else:
                print("Opened.")
        else:
            # Closing generic item
            if 'CONTBIT' not in item.flags and 'DOORBIT' not in item.flags:
                print(f"You can't close the {item.desc}.")
                return

            if 'OPENBIT' not in item.flags:
                print("It is already closed.")
                return

            item.flags.discard('OPENBIT')
            if 'DOORBIT' in item.flags:
                print(f"The {item.desc} is now closed.")
            else:
                print("Closed.")

            # Check if room became dark after closing
            was_lit = self.game.state.lit
            self.game.state.lit = self.game.is_room_lit()
            if was_lit and not self.game.state.lit:
                print("It is now pitch black.")


