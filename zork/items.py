"""
Zork I - Item Definitions

Contains all item definitions and placement.
"""

from .models import Item


def initialize_items(game):
    """Initialize all items in the game world

    Args:
        game: ZorkGame instance to initialize
    """
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

    game.items['skeleton_key'] = Item(
        name='skeleton_key',
        desc='skeleton key',
        synonyms=['key', 'keys'],
        adjectives=['skeleton', 'old'],
        location='maze_5',
        takeable=True,
        flags={'TAKEBIT', 'TOOLBIT'},
        size=10
    )

    # Door objects
    game.items['grating'] = Item(
        name='grating',
        desc='grating',
        synonyms=['grate', 'bars'],
        adjectives=['metal', 'iron'],
        location='grating_clearing',
        flags={'DOORBIT', 'NDESCBIT'}
    )

    # Add items to rooms
    game.rooms['west_of_house'].items.append('mailbox')
    game.rooms['living_room'].items.extend(['sword', 'lantern', 'rug', 'trap_door', 'trophy_case', 'jewels'])
    game.rooms['gallery'].items.append('painting')
    game.rooms['troll_room'].items.append('troll')
    game.rooms['path'].items.append('tree')
    game.rooms['attic'].items.append('rope')
    game.rooms['kitchen'].items.append('bottle')
    game.rooms['grating_clearing'].items.append('grating')
    game.rooms['grating_room'].items.append('grating')  # Grating visible from both sides

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
    game.rooms['maze_5'].items.append('skeleton_key')
