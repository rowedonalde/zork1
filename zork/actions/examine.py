"""
Examine Action - handles examining objects
"""

from typing import Optional, TYPE_CHECKING

from .base import SingleObjectAction

if TYPE_CHECKING:
    from ..game import ZorkGame


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
