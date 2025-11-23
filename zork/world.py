"""
Zork I - World Definition

Contains all room and item definitions.
This is the largest file, containing initialize_world() which sets up:
- All 57 rooms with exits and descriptions
- All 30 items with properties and locations
"""

from .models import Item, Room, Exit, Direction


def initialize_world(game):
    """Initialize all rooms and items
    
    Args:
        game: ZorkGame instance to initialize
    """
    """Initialize all rooms and items"""

    # Create rooms
    game.rooms['west_of_house'] = Room(
        name='west_of_house',
        short_desc='West of House',
        desc='You are standing in an open field west of a white house, with a boarded front door.',
        exits=[
            Exit(Direction.NORTH, 'north_of_house'),
            Exit(Direction.SOUTH, 'south_of_house'),
            Exit(Direction.NE, 'north_of_house'),
            Exit(Direction.SE, 'south_of_house'),
            Exit(Direction.WEST, 'forest_1'),
            Exit(Direction.EAST, None, "The door is boarded and you can't remove the boards."),
        ],
        flags={'ONBIT', 'SACREDBIT'}
    )

    game.rooms['north_of_house'] = Room(
        name='north_of_house',
        short_desc='North of House',
        desc='You are facing the north side of a white house. There is no door here, '
             'and all the windows are boarded up. To the north a narrow path winds through the trees.',
        exits=[
            Exit(Direction.NORTH, 'path'),
            Exit(Direction.SOUTH, None, "The windows are all boarded."),
            Exit(Direction.EAST, 'east_of_house'),
            Exit(Direction.WEST, 'west_of_house'),
            Exit(Direction.SE, 'east_of_house'),
            Exit(Direction.SW, 'west_of_house'),
        ],
        flags={'ONBIT', 'SACREDBIT'}
    )

    game.rooms['south_of_house'] = Room(
        name='south_of_house',
        short_desc='South of House',
        desc='You are facing the south side of a white house. There is no door here, '
             'and all the windows are boarded.',
        exits=[
            Exit(Direction.NORTH, None, "The windows are all boarded."),
            Exit(Direction.EAST, 'east_of_house'),
            Exit(Direction.WEST, 'west_of_house'),
            Exit(Direction.NE, 'east_of_house'),
            Exit(Direction.NW, 'west_of_house'),
            Exit(Direction.SOUTH, 'forest_3'),
        ],
        flags={'ONBIT', 'SACREDBIT'}
    )

    game.rooms['east_of_house'] = Room(
        name='east_of_house',
        short_desc='Behind House',
        desc='You are behind the white house. A path leads into the forest to the east. '
             'In one corner of the house there is a small window which is slightly ajar.',
        exits=[
            Exit(Direction.NORTH, 'north_of_house'),
            Exit(Direction.SOUTH, 'south_of_house'),
            Exit(Direction.NW, 'north_of_house'),
            Exit(Direction.SW, 'south_of_house'),
            Exit(Direction.EAST, 'clearing'),
            Exit(Direction.WEST, 'kitchen', condition=lambda: game.state.flags['kitchen_window_open']),
            Exit(Direction.IN, 'kitchen', condition=lambda: game.state.flags['kitchen_window_open']),
        ],
        flags={'ONBIT', 'SACREDBIT'}
    )

    game.rooms['kitchen'] = Room(
        name='kitchen',
        short_desc='Kitchen',
        desc='You are in the kitchen of the white house. A table seems to have been used recently '
             'for the preparation of food. A passage leads to the west and a dark staircase can be '
             'seen leading upward. A dark chimney leads down and to the north is a small window which is open.',
        exits=[
            Exit(Direction.WEST, 'living_room'),
            Exit(Direction.EAST, 'east_of_house', condition=lambda: game.state.flags['kitchen_window_open']),
            Exit(Direction.OUT, 'east_of_house', condition=lambda: game.state.flags['kitchen_window_open']),
            Exit(Direction.UP, 'attic'),
            Exit(Direction.DOWN, None, "Only Santa Claus climbs down chimneys."),
        ],
        flags={'ONBIT', 'SACREDBIT'}
    )

    game.rooms['attic'] = Room(
        name='attic',
        short_desc='Attic',
        desc='This is the attic. The only exit is a stairway leading down.',
        exits=[
            Exit(Direction.DOWN, 'kitchen'),
        ],
        flags={'SACREDBIT'}
    )

    game.rooms['living_room'] = Room(
        name='living_room',
        short_desc='Living Room',
        desc='You are in the living room. There is a doorway to the east, a wooden door with strange '
             'gothic lettering to the west, which appears to be nailed shut, a trophy case, and a large '
             'oriental rug in the center of the room.',
        exits=[
            Exit(Direction.EAST, 'kitchen'),
            Exit(Direction.WEST, None, "The door is nailed shut."),
            Exit(Direction.DOWN, 'cellar', condition=lambda: game.state.flags['trap_door_open']),
        ],
        flags={'ONBIT', 'SACREDBIT'}
    )

    game.rooms['cellar'] = Room(
        name='cellar',
        short_desc='Cellar',
        desc='You are in a dark and damp cellar with a narrow passageway leading north, '
             'and a crawlway to the south. On the west is the bottom of a steep metal ramp '
             'which is unclimbable.',
        exits=[
            Exit(Direction.NORTH, 'troll_room'),
            Exit(Direction.SOUTH, 'east_of_chasm'),
            Exit(Direction.UP, 'living_room', condition=lambda: game.state.flags['trap_door_open']),
            Exit(Direction.WEST, None, "You try to ascend the ramp, but it is impossible, and you slide back down."),
        ]
    )

    game.rooms['troll_room'] = Room(
        name='troll_room',
        short_desc='Troll Room',
        desc='This is a small room with passages to the east and south and a forbidding hole leading west. '
             'Bloodstains and deep scratches (perhaps made by an axe) mar the walls.',
        exits=[
            Exit(Direction.SOUTH, 'cellar'),
            Exit(Direction.EAST, 'east_of_chasm', condition=lambda: game.state.flags['troll_flag']),
            Exit(Direction.WEST, 'round_room', condition=lambda: game.state.flags['troll_flag']),
        ]
    )

    game.rooms['east_of_chasm'] = Room(
        name='east_of_chasm',
        short_desc='East of Chasm',
        desc='You are on the east edge of a chasm, the bottom of which cannot be seen. '
             'A narrow passage goes north, and the path you are on continues to the east.',
        exits=[
            Exit(Direction.NORTH, 'cellar'),
            Exit(Direction.EAST, 'gallery'),
            Exit(Direction.DOWN, None, "The chasm probably leads straight to the infernal regions."),
        ]
    )

    game.rooms['gallery'] = Room(
        name='gallery',
        short_desc='Gallery',
        desc='This is an art gallery. Most of the paintings have been stolen by vandals with '
             'exceptional taste. The vandals left through either the north or west exits.',
        exits=[
            Exit(Direction.WEST, 'east_of_chasm'),
            Exit(Direction.NORTH, 'studio'),
        ],
        flags={'ONBIT'}
    )

    game.rooms['studio'] = Room(
        name='studio',
        short_desc='Studio',
        desc='This appears to have been an artist\'s studio. The walls and floors are splattered '
             'with paints of 69 different colors. Strangely enough, nothing of value is hanging here. '
             'At the south end of the room is an open door (also covered with paint).',
        exits=[
            Exit(Direction.SOUTH, 'gallery'),
        ]
    )

    game.rooms['clearing'] = Room(
        name='clearing',
        short_desc='Forest Clearing',
        desc='You are in a small clearing in a well marked forest path that extends to the east and west.',
        exits=[
            Exit(Direction.WEST, 'east_of_house'),
            Exit(Direction.EAST, 'canyon_view'),
            Exit(Direction.NORTH, 'forest_2'),
            Exit(Direction.SOUTH, 'forest_3'),
        ],
        flags={'ONBIT', 'SACREDBIT'}
    )

    game.rooms['forest_1'] = Room(
        name='forest_1',
        short_desc='Forest',
        desc='This is a forest, with trees in all directions. To the east, there appears to be sunlight.',
        exits=[
            Exit(Direction.EAST, 'path'),
            Exit(Direction.SOUTH, 'forest_3'),
            Exit(Direction.WEST, None, "You would need a machete to go further west."),
        ],
        flags={'ONBIT', 'SACREDBIT'}
    )

    game.rooms['forest_2'] = Room(
        name='forest_2',
        short_desc='Forest',
        desc='This is a dimly lit forest, with large trees all around.',
        exits=[
            Exit(Direction.NORTH, None, "The forest becomes impenetrable to the north."),
            Exit(Direction.SOUTH, 'clearing'),
            Exit(Direction.WEST, 'path'),
            Exit(Direction.EAST, 'grating_clearing'),
        ],
        flags={'ONBIT', 'SACREDBIT'}
    )

    game.rooms['forest_3'] = Room(
        name='forest_3',
        short_desc='Forest',
        desc='This is a dimly lit forest, with large trees all around.',
        exits=[
            Exit(Direction.NORTH, 'clearing'),
            Exit(Direction.WEST, 'forest_1'),
            Exit(Direction.NW, 'south_of_house'),
            Exit(Direction.EAST, None, "The rank undergrowth prevents eastward movement."),
            Exit(Direction.SOUTH, None, "Storm-tossed trees block your way."),
        ],
        flags={'ONBIT', 'SACREDBIT'}
    )

    game.rooms['path'] = Room(
        name='path',
        short_desc='Forest Path',
        desc='This is a path winding through a dimly lit forest. The path heads north-south here. '
             'One particularly large tree with some low branches stands at the edge of the path.',
        exits=[
            Exit(Direction.NORTH, 'north_of_house'),
            Exit(Direction.SOUTH, 'south_of_house'),
            Exit(Direction.EAST, 'forest_2'),
            Exit(Direction.WEST, 'forest_1'),
            Exit(Direction.UP, 'up_a_tree'),
        ],
        flags={'ONBIT', 'SACREDBIT'}
    )

    game.rooms['up_a_tree'] = Room(
        name='up_a_tree',
        short_desc='Up a Tree',
        desc='You are about 10 feet above the ground nestled among some large branches. '
             'The nearest branch above you is above your reach.',
        exits=[
            Exit(Direction.DOWN, 'path'),
        ],
        flags={'ONBIT', 'SACREDBIT'}
    )

    game.rooms['canyon_view'] = Room(
        name='canyon_view',
        short_desc='Canyon View',
        desc='You are at the top of the Great Canyon on its west wall. From here there is a '
             'marvelous view of the canyon and parts of the Frigid River upstream. Across the '
             'canyon, the walls of the White Cliffs join the mighty ramparts of the Flathead Mountains '
             'to the east. Following the canyon upstream to the north, Aragain Falls may be seen, '
             'complete with rainbow.',
        exits=[
            Exit(Direction.WEST, 'clearing'),
            Exit(Direction.NORTH, 'dam'),
            Exit(Direction.SOUTH, None, "The canyon is too wide to cross."),
            Exit(Direction.EAST, None, "The canyon is too wide to cross."),
        ],
        flags={'ONBIT', 'SACREDBIT'}
    )

    # Dam area (surface)
    game.rooms['dam'] = Room(
        name='dam',
        short_desc='Dam',
        desc='You are standing on the top of the Flood Control Dam #3, which was quite '
             'a tourist attraction in times far distant. There are paths to the north, south, '
             'and west, and a scramble down.',
        exits=[
            Exit(Direction.NORTH, 'dam_lobby'),
            Exit(Direction.SOUTH, 'canyon_view'),
            Exit(Direction.WEST, None, "The path leads to a sheer cliff."),
            Exit(Direction.DOWN, None, "The dam face is too steep to climb."),
        ],
        flags={'ONBIT', 'SACREDBIT'}
    )

    game.rooms['dam_lobby'] = Room(
        name='dam_lobby',
        short_desc='Dam Lobby',
        desc='This is the lobby for Flood Control Dam #3. There are bare concrete walls here, '
             'with an exit to the south and a door to the east leading to the dam maintenance room.',
        exits=[
            Exit(Direction.SOUTH, 'dam'),
            Exit(Direction.EAST, 'maintenance_room'),
        ],
        flags={'ONBIT'}
    )

    game.rooms['maintenance_room'] = Room(
        name='maintenance_room',
        short_desc='Maintenance Room',
        desc='This is what appears to be a maintenance room. There is a tool board here, '
             'a switch, and a drainage pipe leading down. On one wall is a group of buttons '
             'colored blue, yellow, brown, and red. There is a doorway to the west.',
        exits=[
            Exit(Direction.WEST, 'dam_lobby'),
            Exit(Direction.DOWN, None, "The drainage pipe is too small to fit through."),
        ],
        flags={'ONBIT'}
    )

    # Grating area (surface)
    game.rooms['grating_clearing'] = Room(
        name='grating_clearing',
        short_desc='Grating Clearing',
        desc='You are in a small clearing in a well marked forest path. In the center of the '
             'clearing is a grating securely fastened into the ground. All passages lead west.',
        exits=[
            Exit(Direction.WEST, 'forest_2'),
            Exit(Direction.DOWN, 'grating_room', condition=lambda: game.state.flags.get('grating_open', False)),
        ],
        flags={'ONBIT', 'SACREDBIT'}
    )

    game.rooms['grating_room'] = Room(
        name='grating_room',
        short_desc='Grating Room',
        desc='You are in a small room near the grating. There are small passages to the south and west, '
             'and a steep metal ramp descending to the east.',
        exits=[
            Exit(Direction.UP, 'grating_clearing', condition=lambda: game.state.flags.get('grating_open', False)),
            Exit(Direction.SOUTH, 'reservoir_south'),
            Exit(Direction.WEST, None, "The passage is blocked by debris."),
            Exit(Direction.EAST, 'machine_room'),
        ]
    )

    # Underground expansion - Round Room and connected areas
    game.rooms['round_room'] = Room(
        name='round_room',
        short_desc='Round Room',
        desc='You are in a large round room with passages leading in many directions. '
             'The room is dimly lit by phosphorescent lichens on the walls.',
        exits=[
            Exit(Direction.EAST, 'troll_room'),
            Exit(Direction.NORTH, 'deep_ravine'),
            Exit(Direction.NE, 'loud_room'),
            Exit(Direction.SE, 'narrow_passage'),
            Exit(Direction.SOUTH, 'maze_entrance'),
            Exit(Direction.SW, 'west_passage'),
        ],
        flags={'ONBIT'}  # Lit by lichens
    )

    game.rooms['loud_room'] = Room(
        name='loud_room',
        short_desc='Loud Room',
        desc='This is a large room with a ceiling which cannot be detected from the ground. '
             'There is a narrow passage from west to east and a stone stairway leading upward. '
             'The room is extremely noisy. In fact, it is difficult to hear yourself think.',
        exits=[
            Exit(Direction.WEST, 'round_room'),
            Exit(Direction.EAST, None, "The passage is blocked by an avalanche of boulders."),
            Exit(Direction.UP, 'deep_ravine'),
        ]
    )

    game.rooms['deep_ravine'] = Room(
        name='deep_ravine',
        short_desc='Deep Ravine',
        desc='You are on the south edge of a deep ravine. Passages exit to the south and northwest.',
        exits=[
            Exit(Direction.SOUTH, 'round_room'),
            Exit(Direction.NW, 'north_south_passage'),
            Exit(Direction.DOWN, 'loud_room'),
        ]
    )

    game.rooms['north_south_passage'] = Room(
        name='north_south_passage',
        short_desc='North-South Passage',
        desc='This is a high north-south passage, which forks to the northeast.',
        exits=[
            Exit(Direction.NORTH, None, "The passage quickly narrows to an impassable crack."),
            Exit(Direction.SOUTH, None, "The passage ends in a steep cliff."),
            Exit(Direction.NE, None, "The passage is blocked by collapsed rubble."),
            Exit(Direction.SE, 'deep_ravine'),
        ]
    )

    game.rooms['narrow_passage'] = Room(
        name='narrow_passage',
        short_desc='Narrow Passage',
        desc='This is a long and narrow corridor where a long north-south passageway briefly '
             'narrows even further.',
        exits=[
            Exit(Direction.NORTH, 'round_room'),
            Exit(Direction.SOUTH, 'mirror_room'),
        ]
    )

    game.rooms['mirror_room'] = Room(
        name='mirror_room',
        short_desc='Mirror Room',
        desc='You are in a large square room with tall ceilings. On the south wall is an enormous '
             'mirror which fills the entire wall. There are exits on the other three sides of the room.',
        exits=[
            Exit(Direction.NORTH, 'narrow_passage'),
            Exit(Direction.WEST, 'cold_passage'),
            Exit(Direction.EAST, None, "The passage is too dark to navigate safely."),
            Exit(Direction.SOUTH, None, "You cannot pass through the mirror."),
        ]
    )

    game.rooms['cold_passage'] = Room(
        name='cold_passage',
        short_desc='Cold Passage',
        desc='This is a cold and damp corridor carved out of the rock.',
        exits=[
            Exit(Direction.EAST, 'mirror_room'),
            Exit(Direction.WEST, 'slide_room'),
            Exit(Direction.SOUTH, None, "The passage ends in a steep cliff."),
        ]
    )

    game.rooms['slide_room'] = Room(
        name='slide_room',
        short_desc='Slide Room',
        desc='This is a small chamber, which appears to have been part of a coal mine. On the '
             'south wall of the room is a passage, blocked by a heavy wooden door. A stairway '
             'leads down, but it is extremely steep and cannot be safely descended.',
        exits=[
            Exit(Direction.EAST, 'cold_passage'),
            Exit(Direction.SOUTH, None, "The wooden door is tightly shut."),
            Exit(Direction.DOWN, None, "The stairs are too steep and dangerous to descend."),
        ]
    )

    game.rooms['maze_entrance'] = Room(
        name='maze_entrance',
        short_desc='Maze Entrance',
        desc='You are in a maze of twisty little passages, all alike.',
        exits=[
            Exit(Direction.NORTH, 'round_room'),
            Exit(Direction.SOUTH, 'maze_1'),
            Exit(Direction.EAST, 'maze_2'),
            Exit(Direction.WEST, None, "You are in a maze of twisty little passages, all alike."),
        ]
    )

    game.rooms['maze_1'] = Room(
        name='maze_1',
        short_desc='Maze',
        desc='You are in a maze of twisty little passages, all alike.',
        exits=[
            Exit(Direction.NORTH, 'maze_entrance'),
            Exit(Direction.SOUTH, 'maze_3'),
            Exit(Direction.EAST, None, "You are in a maze of twisty little passages, all alike."),
            Exit(Direction.WEST, 'maze_2'),
        ]
    )

    game.rooms['maze_2'] = Room(
        name='maze_2',
        short_desc='Maze',
        desc='You are in a maze of twisty little passages, all alike.',
        exits=[
            Exit(Direction.NORTH, None, "You are in a maze of twisty little passages, all alike."),
            Exit(Direction.SOUTH, None, "You are in a maze of twisty little passages, all alike."),
            Exit(Direction.EAST, 'maze_1'),
            Exit(Direction.WEST, 'maze_entrance'),
        ]
    )

    game.rooms['west_passage'] = Room(
        name='west_passage',
        short_desc='West of Round Room',
        desc='This is a narrow passage with a low ceiling. It connects to the Round Room to the northeast.',
        exits=[
            Exit(Direction.NE, 'round_room'),
            Exit(Direction.WEST, None, "The passage is blocked by fallen rocks."),
        ]
    )

    # Reservoir area (underground)
    game.rooms['reservoir_south'] = Room(
        name='reservoir_south',
        short_desc='Reservoir South',
        desc='You are in a large cavernous room, the south end of a large reservoir. Across the '
             'water to the north you can see a dimly lit shore. There is a path going south and '
             'a passage leading north along the shore.',
        exits=[
            Exit(Direction.NORTH, 'grating_room'),
            Exit(Direction.SOUTH, 'chasm'),
            Exit(Direction.EAST, None, "You would drown trying to cross the deep water."),
        ]
    )

    game.rooms['reservoir_north'] = Room(
        name='reservoir_north',
        short_desc='Reservoir',
        desc='You are on the shore of a large underground reservoir. A path leads north and '
             'passages go south and east.',
        exits=[
            Exit(Direction.NORTH, 'stream'),
            Exit(Direction.SOUTH, None, "The water is too deep to wade across."),
            Exit(Direction.EAST, 'deep_canyon'),
        ]
    )

    game.rooms['stream'] = Room(
        name='stream',
        short_desc='Stream',
        desc='You are standing on a path beside a gently flowing stream. The path continues to '
             'the north and south. To the east is a large boulder.',
        exits=[
            Exit(Direction.NORTH, 'stream_view'),
            Exit(Direction.SOUTH, 'reservoir_north'),
            Exit(Direction.EAST, None, "The boulder is too large to pass."),
        ]
    )

    game.rooms['stream_view'] = Room(
        name='stream_view',
        short_desc='Stream View',
        desc='You are standing high on a ledge overlooking a stream. A path leads south along '
             'the ledge. To the east is an enormous cavern.',
        exits=[
            Exit(Direction.SOUTH, 'stream'),
            Exit(Direction.EAST, 'treasure_room'),
            Exit(Direction.DOWN, None, "The drop is too steep."),
        ]
    )

    # Temple and treasure areas
    game.rooms['temple'] = Room(
        name='temple',
        short_desc='Temple',
        desc='This is the north end of a large temple. In front of you is what appears to be '
             'an altar. In one corner is a small hole in the floor which leads into darkness. '
             'A path exits to the south and west.',
        exits=[
            Exit(Direction.SOUTH, 'egyptian_room'),
            Exit(Direction.WEST, 'torch_room'),
            Exit(Direction.DOWN, None, "The hole is too small to fit through."),
        ],
        flags={'ONBIT'}  # Temple is lit
    )

    game.rooms['egyptian_room'] = Room(
        name='egyptian_room',
        short_desc='Egyptian Room',
        desc='This is a room, which appears to have been part of an Egyptian tomb. The walls '
             'are covered with hieroglyphics. A passage leads north, and a steep staircase leads '
             'upward and to the south.',
        exits=[
            Exit(Direction.NORTH, 'temple'),
            Exit(Direction.UP, 'torch_room'),
            Exit(Direction.SOUTH, None, "The staircase has collapsed."),
        ]
    )

    game.rooms['torch_room'] = Room(
        name='torch_room',
        short_desc='Torch Room',
        desc='This is a large room with torches mounted on the walls. The flickering torches '
             'illuminate the cave with an eerie light. There are exits to the east and west, '
             'and passages going north and south.',
        exits=[
            Exit(Direction.EAST, 'temple'),
            Exit(Direction.WEST, 'north_south_corridor'),
            Exit(Direction.NORTH, None, "The passage is blocked by fallen rocks."),
            Exit(Direction.SOUTH, None, "The floor has collapsed here."),
        ],
        flags={'ONBIT'}  # Lit by torches
    )

    game.rooms['north_south_corridor'] = Room(
        name='north_south_corridor',
        short_desc='North-South Corridor',
        desc='This is a long north-south corridor. The walls are carved from solid rock.',
        exits=[
            Exit(Direction.NORTH, 'chasm'),
            Exit(Direction.SOUTH, 'deep_canyon'),
            Exit(Direction.EAST, 'torch_room'),
        ]
    )

    game.rooms['chasm'] = Room(
        name='chasm',
        short_desc='Chasm',
        desc='A chasm runs across the room from east to west. A narrow passage exits to the south.',
        exits=[
            Exit(Direction.NORTH, 'reservoir_south'),
            Exit(Direction.SOUTH, 'north_south_corridor'),
            Exit(Direction.EAST, None, "The chasm is too wide to cross."),
            Exit(Direction.WEST, None, "The chasm is too wide to cross."),
            Exit(Direction.DOWN, None, "It is too deep to see the bottom."),
        ]
    )

    game.rooms['deep_canyon'] = Room(
        name='deep_canyon',
        short_desc='Deep Canyon',
        desc='You are on a narrow ledge in a deep canyon. Passages exit to the north and west.',
        exits=[
            Exit(Direction.NORTH, 'north_south_corridor'),
            Exit(Direction.WEST, 'reservoir_north'),
            Exit(Direction.DOWN, None, "The canyon is too deep to climb down."),
        ]
    )

    game.rooms['treasure_room'] = Room(
        name='treasure_room',
        short_desc='Treasure Room',
        desc='This is a fabulous treasure room! Piles of gold and jewels are scattered about. '
             'There is a passage to the west.',
        exits=[
            Exit(Direction.WEST, 'stream_view'),
        ],
        flags={'ONBIT'}  # Naturally lit
    )

    # Machine room and coal mine
    game.rooms['machine_room'] = Room(
        name='machine_room',
        short_desc='Machine Room',
        desc='This is a large room full of assorted heavy machinery, whirring noisily. '
             'There is a switch on the wall and a ramp leading west and down. Another exit is to the east.',
        exits=[
            Exit(Direction.WEST, 'grating_room'),
            Exit(Direction.DOWN, 'coal_mine_1'),
            Exit(Direction.EAST, None, "The machinery blocks the way."),
        ]
    )

    game.rooms['coal_mine_1'] = Room(
        name='coal_mine_1',
        short_desc='Coal Mine',
        desc='This is a coal mine. The walls are solid coal. There are passages to the north, '
             'south, and east.',
        exits=[
            Exit(Direction.NORTH, None, "The passage is too dark to navigate."),
            Exit(Direction.SOUTH, 'coal_mine_2'),
            Exit(Direction.EAST, 'coal_mine_3'),
            Exit(Direction.UP, 'machine_room'),
        ]
    )

    game.rooms['coal_mine_2'] = Room(
        name='coal_mine_2',
        short_desc='Coal Mine',
        desc='This is a coal mine. Passages exit to the north and east.',
        exits=[
            Exit(Direction.NORTH, 'coal_mine_1'),
            Exit(Direction.EAST, 'coal_mine_4'),
            Exit(Direction.SOUTH, None, "The mine shaft has collapsed here."),
        ]
    )

    game.rooms['coal_mine_3'] = Room(
        name='coal_mine_3',
        short_desc='Coal Mine',
        desc='This is a coal mine. Passages exit to the west and south.',
        exits=[
            Exit(Direction.WEST, 'coal_mine_1'),
            Exit(Direction.SOUTH, 'coal_mine_4'),
            Exit(Direction.EAST, None, "The passage is blocked by rubble."),
        ]
    )

    game.rooms['coal_mine_4'] = Room(
        name='coal_mine_4',
        short_desc='Ladder Top',
        desc='This is a small room. In the center of the room is a wooden ladder leading down '
             'through a hole in the floor. Passages exit to the north and west.',
        exits=[
            Exit(Direction.NORTH, 'coal_mine_3'),
            Exit(Direction.WEST, 'coal_mine_2'),
            Exit(Direction.DOWN, 'ladder_bottom'),
        ]
    )

    game.rooms['ladder_bottom'] = Room(
        name='ladder_bottom',
        short_desc='Ladder Bottom',
        desc='This is a very small room. A wooden ladder leads upward. To the south is a passageway.',
        exits=[
            Exit(Direction.UP, 'coal_mine_4'),
            Exit(Direction.SOUTH, 'dead_end'),
        ]
    )

    game.rooms['dead_end'] = Room(
        name='dead_end',
        short_desc='Dead End',
        desc='This is a dead end. There is a pile of debris here and a passageway to the north.',
        exits=[
            Exit(Direction.NORTH, 'ladder_bottom'),
        ]
    )

    # Maze expansion
    game.rooms['maze_3'] = Room(
        name='maze_3',
        short_desc='Maze',
        desc='You are in a maze of twisty little passages, all alike.',
        exits=[
            Exit(Direction.NORTH, 'maze_1'),
            Exit(Direction.SOUTH, 'maze_4'),
            Exit(Direction.EAST, None, "You are in a maze of twisty little passages, all alike."),
            Exit(Direction.WEST, None, "You are in a maze of twisty little passages, all alike."),
        ]
    )

    game.rooms['maze_4'] = Room(
        name='maze_4',
        short_desc='Maze',
        desc='You are in a maze of twisty little passages, all alike.',
        exits=[
            Exit(Direction.NORTH, 'maze_3'),
            Exit(Direction.SOUTH, None, "You are in a maze of twisty little passages, all alike."),
            Exit(Direction.EAST, 'maze_5'),
            Exit(Direction.WEST, 'maze_2'),
        ]
    )

    game.rooms['maze_5'] = Room(
        name='maze_5',
        short_desc='Maze',
        desc='You are in a maze of twisty little passages, all alike. However, one passage '
             'to the east seems slightly wider.',
        exits=[
            Exit(Direction.NORTH, None, "You are in a maze of twisty little passages, all alike."),
            Exit(Direction.SOUTH, None, "You are in a maze of twisty little passages, all alike."),
            Exit(Direction.EAST, 'maze_exit'),
            Exit(Direction.WEST, 'maze_4'),
        ]
    )

    game.rooms['maze_exit'] = Room(
        name='maze_exit',
        short_desc='End of Maze',
        desc='You have reached the end of the maze! Congratulations! A passage leads west back '
             'into the maze and north to a small chamber.',
        exits=[
            Exit(Direction.WEST, 'maze_5'),
            Exit(Direction.NORTH, None, "The passage is blocked."),
        ]
    )

    # Create items
    game.items['mailbox'] = Item(
        name='mailbox',
        desc='small mailbox',
        synonyms=['box', 'mail'],
        adjectives=['small'],
        location='west_of_house',
        flags={'CONTBIT'}
    )

    game.items['leaflet'] = Item(
        name='leaflet',
        desc='leaflet',
        synonyms=['booklet', 'pamphlet'],
        location='mailbox',
        takeable=True,
        flags={'TAKEBIT'}
    )

    game.items['sword'] = Item(
        name='sword',
        desc='elvish sword',
        synonyms=['blade', 'weapon'],
        adjectives=['elvish', 'elven'],
        location='living_room',
        takeable=True,
        flags={'TAKEBIT', 'WEAPONBIT'},
        value=10,
        size=25
    )

    game.items['lantern'] = Item(
        name='lantern',
        desc='brass lantern',
        synonyms=['lamp', 'light'],
        adjectives=['brass'],
        location='living_room',
        takeable=True,
        flags={'TAKEBIT', 'LIGHTBIT'},  # Can provide light
        size=15
    )

    game.items['rug'] = Item(
        name='rug',
        desc='large rug',
        synonyms=['carpet'],
        adjectives=['large', 'oriental'],
        location='living_room',
        flags={'TRYTAKEBIT'}
    )

    game.items['trap_door'] = Item(
        name='trap_door',
        desc='trap door',
        synonyms=['door', 'trapdoor', 'trap door'],
        adjectives=['trap'],
        location='living_room',
        flags={'DOORBIT', 'NDESCBIT'}
    )

    game.items['trophy_case'] = Item(
        name='trophy_case',
        desc='trophy case',
        synonyms=['case'],
        adjectives=['trophy'],
        location='living_room',
        flags={'CONTBIT', 'NDESCBIT', 'TRYTAKEBIT'}
    )

    # Treasures
    game.items['painting'] = Item(
        name='painting',
        desc='beautiful painting',
        synonyms=['picture'],
        adjectives=['beautiful'],
        location='gallery',
        takeable=True,
        flags={'TAKEBIT'},
        value=4,
        size=20
    )

    game.items['jewels'] = Item(
        name='jewels',
        desc='jewel-encrusted egg',
        synonyms=['egg', 'jewel'],
        adjectives=['jeweled', 'jewel-encrusted'],
        location='living_room',  # Put in living room for easy testing
        takeable=True,
        flags={'TAKEBIT'},
        value=5,
        size=10
    )

    game.items['platinum_bar'] = Item(
        name='platinum_bar',
        desc='platinum bar',
        synonyms=['bar', 'platinum'],
        adjectives=['platinum'],
        location='loud_room',
        takeable=True,
        flags={'TAKEBIT'},
        value=10,
        size=10
    )

    game.items['chalice'] = Item(
        name='chalice',
        desc='jeweled chalice',
        synonyms=['cup', 'grail'],
        adjectives=['jeweled', 'gold', 'golden'],
        location='deep_ravine',
        takeable=True,
        flags={'TAKEBIT'},
        value=10,
        size=10
    )

    game.items['trident'] = Item(
        name='trident',
        desc='crystal trident',
        synonyms=['fork', 'spear'],
        adjectives=['crystal', 'crystalline'],
        location='mirror_room',
        takeable=True,
        flags={'TAKEBIT'},
        value=4,
        size=15
    )

    game.items['torch'] = Item(
        name='torch',
        desc='ivory torch',
        synonyms=['flame'],
        adjectives=['ivory', 'white'],
        location='cold_passage',
        takeable=True,
        flags={'TAKEBIT'},
        value=6,
        size=12
    )

    game.items['coins'] = Item(
        name='coins',
        desc='bag of coins',
        synonyms=['bag', 'coin', 'gold'],
        adjectives=['gold', 'golden'],
        location='maze_1',
        takeable=True,
        flags={'TAKEBIT'},
        value=5,
        size=8
    )

    # New treasures for expanded areas
    game.items['diamond'] = Item(
        name='diamond',
        desc='huge diamond',
        synonyms=['gem', 'jewel'],
        adjectives=['huge', 'sparkling'],
        location='treasure_room',
        takeable=True,
        flags={'TAKEBIT'},
        value=10,
        size=5
    )

    game.items['emerald'] = Item(
        name='emerald',
        desc='large emerald',
        synonyms=['gem', 'jewel'],
        adjectives=['large', 'green'],
        location='treasure_room',
        takeable=True,
        flags={'TAKEBIT'},
        value=5,
        size=5
    )

    game.items['ruby'] = Item(
        name='ruby',
        desc='glowing ruby',
        synonyms=['gem', 'jewel'],
        adjectives=['glowing', 'red'],
        location='maze_exit',
        takeable=True,
        flags={'TAKEBIT'},
        value=8,
        size=5
    )

    game.items['sapphire'] = Item(
        name='sapphire',
        desc='beautiful sapphire',
        synonyms=['gem', 'jewel'],
        adjectives=['beautiful', 'blue'],
        location='egyptian_room',
        takeable=True,
        flags={'TAKEBIT'},
        value=8,
        size=5
    )

    game.items['crown'] = Item(
        name='crown',
        desc='ancient crown',
        synonyms=['coronet', 'diadem'],
        adjectives=['ancient', 'jeweled'],
        location='temple',
        takeable=True,
        flags={'TAKEBIT'},
        value=12,
        size=15
    )

    game.items['sceptre'] = Item(
        name='sceptre',
        desc='golden sceptre',
        synonyms=['staff', 'rod', 'scepter'],
        adjectives=['golden', 'ornate'],
        location='reservoir_north',
        takeable=True,
        flags={'TAKEBIT'},
        value=6,
        size=18
    )

    game.items['pearl'] = Item(
        name='pearl',
        desc='glistening pearl',
        synonyms=['gem'],
        adjectives=['glistening', 'white'],
        location='stream',
        takeable=True,
        flags={'TAKEBIT'},
        value=4,
        size=3
    )

    game.items['coal'] = Item(
        name='coal',
        desc='lump of coal',
        synonyms=['lump'],
        adjectives=['black'],
        location='coal_mine_4',
        takeable=True,
        flags={'TAKEBIT'},
        value=1,
        size=5
    )

    game.items['bracelet'] = Item(
        name='bracelet',
        desc='silver bracelet',
        synonyms=['armband', 'bangle'],
        adjectives=['silver', 'ornate'],
        location='dead_end',
        takeable=True,
        flags={'TAKEBIT'},
        value=7,
        size=6
    )

    # NPCs
    game.items['troll'] = Item(
        name='troll',
        desc='nasty troll',
        synonyms=['monster'],
        adjectives=['nasty'],
        location='troll_room',
        flags={'ACTORBIT', 'TRYTAKEBIT'}
    )

    # Scenery/climbable objects
    game.items['tree'] = Item(
        name='tree',
        desc='large tree',
        synonyms=['oak', 'branch', 'branches'],
        adjectives=['large', 'tall'],
        location='path',
        flags={'TRYTAKEBIT'}
    )

    # Tools and utility items
    game.items['rope'] = Item(
        name='rope',
        desc='hemp rope',
        synonyms=['cord', 'line'],
        adjectives=['hemp', 'thick'],
        location='attic',
        takeable=True,
        flags={'TAKEBIT'},
        size=15
    )

    game.items['knife'] = Item(
        name='knife',
        desc='nasty knife',
        synonyms=['blade', 'dagger'],
        adjectives=['nasty', 'sharp'],
        location='round_room',
        takeable=True,
        flags={'TAKEBIT', 'WEAPONBIT'},
        value=5,
        size=10
    )

    game.items['bottle'] = Item(
        name='bottle',
        desc='glass bottle',
        synonyms=['flask', 'container'],
        adjectives=['glass', 'clear'],
        location='kitchen',
        takeable=True,
        flags={'TAKEBIT', 'CONTBIT'},
        size=8
    )

    game.items['shovel'] = Item(
        name='shovel',
        desc='sturdy shovel',
        synonyms=['spade', 'tool'],
        adjectives=['sturdy', 'metal'],
        location='slide_room',
        takeable=True,
        flags={'TAKEBIT'},
        size=25
    )

    game.items['axe'] = Item(
        name='axe',
        desc='bloody axe',
        synonyms=['hatchet', 'weapon'],
        adjectives=['bloody', 'rusty'],
        location=None,  # Dropped by troll when killed
        takeable=True,
        flags={'TAKEBIT', 'WEAPONBIT', 'NDESCBIT'},
        value=3,
        size=20
    )

    # Add items to rooms
    game.rooms['west_of_house'].items.append('mailbox')
    game.rooms['living_room'].items.extend(['sword', 'lantern', 'rug', 'trap_door', 'trophy_case', 'jewels'])
    game.rooms['gallery'].items.append('painting')
    game.rooms['troll_room'].items.append('troll')
    game.rooms['path'].items.append('tree')
    game.rooms['attic'].items.append('rope')
    game.rooms['kitchen'].items.append('bottle')

    # Underground treasure locations
    game.rooms['loud_room'].items.append('platinum_bar')
    game.rooms['deep_ravine'].items.append('chalice')
    game.rooms['mirror_room'].items.append('trident')
    game.rooms['cold_passage'].items.append('torch')
    game.rooms['maze_1'].items.append('coins')
    game.rooms['round_room'].items.append('knife')
    game.rooms['slide_room'].items.append('shovel')

    # New treasure locations in expanded areas
    game.rooms['treasure_room'].items.extend(['diamond', 'emerald'])
    game.rooms['maze_exit'].items.append('ruby')
    game.rooms['egyptian_room'].items.append('sapphire')
    game.rooms['temple'].items.append('crown')
    game.rooms['reservoir_north'].items.append('sceptre')
    game.rooms['stream'].items.append('pearl')
    game.rooms['coal_mine_4'].items.append('coal')
    game.rooms['dead_end'].items.append('bracelet')

