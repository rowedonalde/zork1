"""
Attack Action - handles attacking NPCs with weapons
"""

from typing import Optional, TYPE_CHECKING

from .base import TwoObjectAction
from ..models import Item

if TYPE_CHECKING:
    from ..game import ZorkGame


class AttackAction(TwoObjectAction):
    """Action to attack an NPC with a weapon"""

    def __init__(self, game: 'ZorkGame', direct_object: Optional[str],
                 preposition: Optional[str], indirect_object: Optional[str]):
        super().__init__(game, direct_object, preposition, indirect_object,
                        require_direct=True, require_indirect=False)

    @staticmethod
    def from_command(command: str, game: 'ZorkGame') -> 'AttackAction':
        """Factory method to create AttackAction from command"""
        tokens = command.split()

        if 'with' in tokens:
            with_idx = tokens.index('with')
            direct_object = ' '.join(tokens[1:with_idx])
            preposition = 'with'
            indirect_object = ' '.join(tokens[with_idx+1:])
        else:
            # Just "attack troll" without weapon
            direct_object = ' '.join(tokens[1:]) if len(tokens) > 1 else None
            preposition = None
            indirect_object = None

        return AttackAction(game, direct_object, preposition, indirect_object)

    def validate_direct_object(self) -> bool:
        """Validate target exists and is attackable"""
        if not self.direct_object:
            print("Attack what?")
            return False

        target = self.game.find_item(self.direct_object)
        if not target:
            print(f"You don't see any {self.direct_object} here.")
            return False

        if 'ACTORBIT' not in target.flags:
            print(f"You can't attack the {target.desc}.")
            return False

        return True

    def validate_indirect_object(self) -> bool:
        """Validate weapon if specified"""
        if not self.indirect_object:
            return True  # Weapon is optional (validated in effect)

        weapon = self.game.find_item(self.indirect_object)
        if not weapon:
            print(f"You don't have any {self.indirect_object}.")
            return False

        if not self.game.state.has_item(weapon.name):
            print(f"You aren't holding the {weapon.desc}.")
            return False

        if 'WEAPONBIT' not in weapon.flags:
            print(f"The {weapon.desc} isn't much of a weapon.")
            return False

        return True

    def effect(self):
        """Perform the attack"""
        import random

        assert self.direct_object is not None, "Direct object required"
        direct_obj: str = self.direct_object
        target = self.game.find_item(direct_obj)
        assert target is not None, "Target should exist after validation"
        weapon = self.game.find_item(self.indirect_object) if self.indirect_object else None

        # Handle troll specifically
        if target.name == 'troll':
            if not weapon:
                print("With what? Your bare hands?")
                return

            # Simple combat - 50% chance of killing troll
            if random.random() < 0.5:
                print(f"You swing the {weapon.desc} at the troll.")
                print("The troll is struck by your blow and falls dead!")
                print("The troll's body dissolves into a cloud of greasy black smoke.")

                # Remove troll
                room = self.game.get_current_room()
                if target.name in room.items:
                    room.items.remove(target.name)

                # Set troll flag to open passages
                self.game.state.flags['troll_flag'] = True

                # Drop the axe
                room.items.append('axe')
                if 'axe' not in self.game.items:
                    self.game.items['axe'] = Item(
                        name='axe',
                        desc='bloody axe',
                        synonyms=['weapon'],
                        adjectives=['bloody'],
                        location=room.name,
                        takeable=True,
                        flags={'TAKEBIT', 'WEAPONBIT'},
                        size=25
                    )
                else:
                    self.game.items['axe'].location = room.name
            else:
                print(f"You swing the {weapon.desc} at the troll.")
                print("The troll deftly parries your blow and grins menacingly.")
                print("The troll doesn't look amused.")
        else:
            print(f"You can't attack the {target.desc}.")
