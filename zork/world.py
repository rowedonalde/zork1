"""
Zork I - World Definition

Coordinates initialization of rooms and items.
"""

from .rooms import initialize_rooms
from .items import initialize_items


def initialize_world(game):
    """Initialize all rooms and items

    Args:
        game: ZorkGame instance to initialize
    """
    # Initialize rooms first
    initialize_rooms(game)

    # Then initialize items (which also places them in rooms)
    initialize_items(game)
