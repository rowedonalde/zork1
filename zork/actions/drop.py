"""
Drop Action - handles dropping items in room or containers
"""

from typing import Optional, TYPE_CHECKING

from .base import BaseAction

if TYPE_CHECKING:
    from ..game import ZorkGame


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

        direct_obj: str = self.direct_object
        item = self.game.find_item(direct_obj)
        if not item:
            if self.indirect_object:
                print(f"You don't see any {direct_obj} here.")
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

        indirect_obj: str = self.indirect_object
        container = self.game.find_item(indirect_obj)
        if not container:
            print(f"You don't see any {indirect_obj} here.")
            return False

        if 'CONTBIT' not in container.flags:
            print(f"The {container.desc} isn't a container.")
            return False

        return True

    def effect(self):
        """Drop the item in room or container"""
        assert self.direct_object is not None, "Direct object required"
        direct_obj: str = self.direct_object
        item = self.game.find_item(direct_obj)
        assert item is not None, "Item should exist after validation"
        self.game.state.remove_item(item.name)

        if self.indirect_object:
            # Putting in container
            container = self.game.find_item(self.indirect_object)
            assert container is not None, "Container should exist after validation"
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
