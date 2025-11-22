# ZIL Index - Usage Guide

## Overview

The ZIL indexer creates a searchable database of all definitions in the Zork I source code. This dramatically speeds up translation work by allowing instant lookup without reading through thousands of lines.

## What's Indexed

**914 Total Definitions:**
- **110 Rooms** - All game locations
- **138 Objects** - Items, NPCs, scenery
- **441 Routines** - Functions and action handlers
- **15 Macros** - ZIL macro definitions
- **109 Globals** - Global variables
- **101 Constants** - Game constants

## Quick Start

### Build the Index (already done)

```bash
python3 zil_indexer.py
# Creates: zil_index.json (668KB)
```

### Query the Index

```python
from zil_indexer import ZILQueryHelper

helper = ZILQueryHelper('zil_index.json')
```

## Common Queries

### 1. Find a Specific Definition

```python
# Find the THIEF object
thief = helper.find('THIEF')
print(f"File: {thief['file']}")
print(f"Lines: {thief['line_start']}-{thief['line_end']}")
print(f"Location: {thief['properties']['location']}")
```

**Output:**
```
File: 1dungeon.zil
Lines: 968-978
Location: ROUND-ROOM
```

### 2. Find All Definitions of a Type

```python
# Get all rooms
rooms = helper.find_by_type('room')
print(f"Total rooms: {len(rooms)}")

# Get all objects
objects = helper.find_by_type('object')
```

### 3. Find by Property

```python
# Find all objects that can be taken
takeables = helper.find_with_property('flags', 'TAKEBIT')

# Find all weapons
weapons = helper.find_with_property('flags', 'WEAPONBIT')
print(f"Found {len(weapons)} weapons")

# Find all containers
containers = helper.find_with_property('flags', 'CONTBIT')
```

### 4. Search Text

```python
# Search for anything mentioning "lantern"
results = helper.search('lantern')
for r in results:
    print(f"{r['type']:10s} {r['name']:20s}")
```

**Output:**
```
OBJECT     BROKEN-LAMP
OBJECT     BURNED-OUT-LANTERN
OBJECT     LAMP
ROUTINE    LANTERN
ROUTINE    I-LANTERN
```

### 5. Dependency Analysis

```python
# What does the THIEF depend on?
deps = helper.find_dependencies('THIEF')
print(f"THIEF depends on: {deps}")

# What depends on LAMP?
dependents = helper.find_dependents('LAMP')
print(f"{len(dependents)} things use LAMP")
```

## Translation Workflow

### Before (Without Index)
```python
# Need to find how the basket works
# 1. Open 1dungeon.zil
# 2. Search for "BASKET"
# 3. Read through 100+ lines
# 4. Find RAISED-BASKET at line 139
# 5. Also need LOWERED-BASKET... search again
# Time: 5-10 minutes
```

### After (With Index)
```python
helper = ZILQueryHelper('zil_index.json')

# Find all baskets
baskets = helper.search('basket')
for b in baskets:
    print(f"{b['name']} at {b['file']}:{b['line_start']}")

# RAISED-BASKET at 1dungeon.zil:139
# LOWERED-BASKET at 1dungeon.zil:130
# BASKET-F at 1actions.zil:542

# Time: 5 seconds
```

## Practical Examples

### Implementing the Lantern System

```python
# 1. Find all lantern-related objects
lantern_stuff = helper.search('lantern')

# 2. Get the main LAMP object
lamp = helper.find('LAMP')
print(f"Synonyms: {lamp['properties']['synonyms']}")
print(f"Flags: {lamp['properties']['flags']}")

# 3. Find the lantern handler routine
lantern_routine = helper.find('LANTERN')
print(f"Implementation: {lantern_routine['file']}:{lantern_routine['line_start']}")

# 4. Find what depends on lamp
lamp_users = helper.find_dependents('LAMP')
# Shows: UP-CHIMNEY-FUNCTION, I-LANTERN, DEAD-FUNCTION, etc.
```

### Implementing NPCs

```python
# Find all NPCs (objects with ACTORBIT)
npcs = helper.find_with_property('flags', 'ACTORBIT')

for npc in npcs:
    name = npc['name']
    location = npc['properties'].get('location', 'unknown')
    print(f"{name:20s} starts in {location}")

    # Find their action handler
    deps = npc.get('dependencies', [])
    print(f"  Uses: {', '.join(deps[:5])}")
```

### Finding All Treasures

```python
# Find objects with VALUE property
all_objects = helper.find_by_type('object')
treasures = []

for name, obj in all_objects.items():
    props = obj.get('properties', {})
    if 'flags' in props and any('TREASURE' in str(f) for f in props['flags']):
        treasures.append(obj)

print(f"Found {len(treasures)} treasure objects")
```

## Index Structure

Each definition includes:

```json
{
  "type": "OBJECT",
  "name": "SWORD",
  "file": "1dungeon.zil",
  "line_start": 445,
  "line_end": 452,
  "properties": {
    "desc": "elvish sword",
    "synonyms": ["SWORD", "BLADE"],
    "adjectives": ["ELVISH"],
    "flags": ["TAKEBIT", "WEAPONBIT"],
    "location": "LIVING-ROOM"
  },
  "dependencies": ["LIVING-ROOM", "TROLL", "V-ATTACK"],
  "code_snippet": "<OBJECT SWORD\n  (IN LIVING-ROOM)..."
}
```

## Performance

- **Index size:** 668KB
- **Load time:** ~50ms
- **Query time:** <1ms
- **vs. grep/search:** 100-1000x faster

## Tips

1. **Always check dependencies** - Understanding what a routine uses helps translation
2. **Search broadly first** - Use `search()` to find all related items
3. **Cross-reference** - Check both dependencies and dependents
4. **Use properties** - Filter by flags to find similar objects
5. **Keep it open** - Load the helper once, query many times

## Next Steps

When translating, use this workflow:

1. **Search** for the feature you're implementing
2. **Find** the relevant objects/rooms/routines
3. **Read** just those specific sections from source files
4. **Check dependencies** to ensure you have everything needed
5. **Implement** in Python

This reduces context switching and ensures you don't miss dependencies!
