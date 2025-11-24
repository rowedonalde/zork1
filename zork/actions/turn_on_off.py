"""
Turn On/Off Action - handles lighting and extinguishing light sources
"""

from typing import Optional, TYPE_CHECKING

from .base import BaseAction

if TYPE_CHECKING:
    from ..game import ZorkGame


class TurnOnOffAction(BaseAction):
    """Action to turn light sources on or off"""

    def __init__(self, game: 'ZorkGame', direct_object: Optional[str], turn_on: bool):
        super().__init__(game, direct_object)
        self.turn_on = turn_on

    @staticmethod
    def from_command(command: str, game: 'ZorkGame', turn_on: bool) -> 'TurnOnOffAction':  # type: ignore[override]
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

        direct_obj: str = self.direct_object
        item = self.game.find_item(direct_obj)
        if not item:
            print(f"I don't see any {direct_obj} here.")
            return False

        if 'LIGHTBIT' not in item.flags:
            print(f"You can't turn that {'on' if self.turn_on else 'off'}.")
            return False

        return True

    def effect(self):
        """Toggle the light source and update room lighting"""
        assert self.direct_object is not None, "Direct object required"
        direct_obj: str = self.direct_object
        item = self.game.find_item(direct_obj)
        assert item is not None, "Item should exist after validation"
        is_on = 'ONBIT' in item.flags

        if self.turn_on:
            if is_on:
                print("It is already on.")
                return

            # Check if this is the lantern and battery is dead (matching ZIL LANTERN routine)
            if item.name == 'lantern' and self.game.state.lamp_battery <= 0:
                print("A burned-out lamp won't light.")
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
