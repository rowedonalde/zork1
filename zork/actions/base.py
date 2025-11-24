"""
Zork I - Action Base Classes

Base classes for all action implementations:
- BaseAction: Abstract base for all actions
- SingleObjectAction: For actions with one object (examine, climb, move)
- TwoObjectAction: For actions with two objects (give X to Y, attack X with Y)
- ToggleAction: For paired on/off or open/close actions
"""

from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass

from ..models import Item

if TYPE_CHECKING:
    from ..game import ZorkGame


@dataclass
class BaseAction:
    """Abstract base class for an action that can be performed"""
    game: 'ZorkGame'
    direct_object: Optional[str] = None
    preposition: Optional[str] = None
    indirect_object: Optional[str] = None

    @staticmethod
    def from_command(command: str, game: 'ZorkGame', **kwargs) -> 'BaseAction':  # type: ignore[misc]
        """
        Factory method to create action from command string

        `command` is the full user input command, e.g. "take sword from chest".
        `**kwargs` allows subclasses to accept additional parameters (e.g., turn_on, is_opening).

        Example:
            def from_command(command: str, game: 'ZorkGame', **kwargs) -> 'SomeAction':
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

        direct_obj: str = self.direct_object
        if not self.game.find_item(direct_obj):
            print(f"I don't see any {direct_obj} here.")
            return False
        return True

    def validate_indirect_object(self) -> bool:
        """Confirm presence of indirect object"""
        if not self.indirect_object:
            return True  # No indirect object to validate

        indirect_obj: str = self.indirect_object
        if not self.game.find_item(indirect_obj):
            print(f"I don't see any {indirect_obj} here.")
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

        direct_obj: str = self.direct_object
        item = self.game.find_item(direct_obj)
        if not item:
            if self.allow_missing:
                return True  # Subclass will handle missing object
            print(f"You don't see any {direct_obj} here.")
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

        direct_obj: str = self.direct_object
        item = self.game.find_item(direct_obj)
        if not item:
            print(f"You don't see any {direct_obj} here.")
            return False

        return True

    def validate_indirect_object(self) -> bool:
        """Standard validation for indirect object"""
        if not self.indirect_object:
            if self.require_indirect:
                print(f"{self.__class__.__name__.replace('Action', '')} what {self.preposition} what?")
                return False
            return True

        indirect_obj: str = self.indirect_object
        item = self.game.find_item(indirect_obj)
        if not item:
            print(f"You don't see any {indirect_obj} here.")
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
