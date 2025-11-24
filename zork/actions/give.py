"""
Give Action - handles giving items to NPCs
"""

from typing import Optional, TYPE_CHECKING

from .base import TwoObjectAction

if TYPE_CHECKING:
    from ..game import ZorkGame


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
        assert self.direct_object is not None and self.indirect_object is not None, "Objects required"
        direct_obj: str = self.direct_object
        indirect_obj: str = self.indirect_object
        item = self.game.find_item(direct_obj)
        assert item is not None, "Item should exist after validation"
        target = self.game.find_item(indirect_obj)
        assert target is not None, "Target should exist after validation"

        # Default behavior - NPC refuses (can be overridden for specific NPCs later)
        print(f"The {target.desc} refuses it politely.")
