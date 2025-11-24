"""
Open/Close Action - handles opening and closing doors, windows, and containers
"""

from typing import Optional, TYPE_CHECKING

from .base import BaseAction

if TYPE_CHECKING:
    from ..game import ZorkGame


class OpenCloseAction(BaseAction):
    """Action to open or close doors, windows, and containers"""

    def __init__(self, game: 'ZorkGame', direct_object: Optional[str], is_opening: bool):
        super().__init__(game, direct_object)
        self.is_opening = is_opening

    @staticmethod
    def from_command(command: str, game: 'ZorkGame', is_opening: bool) -> 'OpenCloseAction':  # type: ignore[override]
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
        if self.direct_object and 'window' in self.direct_object:
            return True

        item = self.game.find_item(self.direct_object or "")
        if not item:
            print(f"{'I don' if self.is_opening else 'You don'}\'t see any {self.direct_object} here.")
            return False

        return True

    def effect(self):
        """Open or close the object"""
        item = self.game.find_item(self.direct_object or "")

        # Special case: Kitchen window (at east_of_house or in kitchen)
        if self.direct_object and 'window' in self.direct_object:
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

        # Special case: Grating
        if item.name == 'grating':
            if self.is_opening:
                # Check if it's unlocked first
                if not self.game.state.flags.get('grating_unlocked', False):
                    if self.game.state.current_room == 'grating_clearing':
                        print("Above you is a grating locked with a skull-and-crossbones lock.")
                    else:
                        print("The grating is locked.")
                    return

                if self.game.state.flags['grating_open']:
                    print("It's already open.")
                else:
                    if self.game.state.current_room == 'grating_clearing':
                        print("The grating opens.")
                    else:
                        print("The grating opens to reveal trees above you.")
                    self.game.state.flags['grating_open'] = True
            else:
                # Closing
                if not self.game.state.flags['grating_open']:
                    print("It's already closed.")
                else:
                    print("The grating is closed.")
                    self.game.state.flags['grating_open'] = False
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
