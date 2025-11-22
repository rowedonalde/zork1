#!/usr/bin/env python3
"""
ZIL Source Code Indexer
Parses ZIL files and creates a searchable index of all definitions
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field, asdict


@dataclass
class ZILDefinition:
    """Represents a ZIL definition (ROOM, OBJECT, ROUTINE, etc.)"""
    type: str  # 'ROOM', 'OBJECT', 'ROUTINE', 'DEFMAC', etc.
    name: str
    file: str
    line_start: int
    line_end: int
    properties: Dict = field(default_factory=dict)
    dependencies: Set[str] = field(default_factory=set)
    code_snippet: str = ""

    def to_dict(self):
        """Convert to JSON-serializable dict"""
        d = asdict(self)
        d['dependencies'] = list(d['dependencies'])  # Convert set to list
        return d


class ZILIndexer:
    """Indexes ZIL source files for fast lookup"""

    def __init__(self, zil_dir: Path):
        self.zil_dir = Path(zil_dir)
        self.index: Dict[str, Dict[str, ZILDefinition]] = {
            'rooms': {},
            'objects': {},
            'routines': {},
            'macros': {},
            'globals': {},
            'constants': {},
        }
        self.name_to_type: Dict[str, str] = {}  # Quick lookup: name -> type

    def parse_zil_files(self, pattern: str = "*.zil") -> None:
        """Parse all ZIL files matching pattern"""
        zil_files = sorted(self.zil_dir.glob(pattern))

        for zil_file in zil_files:
            print(f"Parsing {zil_file.name}...")
            self.parse_file(zil_file)

    def parse_file(self, filepath: Path) -> None:
        """Parse a single ZIL file"""
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip comments and empty lines
            if not line or line.startswith('"') or line.startswith(';'):
                i += 1
                continue

            # Check for definitions
            if line.startswith('<ROOM '):
                i = self.parse_definition('ROOM', 'rooms', lines, i, filepath.name)
            elif line.startswith('<OBJECT '):
                i = self.parse_definition('OBJECT', 'objects', lines, i, filepath.name)
            elif line.startswith('<ROUTINE '):
                i = self.parse_definition('ROUTINE', 'routines', lines, i, filepath.name)
            elif line.startswith('<DEFMAC '):
                i = self.parse_definition('DEFMAC', 'macros', lines, i, filepath.name)
            elif line.startswith('<GLOBAL '):
                i = self.parse_global(lines, i, filepath.name)
            elif line.startswith('<CONSTANT '):
                i = self.parse_constant(lines, i, filepath.name)
            else:
                i += 1

    def parse_definition(self, def_type: str, index_key: str, lines: List[str],
                        start_idx: int, filename: str) -> int:
        """Parse a ROOM, OBJECT, ROUTINE, or DEFMAC definition

        Examples of what we're parsing:

        <ROOM WEST-OF-HOUSE
              (IN ROOMS)
              (DESC "West of House")
              (NORTH TO NORTH-OF-HOUSE)
              (FLAGS RLANDBIT ONBIT)>

        <OBJECT SWORD
                (IN LIVING-ROOM)
                (SYNONYM SWORD BLADE)
                (ADJECTIVE ELVISH)
                (FLAGS TAKEBIT WEAPONBIT)>

        <ROUTINE WEST-HOUSE (RARG)
                 <COND (<EQUAL? .RARG ,M-LOOK>
                        <TELL "You are west of house." CR>)>>

        <DEFMAC TELL ("ARGS" A)
                <FORM PROG () !<MAPF ...>>>
        """
        line_start = start_idx + 1  # 1-indexed line numbers

        # Extract name from first line
        first_line = lines[start_idx].strip()
        name_match = re.match(r'<(?:ROOM|OBJECT|ROUTINE|DEFMAC)\s+(\S+)', first_line)
        if not name_match:
            return start_idx + 1

        name = name_match.group(1)

        # Find matching closing angle bracket
        depth = 0
        i = start_idx
        code_lines = []

        while i < len(lines):
            line = lines[i]
            code_lines.append(line.rstrip())

            # Count angle brackets
            for char in line:
                if char == '<':
                    depth += 1
                elif char == '>':
                    depth -= 1
                    if depth == 0:
                        # Found the end
                        line_end = i + 1
                        code_snippet = '\n'.join(code_lines[:50])  # First 50 lines

                        # Extract properties
                        properties = self.extract_properties(code_lines, def_type)

                        # Extract dependencies (references to other objects/rooms)
                        dependencies = self.extract_dependencies(code_lines)

                        # Create definition
                        definition = ZILDefinition(
                            type=def_type,
                            name=name,
                            file=filename,
                            line_start=line_start,
                            line_end=line_end,
                            properties=properties,
                            dependencies=dependencies,
                            code_snippet=code_snippet
                        )

                        self.index[index_key][name] = definition
                        self.name_to_type[name] = index_key

                        return i + 1
            i += 1

        return i

    def parse_global(self, lines: List[str], start_idx: int, filename: str) -> int:
        """Parse a GLOBAL definition

        Example of what we're parsing:
            <GLOBAL SCORE 0>
            <GLOBAL PLAYER <>>
            <GLOBAL VERBOSE <>>
            <GLOBAL LOAD-MAX 100>
        """
        line = lines[start_idx].strip()
        match = re.match(r'<GLOBAL\s+(\S+)\s+(.*)>', line)
        if match:
            name = match.group(1)
            value = match.group(2)

            definition = ZILDefinition(
                type='GLOBAL',
                name=name,
                file=filename,
                line_start=start_idx + 1,
                line_end=start_idx + 1,
                properties={'initial_value': value},
                code_snippet=line
            )

            self.index['globals'][name] = definition
            self.name_to_type[name] = 'globals'

        return start_idx + 1

    def parse_constant(self, lines: List[str], start_idx: int, filename: str) -> int:
        """Parse a CONSTANT definition

        Example of what we're parsing:
            <CONSTANT SERIAL 0>
            <CONSTANT M-FATAL 2>
            <CONSTANT M-BEG 1>
        """
        line = lines[start_idx].strip()
        match = re.match(r'<CONSTANT\s+(\S+)\s+(.*)>', line)
        if match:
            name = match.group(1)
            value = match.group(2)

            definition = ZILDefinition(
                type='CONSTANT',
                name=name,
                file=filename,
                line_start=start_idx + 1,
                line_end=start_idx + 1,
                properties={'value': value},
                code_snippet=line
            )

            self.index['constants'][name] = definition
            self.name_to_type[name] = 'constants'

        return start_idx + 1

    def extract_properties(self, code_lines: List[str], def_type: str) -> Dict:
        """Extract key properties from definition

        Examples of what we're extracting:

        From ROOM:
            (DESC "West of House")           -> properties['desc'] = "West of House"
            (NORTH TO NORTH-OF-HOUSE)        -> properties['exits'] = ['NORTH-OF-HOUSE']
            (FLAGS RLANDBIT ONBIT)           -> properties['flags'] = ['RLANDBIT', 'ONBIT']

        From OBJECT:
            (DESC "brass lantern")           -> properties['desc'] = "brass lantern"
            (SYNONYM LAMP LANTERN)           -> properties['synonyms'] = ['LAMP', 'LANTERN']
            (ADJECTIVE BRASS)                -> properties['adjectives'] = ['BRASS']
            (FLAGS TAKEBIT)                  -> properties['flags'] = ['TAKEBIT']
            (IN LIVING-ROOM)                 -> properties['location'] = 'LIVING-ROOM'

        From ROUTINE:
            <ROUTINE WEST-HOUSE (RARG)       -> properties['parameters'] = ['RARG']
        """
        properties = {}
        full_text = ' '.join(code_lines)

        if def_type == 'ROOM':
            # Extract DESC
            desc_match = re.search(r'\(DESC\s+"([^"]+)"', full_text)
            if desc_match:
                properties['desc'] = desc_match.group(1)

            # Extract exits
            exit_pattern = r'\((?:NORTH|SOUTH|EAST|WEST|NE|NW|SE|SW|UP|DOWN|IN|OUT)\s+(?:TO\s+)?([^)]+)\)'
            properties['exits'] = re.findall(exit_pattern, full_text)

            # Extract flags
            flags_match = re.search(r'\(FLAGS\s+([^)]+)\)', full_text)
            if flags_match:
                properties['flags'] = flags_match.group(1).split()

        elif def_type == 'OBJECT':
            # Extract DESC
            desc_match = re.search(r'\(DESC\s+"([^"]+)"', full_text)
            if desc_match:
                properties['desc'] = desc_match.group(1)

            # Extract synonyms
            syn_match = re.search(r'\(SYNONYM\s+([^)]+)\)', full_text)
            if syn_match:
                properties['synonyms'] = syn_match.group(1).split()

            # Extract adjectives
            adj_match = re.search(r'\(ADJECTIVE\s+([^)]+)\)', full_text)
            if adj_match:
                properties['adjectives'] = adj_match.group(1).split()

            # Extract flags
            flags_match = re.search(r'\(FLAGS\s+([^)]+)\)', full_text)
            if flags_match:
                properties['flags'] = flags_match.group(1).split()

            # Extract location
            in_match = re.search(r'\(IN\s+([^)]+)\)', full_text)
            if in_match:
                properties['location'] = in_match.group(1)

        elif def_type == 'ROUTINE':
            # Extract parameters
            params_match = re.search(r'<ROUTINE\s+\S+\s+\(([^)]*)\)', code_lines[0])
            if params_match:
                properties['parameters'] = params_match.group(1).split()

        return properties

    def extract_dependencies(self, code_lines: List[str]) -> Set[str]:
        """Extract references to other definitions

        Examples of what we're detecting:

        Global variable references (with comma prefix):
            ,PRSO                    -> depends on PRSO
            ,HERE                    -> depends on HERE
            ,WINNER                  -> depends on WINNER

        Function/object references:
            <EQUAL? ,PRSO ,SWORD>    -> depends on PRSO, SWORD
            <FSET? ,LAMP ,ONBIT>     -> depends on LAMP, ONBIT
            <MOVE ,THIEF ,HERE>      -> depends on THIEF, HERE
            (NORTH TO TROLL-ROOM)    -> depends on TROLL-ROOM

        We filter out common ZIL keywords like ROUTINE, COND, TELL, etc.
        """
        dependencies = set()
        full_text = ' '.join(code_lines)

        # Look for common reference patterns
        # ,NAME (global variable)
        for match in re.finditer(r',([A-Z][A-Z0-9-]*)', full_text):
            dependencies.add(match.group(1))

        # <NAME> or (NAME ...) - function/macro calls
        for match in re.finditer(r'[<(]([A-Z][A-Z0-9-]*)', full_text):
            name = match.group(1)
            # Filter out common keywords
            if name not in {'ROUTINE', 'OBJECT', 'ROOM', 'COND', 'SET', 'TELL',
                           'EQUAL?', 'NOT', 'AND', 'OR', 'FSET?', 'IN', 'FLAGS',
                           'DESC', 'SYNONYM', 'ADJECTIVE', 'ACTION', 'LDESC',
                           'NORTH', 'SOUTH', 'EAST', 'WEST', 'UP', 'DOWN',
                           'REPEAT', 'PROG', 'RETURN', 'RTRUE', 'RFALSE'}:
                dependencies.add(name)

        return dependencies

    def save_index(self, output_file: str = "zil_index.json") -> None:
        """Save index to JSON file"""
        output_path = self.zil_dir / output_file

        # Convert to JSON-serializable format
        json_index = {}
        for category, defs in self.index.items():
            json_index[category] = {
                name: def_obj.to_dict()
                for name, def_obj in defs.items()
            }

        with open(output_path, 'w') as f:
            json.dump(json_index, f, indent=2)

        print(f"\nIndex saved to {output_path}")

    def print_stats(self) -> None:
        """Print indexing statistics"""
        print("\n" + "="*60)
        print("ZIL INDEX STATISTICS")
        print("="*60)
        for category, defs in self.index.items():
            print(f"{category.upper():15s}: {len(defs):3d} definitions")
        print("="*60)
        print(f"{'TOTAL':15s}: {sum(len(d) for d in self.index.values()):3d} definitions")
        print("="*60)


class ZILQueryHelper:
    """Helper class for querying the ZIL index"""

    def __init__(self, index_file: str):
        with open(index_file, 'r') as f:
            self.index = json.load(f)

    def find(self, name: str) -> Optional[Dict]:
        """Find a definition by name"""
        for category, defs in self.index.items():
            if name in defs:
                return defs[name]
        return None

    def find_by_type(self, def_type: str) -> Dict:
        """Get all definitions of a type"""
        type_map = {
            'room': 'rooms',
            'object': 'objects',
            'routine': 'routines',
            'macro': 'macros',
            'global': 'globals',
            'constant': 'constants',
        }
        category = type_map.get(def_type.lower(), def_type.lower() + 's')
        return self.index.get(category, {})

    def find_with_property(self, property_name: str, property_value: str = None) -> List[Dict]:
        """Find all definitions with a specific property"""
        results = []
        for category, defs in self.index.items():
            for name, def_data in defs.items():
                props = def_data.get('properties', {})
                if property_name in props:
                    if property_value is None or property_value in str(props[property_name]):
                        results.append(def_data)
        return results

    def find_dependencies(self, name: str) -> List[str]:
        """Find what a definition depends on"""
        definition = self.find(name)
        if definition:
            return definition.get('dependencies', [])
        return []

    def find_dependents(self, name: str) -> List[str]:
        """Find what depends on this definition"""
        dependents = []
        for category, defs in self.index.items():
            for def_name, def_data in defs.items():
                if name in def_data.get('dependencies', []):
                    dependents.append(def_name)
        return dependents

    def search(self, query: str) -> List[Dict]:
        """Search for definitions matching query"""
        query_lower = query.lower()
        results = []

        for category, defs in self.index.items():
            for name, def_data in defs.items():
                # Search in name
                if query_lower in name.lower():
                    results.append(def_data)
                    continue

                # Search in properties
                props_str = json.dumps(def_data.get('properties', {})).lower()
                if query_lower in props_str:
                    results.append(def_data)
                    continue

                # Search in code snippet
                if query_lower in def_data.get('code_snippet', '').lower():
                    results.append(def_data)

        return results


def main():
    """Build the ZIL index"""
    import sys

    zil_dir = Path('/Users/don/gitrepos/zork1')

    print("Building ZIL source index...")
    print(f"Directory: {zil_dir}\n")

    indexer = ZILIndexer(zil_dir)
    indexer.parse_zil_files()
    indexer.print_stats()
    indexer.save_index()

    print("\nCreating query helper examples...")
    helper = ZILQueryHelper(zil_dir / "zil_index.json")

    # Example queries
    print("\nExample: Finding the THIEF object")
    thief = helper.find('THIEF')
    if thief:
        print(f"  Found in: {thief['file']}")
        print(f"  Lines: {thief['line_start']}-{thief['line_end']}")
        print(f"  Properties: {list(thief.get('properties', {}).keys())}")

    print("\nExample: All objects with WEAPONBIT")
    weapons = helper.find_with_property('flags', 'WEAPONBIT')
    print(f"  Found {len(weapons)} weapons:")
    for w in weapons[:5]:
        print(f"    - {w['name']}")

    print("\nExample: What depends on LAMP?")
    dependents = helper.find_dependents('LAMP')
    print(f"  {len(dependents)} definitions reference LAMP")
    if dependents:
        print(f"  Examples: {', '.join(dependents[:5])}")

    print("\n✓ Index built successfully!")
    print(f"  Use 'ZILQueryHelper(\"zil_index.json\")' to query the index")


if __name__ == '__main__':
    main()
