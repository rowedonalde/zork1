# Zork I Python Translation Guidelines

## Core Principle: Player Experience Fidelity

**The translation to Python should be as feature-accurate as possible from the player's perspective.**

### What This Means:

1. **Identical Output**: Given the same user input, the Python version should produce identical output to the original ZIL version. Someone who is incredibly familiar with Zork shouldn't be able to pick out any differences.

2. **Match Original Behavior Exactly**:
   - Warning messages must use the exact same text
   - Thresholds must match (e.g., lamp warnings at 100, 70, 15 turns, not 50, 30, 10)
   - Game mechanics must behave identically
   - Error messages must match the original phrasing

3. **Implementation Can Differ**: It's OK if the implementation is different under the hood:
   - ✅ Using `lamp_battery <= 0` check instead of a `RMUNGBIT` flag is fine
   - ✅ Using Python classes instead of ZIL routines is fine
   - ✅ Using different data structures is fine
   - ❌ But the player-facing behavior must be identical

4. **When in Doubt**: Check the original ZIL source and match it exactly.

### Examples:

**Good**: Implementing lamp battery with different code structure but same thresholds/messages
**Bad**: Changing warning thresholds from 100/70/15 to 50/30/10
**Bad**: Paraphrasing messages like "The lamp appears a bit dimmer" → "The brass lantern is getting dim"

### Testing Standard:

A Zork veteran should be able to play through the game and not notice any differences from the original.

# Other project-related instructions:
- When using the `python-zork-language-server - edit_file` tool, print out the newText so it's readable to me. Otherwise, it's just a long string with a bunch of escaped chars that's hard for me to understand and verify. The UX here should be closer to the diff you print out when proposing a change.
- Run tests with `uv run python -m unittest`
