"""
Take Action - handles picking up items from room or containers
"""

from typing import Optional, TYPE_CHECKING

from .base import BaseAction

if TYPE_CHECKING:
    from ..game import ZorkGame


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

        direct_obj: str = self.direct_object
        # If taking from container, find item in container
        if self.indirect_object:
            # Container validation happens in validate_indirect_object
            # Here we just check if item exists in the container
            indirect_obj: str = self.indirect_object
            container = self.game.find_item(indirect_obj)
            if not container:
                return False  # Error already printed in validate_indirect_object

            # Find item in container
            item = None
            for item_name, potential_item in self.game.items.items():
                if potential_item.location == container.name and potential_item.matches(direct_obj):
                    item = potential_item
                    break

            if not item:
                print(f"There's no {direct_obj} in the {container.desc}.")
                return False

            return True
        else:
            # Simple take - find item in room or inventory
            item = self.game.find_item(direct_obj)
            if not item:
                print(f"I don't see any {direct_obj} here.")
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

        indirect_obj: str = self.indirect_object
        container = self.game.find_item(indirect_obj)
        if not container:
            print(f"You don't see any {indirect_obj} here.")
            return False

        if 'CONTBIT' not in container.flags:
            print(f"You can't take things from the {container.desc}.")
            return False

        return True

    def effect(self):
        """Take the item and add to inventory"""
        assert self.direct_object is not None, "Direct object required"
        direct_obj: str = self.direct_object
        item = self.game.find_item(direct_obj)
        assert item is not None, "Item should exist after validation"

        if self.indirect_object:
            # Taking from container
            container = self.game.find_item(self.indirect_object)
            assert container is not None, "Container should exist after validation"
            # Find the actual item in container (by location)
            for item_name, potential_item in self.game.items.items():
                if potential_item.location == container.name and potential_item.matches(self.direct_object or ""):
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
