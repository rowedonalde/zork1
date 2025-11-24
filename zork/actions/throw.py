"""
Throw Action - handles throwing items at targets
"""

from typing import Optional, TYPE_CHECKING

from .base import TwoObjectAction

if TYPE_CHECKING:
    from ..game import ZorkGame


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
        assert self.direct_object is not None, "Direct object required"
        direct_obj: str = self.direct_object
        item = self.game.find_item(direct_obj)
        assert item is not None, "Item should exist after validation"

        if self.indirect_object:
            # Throwing at target
            target = self.game.find_item(self.indirect_object)
            assert target is not None, "Target should exist after validation"
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
