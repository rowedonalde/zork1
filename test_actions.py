#!/usr/bin/env python3
"""
Unit tests for Zork action classes

Run with: python -m unittest test_actions
Or: python test_actions.py
"""

import unittest
import sys
from io import StringIO
from zork import ZorkGame, TurnOnOffAction, TakeAction, DropAction
from zork import ExamineAction, GiveAction, AttackAction, ThrowAction
from zork import ClimbAction, MoveAction, OpenCloseAction


class TestBaseActionClasses(unittest.TestCase):
    """Test the base action class hierarchy"""

    def setUp(self):
        """Create a fresh game instance for each test"""
        self.game = ZorkGame()
        self.game.state.current_room = 'living_room'

    def capture_output(self, action):
        """Capture print output from an action"""
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            action()
            output = sys.stdout.getvalue()
            return output
        finally:
            sys.stdout = old_stdout


class TestTurnOnOffAction(TestBaseActionClasses):
    """Test light toggle actions"""

    def test_turn_on_lantern(self):
        """Test turning on the lantern"""
        self.game.do_take('lantern')
        action = TurnOnOffAction(self.game, 'lantern', turn_on=True)
        output = self.capture_output(action)

        self.assertIn('brass lantern is now on', output)
        self.assertIn('ONBIT', self.game.items['lantern'].flags)

    def test_turn_off_lantern(self):
        """Test turning off the lantern"""
        self.game.do_take('lantern')
        self.game.items['lantern'].flags.add('ONBIT')

        action = TurnOnOffAction(self.game, 'lantern', turn_on=False)
        output = self.capture_output(action)

        self.assertIn('brass lantern is now off', output)
        self.assertNotIn('ONBIT', self.game.items['lantern'].flags)

    def test_turn_on_already_on(self):
        """Test turning on an already-on light"""
        self.game.do_take('lantern')
        self.game.items['lantern'].flags.add('ONBIT')

        action = TurnOnOffAction(self.game, 'lantern', turn_on=True)
        output = self.capture_output(action)

        self.assertIn('already on', output)

    def test_turn_on_non_light(self):
        """Test turning on something that isn't a light"""
        action = TurnOnOffAction(self.game, 'sword', turn_on=True)
        output = self.capture_output(action)

        self.assertIn("can't turn that on", output)


class TestTakeAction(TestBaseActionClasses):
    """Test take/get actions"""

    def test_take_item(self):
        """Test taking an item from the room"""
        action = TakeAction(self.game, 'sword')
        output = self.capture_output(action)

        self.assertIn('Taken', output)
        self.assertIn('sword', self.game.state.inventory)

    def test_take_from_container(self):
        """Test taking an item from a container"""
        self.game.state.current_room = 'west_of_house'
        action = TakeAction(self.game, 'leaflet', 'from', 'mailbox')
        output = self.capture_output(action)

        self.assertIn('take the leaflet from the small mailbox', output)
        self.assertIn('leaflet', self.game.state.inventory)

    def test_take_already_have(self):
        """Test taking an item already in inventory"""
        self.game.do_take('sword')
        action = TakeAction(self.game, 'sword')
        output = self.capture_output(action)

        self.assertIn('already have', output)

    def test_take_non_takeable(self):
        """Test taking a non-takeable item"""
        action = TakeAction(self.game, 'rug')
        output = self.capture_output(action)

        self.assertIn("can't take", output)


class TestDropAction(TestBaseActionClasses):
    """Test drop/put actions"""

    def test_drop_item(self):
        """Test dropping an item"""
        self.game.do_take('sword')
        action = DropAction(self.game, 'sword')
        output = self.capture_output(action)

        self.assertIn('Dropped', output)
        self.assertNotIn('sword', self.game.state.inventory)
        self.assertIn('sword', self.game.get_current_room().items)

    def test_put_in_container(self):
        """Test putting an item in a container"""
        self.game.do_take('lantern')
        action = DropAction(self.game, 'lantern', 'in', 'trophy_case')
        output = self.capture_output(action)

        self.assertIn('put the brass lantern in the trophy case', output)
        self.assertNotIn('lantern', self.game.state.inventory)

    def test_put_in_trophy_case_scoring(self):
        """Test that putting treasures in trophy case awards points"""
        self.game.do_take('jewels')
        initial_score = self.game.state.score

        action = DropAction(self.game, 'jewels', 'in', 'trophy_case')
        output = self.capture_output(action)

        self.assertIn('score has just gone up', output)
        self.assertGreater(self.game.state.score, initial_score)

    def test_drop_not_holding(self):
        """Test dropping an item not in inventory"""
        action = DropAction(self.game, 'sword')
        output = self.capture_output(action)

        self.assertIn("aren't holding", output)


