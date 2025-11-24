"""
Move Action - handles moving/pushing objects
"""

from typing import Optional, TYPE_CHECKING

from .base import SingleObjectAction

if TYPE_CHECKING:
    from ..game import ZorkGame


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
        assert self.direct_object is not None, "Direct object required"
        direct_obj: str = self.direct_object
        item = self.game.find_item(direct_obj)
        assert item is not None, "Item should exist after validation"

        # Special case for rug - reveals trap door
        if item.name == 'rug':
            print("With a great effort, the rug is moved to one side of the room, revealing the dusty cover of a closed trap door.")
            trap_door = self.game.items.get('trap_door')
            if trap_door:
                trap_door.flags.discard('NDESCBIT')
        else:
            print(f"You can't move the {item.desc}.")
