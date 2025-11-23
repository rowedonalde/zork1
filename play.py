#!/usr/bin/env python3
"""
Zork I: The Great Underground Empire
Play the game!

Run with: python3 play.py
"""

from zork import ZorkGame


def main():
    """Entry point"""
    game = ZorkGame()
    game.run()


if __name__ == '__main__':
    main()
