"""
Zork I - Game Engine

Main ZorkGame class that handles:
- Game loop and command processing
- Room navigation
- Object interaction
- Command parsing
"""

import re
import sys
from typing import Dict, List, Optional

from .models import Direction, DIRECTION_ALIASES, Item, Room, GameState
from .actions import *
from .world import initialize_world


class ZorkGame:
    """Main game engine"""

    def __init__(self):
        self.state = GameState()
        self.rooms: Dict[str, Room] = {}
        self.items: Dict[str, Item] = {}
        initialize_world(self)

    def get_current_room(self) -> Room:
        """Get the current room object"""
        return self.rooms[self.state.current_room]

    def is_room_lit(self) -> bool:
        """Check if the current room is lit

        Room is lit if:
        1. Room has ONBIT flag (naturally lit), OR
        2. Player has a light source that's on (LIGHTBIT + ONBIT)
        """
        room = self.get_current_room()

        # Check if room is naturally lit
        if 'ONBIT' in room.flags:
            return True

        # Check if player has an active light source
        for item_name in self.state.inventory:
            item = self.items.get(item_name)
            if item and 'LIGHTBIT' in item.flags and 'ONBIT' in item.flags:
                return True

        # Check if there's a light source in the room
        for item_name in room.items:
            item = self.items.get(item_name)
            if item and 'LIGHTBIT' in item.flags and 'ONBIT' in item.flags:
                return True

        return False

    def find_item(self, word: str, include_hidden: bool = True) -> Optional[Item]:
        """Find an item by name in current room or inventory"""
        room = self.get_current_room()

        # Check inventory
        for item_name in self.state.inventory:
            item = self.items.get(item_name)
            if item and item.matches(word):
                return item

        # Check current room (including hidden items if requested)
        for item_name in room.items:
            item = self.items.get(item_name)
            if item and item.matches(word):
                return item

        # Check items inside containers in room
        for item_name in room.items:
            container = self.items.get(item_name)
            if container and 'CONTBIT' in container.flags:
                # Check inside container
                for other_name, other_item in self.items.items():
                    if other_item.location == item_name and other_item.matches(word):
                        return other_item

        return None

    def parse_command(self, command: str) -> tuple:
        """Parse user command into verb and objects"""
        words = command.lower().strip().split()
        if not words:
            return None, None, None

        verb = words[0]
        obj1 = words[1] if len(words) > 1 else None
        obj2 = None

        # Special handling for "turn on/off object"
        if verb == 'turn' and len(words) >= 3 and words[1] in ['on', 'off']:
            obj1 = words[1]  # 'on' or 'off'
            obj2 = ' '.join(words[2:])  # object name
            return verb, obj1, obj2

        # Special handling for multi-word commands with prepositions
        if len(words) > 3:
            if verb == 'put' and 'in' in words:
                in_idx = words.index('in')
                obj1 = ' '.join(words[1:in_idx])  # item to put
                obj2 = ' '.join(words[in_idx+1:])  # container
                return 'put_in', obj1, obj2
            elif verb == 'take' and 'from' in words:
                from_idx = words.index('from')
                obj1 = ' '.join(words[1:from_idx])  # item to take
                obj2 = ' '.join(words[from_idx+1:])  # container
                return 'take_from', obj1, obj2
            elif verb == 'give' and 'to' in words:
                to_idx = words.index('to')
                obj1 = ' '.join(words[1:to_idx])  # item to give
                obj2 = ' '.join(words[to_idx+1:])  # target
                return 'give_to', obj1, obj2
            elif verb == 'throw' and 'at' in words:
                at_idx = words.index('at')
                obj1 = ' '.join(words[1:at_idx])  # item to throw
                obj2 = ' '.join(words[at_idx+1:])  # target
                return verb, obj1, obj2

        # Handle "verb obj1 with/using obj2" or "verb obj1 in/on obj2"
        if len(words) > 2:
            if words[2] in ['with', 'using', 'in', 'on', 'to', 'at', 'under']:
                obj2 = words[3] if len(words) > 3 else None
            else:
                obj1 = ' '.join(words[1:])

        return verb, obj1, obj2

    def do_look(self, _=None, __=None):
        """Look around the current room"""
        room = self.get_current_room()

        # Update light status
        self.state.lit = self.is_room_lit()

        if not self.state.lit:
            print("\nIt is pitch black. You are likely to be eaten by a grue.")
            return

        print(f"\n{room.short_desc}")

        if self.state.verbose_mode or not room.visited:
            print(room.desc)
            room.visited = True

        # List items in room
        visible_items = []
        for item_name in room.items:
            item = self.items.get(item_name)
            if item and 'NDESCBIT' not in item.flags:
                visible_items.append(item)

        if visible_items:
            print()
            for item in visible_items:
                print(f"There is a {item.desc} here.")

    def do_go(self, direction_word: str, _=None):
        """Move in a direction"""
        direction = DIRECTION_ALIASES.get(direction_word)
        if not direction:
            print("I don't understand that direction.")
            return

        room = self.get_current_room()
        exit = room.get_exit(direction)

        if not exit:
            print("You can't go that way.")
            return

        if exit.message:
            print(exit.message)
            return

        if exit.condition and not exit.condition():
            # Check if troll is blocking
            if self.state.current_room == 'troll_room' and direction in [Direction.EAST, Direction.WEST]:
                print("The troll fends you off with a menacing gesture.")
            elif direction in [Direction.WEST, Direction.IN] and self.state.current_room == 'east_of_house':
                print("The window is closed.")
            else:
                print("You can't go that way.")
            return

        if not exit.destination:
            print("You can't go that way.")
            return

        self.state.current_room = exit.destination
        self.state.moves += 1
        self.do_look()

    def do_take(self, obj_name: str, _=None):
        """Take an item"""
        action = TakeAction(self, obj_name)
        action()

    def do_drop(self, obj_name: str, _=None):
        """Drop an item"""
        action = DropAction(self, obj_name)
        action()

    def find_and_validate_container(self, container_name: str) -> Optional[Item]:
        """Find a container and validate it's actually a container

        Returns the container Item if valid, None otherwise.
        Prints appropriate error messages.
        """
        if not container_name:
            return None

        container = self.find_item(container_name)
        if not container:
            print(f"You don't see any {container_name} here.")
            return None

        if 'CONTBIT' not in container.flags:
            print(f"You can't put things in the {container.desc}.")
            return None

        return container

    def do_put_in(self, obj_name: str, container_name: str):
        """Put an item in a container"""
        action = DropAction(self, obj_name, 'in', container_name)
        action()

    def do_take_from(self, obj_name: str, container_name: str):
        """Take an item from a container"""
        action = TakeAction(self, obj_name, 'from', container_name)
        action()

    def do_inventory(self, _=None, __=None):
        """Show inventory"""
        if not self.state.inventory:
            print("You are empty-handed.")
        else:
            print("You are carrying:")
            for item_name in self.state.inventory:
                item = self.items.get(item_name)
                if item:
                    print(f"  A {item.desc}")

    def do_examine(self, obj_name: str, _=None):
        """Examine an item"""
        action = ExamineAction(self, obj_name)
        action()

    def do_open(self, obj_name: str, _=None):
        """Open an object"""
        action = OpenCloseAction(self, obj_name, is_opening=True)
        action()

    def do_read(self, obj_name: str, _=None):
        """Read an object"""
        if obj_name in ['leaflet', 'booklet', 'pamphlet']:
            self.do_examine('leaflet')
        else:
            print(f"I don't know how to read that.")

    def do_move(self, obj_name: str, _=None):
        """Move an object"""
        action = MoveAction(self, obj_name)
        action()

    def do_turn_on(self, obj_name: str, _=None):
        """Turn on a light source"""
        action = TurnOnOffAction(self, obj_name, turn_on=True)
        action()

    def do_turn_off(self, obj_name: str, _=None):
        """Turn off a light source"""
        action = TurnOnOffAction(self, obj_name, turn_on=False)
        action()

    def handle_turn_command(self, obj_name: str, modifier: str):
        """Handle 'turn on' and 'turn off' commands

        Handles both:
        - "turn on lantern" -> obj_name="on", modifier="lantern"
        - "turn lantern on" -> obj_name="lantern", modifier="on"
        """
        # Check if first word is on/off
        if obj_name in ['on', 'off']:
            if modifier:
                # "turn on lantern"
                action = TurnOnOffAction(self, modifier, turn_on=(obj_name == 'on'))
                action()
            else:
                print(f"Turn {obj_name} what?")
        # Check if second word is on/off
        elif modifier and modifier in ['on', 'off']:
            # "turn lantern on"
            action = TurnOnOffAction(self, obj_name, turn_on=(modifier == 'on'))
            action()
        else:
            print("You want to turn what on or off?")

    def do_quit(self, _=None, __=None):
        """Quit the game"""
        print(f"\nYour score is {self.state.score} (total of 350 points), in {self.state.moves} moves.")
        print("Do you wish to leave the game? (yes/no)")
        response = input("> ").strip().lower()
        if response in ['yes', 'y']:
            self.state.game_over = True
            print("\nThank you for playing Zork!")

    def do_score(self, _=None, __=None):
        """Show score"""
        print(f"Your score is {self.state.score} (total of 350 points), in {self.state.moves} moves.")
        rank = "Beginner"
        if self.state.score > 50:
            rank = "Amateur Adventurer"
        if self.state.score > 100:
            rank = "Novice Adventurer"
        if self.state.score > 200:
            rank = "Experienced Adventurer"
        if self.state.score > 300:
            rank = "Master"
        print(f"This gives you the rank of {rank}.")

    def do_verbose(self, _=None, __=None):
        """Enable verbose mode"""
        self.state.verbose_mode = True
        print("Maximum verbosity.")

    def do_brief(self, _=None, __=None):
        """Enable brief mode"""
        self.state.verbose_mode = False
        print("Brief descriptions.")

    def do_attack(self, target_name: str, weapon_name: str):
        """Attack an NPC with a weapon"""
        action = AttackAction(self, target_name, 'with', weapon_name)
        action()

    def do_debug(self, _=None, __=None):
        """Show debug information about game state"""
        print("\n" + "="*60)
        print("DEBUG: GAME STATE")
        print("="*60)

        # Current location
        room = self.get_current_room()
        print(f"\nCURRENT ROOM: {self.state.current_room}")
        print(f"  Short desc: {room.short_desc}")
        print(f"  Flags: {room.flags}")
        print(f"  Visited: {room.visited}")

        # Light status
        print(f"\nLIGHT STATUS:")
        print(f"  Room lit: {self.state.lit}")
        print(f"  Room naturally lit: {'ONBIT' in room.flags}")
        print(f"  Lamp battery: {self.state.lamp_battery} turns")
        print(f"  Lamp warned: {self.state.lamp_warned}")

        # Inventory
        print(f"\nINVENTORY ({len(self.state.inventory)} items):")
        for item_name in self.state.inventory:
            item = self.items.get(item_name)
            if item:
                flags_str = ', '.join(item.flags) if item.flags else 'none'
                print(f"  - {item_name:15s} flags: {flags_str}")

        # Items in current room
        print(f"\nITEMS IN ROOM ({len(room.items)} items):")
        for item_name in room.items:
            item = self.items.get(item_name)
            if item:
                flags_str = ', '.join(item.flags) if item.flags else 'none'
                hidden = ' (HIDDEN)' if 'NDESCBIT' in item.flags else ''
                print(f"  - {item_name:15s} flags: {flags_str}{hidden}")

        # Exits
        print(f"\nAVAILABLE EXITS ({len(room.exits)} exits):")
        for exit in room.exits:
            dest = exit.destination if exit.destination else "(blocked)"
            cond = " [conditional]" if exit.condition else ""
            print(f"  {exit.direction.name:10s} -> {dest}{cond}")

        # Game flags
        print(f"\nGAME FLAGS:")
        for flag, value in sorted(self.state.flags.items()):
            print(f"  {flag:25s}: {value}")

        # Score/stats
        print(f"\nGAME STATS:")
        print(f"  Score: {self.state.score}/350")
        print(f"  Moves: {self.state.moves}")
        print(f"  Verbose mode: {self.state.verbose_mode}")

        print("="*60 + "\n")

    def do_wait(self, _=None, __=None):
        """Wait - pass time"""
        print("Time passes...")
        self.state.moves += 1

    def do_close(self, obj_name: str, _=None):
        """Close a door, window, or container"""
        action = OpenCloseAction(self, obj_name, is_opening=False)
        action()

    def do_give(self, obj_name: str, target_name: str):
        """Give an item to an NPC"""
        action = GiveAction(self, obj_name, 'to', target_name)
        action()

    def do_climb(self, obj_name: str, _=None):
        """Climb something"""
        action = ClimbAction(self, obj_name)
        action()

    def do_throw(self, obj_name: str, target_name: str):
        """Throw an item"""
        action = ThrowAction(self, obj_name, 'at', target_name)
        action()

    def do_lock(self, obj_name: str, key_name: str):
        """Lock something with a key"""
        if not obj_name:
            print("Lock what?")
            return

        # Find the object to lock
        item = self.find_item(obj_name)
        if not item:
            print(f"You don't see any {obj_name} here.")
            return

        # Check if it's lockable (door or container)
        if 'DOORBIT' not in item.flags and 'CONTBIT' not in item.flags:
            print(f"You can't lock the {item.desc}.")
            return

        # Handle grating specifically
        if item.name == 'grating':
            if self.state.current_room == 'grating_clearing':
                print("You can't lock it from this side.")
                return

            if self.state.current_room == 'grating_room':
                if not self.state.flags.get('grating_unlocked', False):
                    print("The grating is already locked.")
                    return

                self.state.flags['grating_unlocked'] = False
                self.state.flags['grating_open'] = False
                print("The grating is locked.")
                return

        # Default behavior - most things can't be locked
        print("It doesn't seem to work.")

    def do_unlock(self, obj_name: str, key_name: str):
        """Unlock something with a key"""
        if not obj_name:
            print("Unlock what?")
            return

        # Find the object to unlock
        item = self.find_item(obj_name)
        if not item:
            print(f"You don't see any {obj_name} here.")
            return

        # Check if it's lockable (door or container)
        if 'DOORBIT' not in item.flags and 'CONTBIT' not in item.flags:
            print(f"You can't unlock the {item.desc}.")
            return

        # Check if we have the required key
        if not key_name:
            print("Unlock it with what?")
            return

        key_item = self.find_item(key_name)
        if not key_item:
            print(f"You don't see any {key_name} here.")
            return

        if key_item.location != 'inventory':
            print(f"You're not holding the {key_item.desc}.")
            return

        # Handle grating specifically
        if item.name == 'grating':
            if self.state.current_room == 'grating_clearing':
                print("You can't reach the lock from here.")
                return

            if self.state.current_room == 'grating_room':
                if key_item.name == 'skeleton_key':
                    if self.state.flags.get('grating_unlocked', False):
                        print("The grating is already unlocked.")
                        return

                    self.state.flags['grating_unlocked'] = True
                    print("The grating is unlocked.")
                    return
                else:
                    print(f"The {key_item.desc} doesn't fit the lock.")
                    return

        # Default behavior - most things can't be unlocked
        print("It doesn't seem to work.")

    def execute_command(self, command: str):
        """Execute a parsed command"""
        verb, obj1, obj2 = self.parse_command(command)

        if not verb:
            return

        # Movement commands
        if verb in DIRECTION_ALIASES:
            self.do_go(verb, None)
            return

        # Map verbs to methods
        verb_map = {
            'look': self.do_look,
            'l': self.do_look,
            'examine': self.do_examine,
            'x': self.do_examine,
            'take': self.do_take,
            'get': self.do_take,
            'pick': self.do_take,
            'drop': self.do_drop,
            'put': self.do_drop,
            'put_in': self.do_put_in,  # Special parsed command
            'take_from': self.do_take_from,  # Special parsed command
            'inventory': self.do_inventory,
            'i': self.do_inventory,
            'open': self.do_open,
            'read': self.do_read,
            'move': self.do_move,
            'push': self.do_move,
            'turn': self.handle_turn_command,
            'light': self.do_turn_on,
            'attack': self.do_attack,
            'kill': self.do_attack,
            'fight': self.do_attack,
            'close': self.do_close,
            'wait': self.do_wait,
            'z': self.do_wait,
            'give': self.do_give,
            'give_to': self.do_give,  # Special parsed command
            'climb': self.do_climb,
            'throw': self.do_throw,
            'lock': self.do_lock,
            'unlock': self.do_unlock,
            'quit': self.do_quit,
            'q': self.do_quit,
            'score': self.do_score,
            'verbose': self.do_verbose,
            'brief': self.do_brief,
            'debug': self.do_debug,  # Debug command for development
        }

        action = verb_map.get(verb)
        if action:
            action(obj1, obj2)
        else:
            print("I don't understand that command.")

    def show_intro(self):
        """Show game introduction"""
        print("\n" + "="*70)
        print("ZORK I: The Great Underground Empire")
        print("Infocom interactive fiction - a fantasy story")
        print("Copyright (c) 1981, 1982, 1983, 1984, 1985, 1986 Infocom, Inc.")
        print("All rights reserved.")
        print("Python translation for educational purposes.")
        print("="*70)
        print()

    def run(self):
        """Main game loop"""
        self.show_intro()
        self.do_look()

        while not self.state.game_over:
            try:
                command = input("\n> ").strip()
                if command:
                    self.execute_command(command)
            except KeyboardInterrupt:
                print("\n\nInterrupted.")
                self.do_quit()
            except EOFError:
                print()
                self.do_quit()


def main():
    """Entry point"""
    game = ZorkGame()
    game.run()


if __name__ == '__main__':
    main()
