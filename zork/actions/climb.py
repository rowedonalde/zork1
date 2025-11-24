"""
Climb Action - handles climbing objects
"""

from typing import Optional, TYPE_CHECKING

from .base import SingleObjectAction

if TYPE_CHECKING:
    from ..game import ZorkGame


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
        assert self.direct_object is not None, "Direct object required"
        direct_obj: str = self.direct_object
        item = self.game.find_item(direct_obj)
        assert item is not None, "Item should exist after validation"

        # Special case for tree in forest path
        if item.name == 'tree' and self.game.state.current_room == 'path':
            self.game.state.current_room = 'up_a_tree'
            self.game.state.moves += 1
            self.game.do_look()
        else:
            print(f"You can't climb the {item.desc}.")