class TestExamineAction(TestBaseActionClasses):
    """Test examine/look actions"""

    def test_examine_leaflet(self):
        """Test examining the leaflet shows special text"""
        self.game.state.current_room = 'west_of_house'
        action = ExamineAction(self.game, 'leaflet')
        output = self.capture_output(action)

        self.assertIn('WELCOME TO ZORK', output)

    def test_examine_mailbox(self):
        """Test examining the mailbox"""
        self.game.state.current_room = 'west_of_house'
        action = ExamineAction(self.game, 'mailbox')
        output = self.capture_output(action)

        self.assertIn('mailbox', output)

    def test_examine_generic_item(self):
        """Test examining a generic item"""
        action = ExamineAction(self.game, 'sword')
        output = self.capture_output(action)

        self.assertIn('nothing special', output)

    def test_examine_no_object(self):
        """Test examine with no object defaults to look"""
        action = ExamineAction(self.game, None)
        output = self.capture_output(action)

        self.assertIn('Living Room', output)


class TestGiveAction(TestBaseActionClasses):
    """Test give action"""

    def test_give_to_npc(self):
        """Test giving an item to an NPC"""
        # Take sword first while in living room
        self.game.do_take('sword')
        # Then move to troll room
        self.game.state.current_room = 'troll_room'

        action = GiveAction(self.game, 'sword', 'to', 'troll')
        output = self.capture_output(action)

        self.assertIn('refuses it politely', output)

    def test_give_not_holding(self):
        """Test giving an item not in inventory"""
        self.game.state.current_room = 'troll_room'

        action = GiveAction(self.game, 'sword', 'to', 'troll')
        output = self.capture_output(action)

        self.assertIn("don't have any", output)

    def test_give_to_non_actor(self):
        """Test giving to a non-NPC"""
        self.game.do_take('sword')

        action = GiveAction(self.game, 'sword', 'to', 'rug')
        output = self.capture_output(action)

        self.assertIn("can't give", output)


class TestAttackAction(TestBaseActionClasses):
    """Test attack action"""

    def test_attack_with_weapon(self):
        """Test attacking with a weapon"""
        # Take sword while in living room
        self.game.do_take('sword')
        # Then move to troll room
        self.game.state.current_room = 'troll_room'

        action = AttackAction(self.game, 'troll', 'with', 'sword')
        output = self.capture_output(action)

        # Should either kill troll or miss (50% chance each)
        self.assertTrue('swing' in output or 'falls dead' in output or 'parries' in output)

    def test_attack_without_weapon(self):
        """Test attacking without a weapon"""
        self.game.state.current_room = 'troll_room'

        action = AttackAction(self.game, 'troll', None, None)
        output = self.capture_output(action)

        self.assertIn('bare hands', output)

    def test_attack_non_actor(self):
        """Test attacking a non-NPC"""
        self.game.do_take('sword')
        action = AttackAction(self.game, 'rug', 'with', 'sword')
        output = self.capture_output(action)

        self.assertIn("can't attack", output)

    def test_attack_with_non_weapon(self):
        """Test attacking with a non-weapon"""
        # Take lantern while in living room
        self.game.do_take('lantern')
        # Then move to troll room
        self.game.state.current_room = 'troll_room'

        action = AttackAction(self.game, 'troll', 'with', 'lantern')
        output = self.capture_output(action)

        self.assertIn("isn't much of a weapon", output)


class TestThrowAction(TestBaseActionClasses):
    """Test throw action"""

    def test_throw_at_target(self):
        """Test throwing an item at a target"""
        # Take sword while in living room
        self.game.do_take('sword')
        # Then move to troll room
        self.game.state.current_room = 'troll_room'

        action = ThrowAction(self.game, 'sword', 'at', 'troll')
        output = self.capture_output(action)

        self.assertIn('throw', output)
        self.assertIn('bounces harmlessly', output)
        self.assertNotIn('sword', self.game.state.inventory)

    def test_throw_without_target(self):
        """Test throwing without a target"""
        self.game.do_take('sword')

        action = ThrowAction(self.game, 'sword', None, None)
        output = self.capture_output(action)

        self.assertIn('Thrown', output)
        self.assertNotIn('sword', self.game.state.inventory)

    def test_throw_not_holding(self):
        """Test throwing an item not in inventory"""
        action = ThrowAction(self.game, 'sword', 'at', 'troll')
        output = self.capture_output(action)

        self.assertIn("aren't holding", output)


class TestClimbAction(TestBaseActionClasses):
    """Test climb action"""

    def test_climb_tree(self):
        """Test climbing the tree"""
        self.game.state.current_room = 'path'

        action = ClimbAction(self.game, 'tree')
        self.capture_output(action)

        self.assertEqual(self.game.state.current_room, 'up_a_tree')

    def test_climb_non_climbable(self):
        """Test climbing a non-climbable object"""
        action = ClimbAction(self.game, 'rug')
        output = self.capture_output(action)

        self.assertIn("can't climb", output)


class TestMoveAction(TestBaseActionClasses):
    """Test move/push action"""

    def test_move_rug(self):
        """Test moving the rug reveals trap door"""
        action = MoveAction(self.game, 'rug')
        output = self.capture_output(action)

        self.assertIn('trap door', output)
        trap_door = self.game.items.get('trap_door')
        self.assertNotIn('NDESCBIT', trap_door.flags)

    def test_move_non_moveable(self):
        """Test moving a non-moveable object"""
        action = MoveAction(self.game, 'sword')
        output = self.capture_output(action)

        self.assertIn("can't move", output)


class TestOpenCloseAction(TestBaseActionClasses):
    """Test open/close actions"""

    def test_open_window_at_east_of_house(self):
        """Test opening the window at east of house"""
        self.game.state.current_room = 'east_of_house'
        action = OpenCloseAction(self.game, 'window', is_opening=True)
        output = self.capture_output(action)

        self.assertIn('open the window far enough to allow entry', output)
        self.assertTrue(self.game.state.flags['kitchen_window_open'])

    def test_open_window_already_open(self):
        """Test opening an already-open window"""
        self.game.state.current_room = 'east_of_house'
        self.game.state.flags['kitchen_window_open'] = True

        action = OpenCloseAction(self.game, 'window', is_opening=True)
        output = self.capture_output(action)

        self.assertIn('already open', output)

    def test_close_window(self):
        """Test closing the window"""
        self.game.state.current_room = 'east_of_house'
        self.game.state.flags['kitchen_window_open'] = True

        action = OpenCloseAction(self.game, 'window', is_opening=False)
        output = self.capture_output(action)

        self.assertIn('window is now closed', output)
        self.assertFalse(self.game.state.flags['kitchen_window_open'])

    def test_close_window_already_closed(self):
        """Test closing an already-closed window"""
        self.game.state.current_room = 'east_of_house'
        self.game.state.flags['kitchen_window_open'] = False

        action = OpenCloseAction(self.game, 'window', is_opening=False)
        output = self.capture_output(action)

        self.assertIn('already closed', output)

    def test_open_mailbox(self):
        """Test opening the mailbox shows leaflet"""
        self.game.state.current_room = 'west_of_house'
        action = OpenCloseAction(self.game, 'mailbox', is_opening=True)
        output = self.capture_output(action)

        self.assertIn('reveals a leaflet', output)

    def test_open_mailbox_empty(self):
        """Test opening empty mailbox"""
        self.game.state.current_room = 'west_of_house'
        # Take the leaflet first using TakeAction
        take_action = TakeAction(self.game, 'leaflet', 'from', 'mailbox')
        self.capture_output(take_action)

        action = OpenCloseAction(self.game, 'mailbox', is_opening=True)
        output = self.capture_output(action)

        self.assertIn('mailbox is empty', output)

    def test_open_trap_door(self):
        """Test opening the trap door"""
        # First reveal the trap door by moving the rug
        self.game.do_move('rug')

        action = OpenCloseAction(self.game, 'trap_door', is_opening=True)
        output = self.capture_output(action)

        self.assertIn('reluctantly opens', output)
        self.assertIn('rickety staircase', output)
        self.assertTrue(self.game.state.flags['trap_door_open'])

    def test_open_trap_door_already_open(self):
        """Test opening an already-open trap door"""
        self.game.do_move('rug')
        self.game.state.flags['trap_door_open'] = True

        action = OpenCloseAction(self.game, 'trap_door', is_opening=True)
        output = self.capture_output(action)

        self.assertIn('already open', output)

    def test_close_trap_door(self):
        """Test closing the trap door"""
        self.game.do_move('rug')
        self.game.state.flags['trap_door_open'] = True

        action = OpenCloseAction(self.game, 'trap_door', is_opening=False)
        output = self.capture_output(action)

        self.assertIn('trap door is now closed', output)
        self.assertFalse(self.game.state.flags['trap_door_open'])

    def test_open_non_openable(self):
        """Test opening something that can't be opened"""
        action = OpenCloseAction(self.game, 'sword', is_opening=True)
        output = self.capture_output(action)

        self.assertIn("can't open", output)

    def test_close_non_closeable(self):
        """Test closing something that can't be closed"""
        action = OpenCloseAction(self.game, 'sword', is_opening=False)
        output = self.capture_output(action)

        self.assertIn("can't close", output)

    def test_open_no_object(self):
        """Test open with no object"""
        action = OpenCloseAction(self.game, None, is_opening=True)
        output = self.capture_output(action)

        self.assertIn('Open what', output)

    def test_close_no_object(self):
        """Test close with no object"""
        action = OpenCloseAction(self.game, None, is_opening=False)
        output = self.capture_output(action)

        self.assertIn('Close what', output)


if __name__ == '__main__':
    unittest.main()
