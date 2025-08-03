# Contest Log Analyzer/contest_tools/core_annotations/get_cty.py
#
# Purpose: Provides the CtyLookup class for determining DXCC/WAE entities,
#          zones, and other geographical data from amateur radio callsigns
#          based on the CTY.DAT file. This is a refactored version based
#          on the detailed algorithm specification.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-02
# Version: 0.28.1-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# --- Revision History ---
# All notable changes to this project will be documented in this file.
# The format is based on "Keep a Changelog" (https://keepachangelog.com/en/1.0.0/),
# and this project aims to adhere to Semantic Versioning (https://semver.org/).
## [0.28.1-Beta] - 2025-08-02
### Added
# - Added a `portableid` field to the return tuples to pass the identified
#   portable designator to downstream routines.
### Fixed
# - Added a high-priority check to invalidate `digit/call` portable formats
#   (e.g., `7/KD4D`), which the previous logic did not handle.
#
## [0.27.1-Beta] - 2025-08-02
### Fixed
# - Corrected a bug in the get_cty_DXCC_WAE merge logic where the CtyInfo
#   tuple was being unpacked into variables in the wrong order. The logic
#   now unpacks by field name to prevent column shifts in the output.
## [0.27.0-Beta] - 2025-08-02
### Changed
# - Complete refactoring of the module to align with the "Definitive
#   Callsign Lookup Algorithm Specification v1.4.0". The logic is now
#   functionally identical but implemented in a cleaner, more maintainable
#   structure. This replaces all previous versions.

from typing import List, Dict, Optional, Tuple
import re
from collections import namedtuple
import sys
import os
import argparse

class CtyLookup:
    """
    A class to lookup amateur radio callsigns and determine their
    associated country (DXCC entity), CQ Zone, ITU Zone, and Continent
    based on the CTY.DAT file, following a precise, ordered algorithm.
    """

    # --- Data Structures ---
    CtyInfo = namedtuple('CtyInfo', 'name CQZone ITUZone Continent Lat Lon Tzone DXCC portableid')
    FullCtyInfo = namedtuple('FullCtyInfo', 'DXCCName DXCCPfx CQZone ITUZone Continent Lat Lon Tzone WAEName WAEPfx portableid')
    UNKNOWN_ENTITY = CtyInfo("Unknown", "Unknown", "Unknown", "Unknown", "0.0", "0.0", "0.0", "Unknown", "")

    # --- US/Canada Structural Patterns for Portable Logic ---
    _US_PATTERN = re.compile(r'^(A[A-L]|K|N|W)[A-Z]?[0-9]')
    _CA_PATTERN = re.compile(r'^(C[F-Z]|V[A-G]|V[O-Y]|X[J-O])[0-9]')

    def __init__(self, cty_dat_path: str):
        self.filename = cty_dat_path
        self.dxccprefixes: Dict[str, CtyLookup.CtyInfo] = {}
        self.waeprefixes: Dict[str, CtyLookup.CtyInfo] = {}

        if not os.path.exists(self.filename):
            raise FileNotFoundError(f"CTY.DAT file not found: {self.filename}")
        
        self._parse_cty_file()
        self._validate_patterns()

    def _parse_cty_file(self):
        """Parses the CTY.DAT file and populates the prefix dictionaries."""
        try:
            with open(self.filename, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            raise IOError(f"Error reading CTY.DAT file {self.filename}: {e}")

        # Pre-process the file content to handle comments and multi-line aliases
        content = re.sub(r';[^\n\r]*', ';', content)
        content = re.sub(r'\s*&\s*', ',', content)
        
        for record in content.split(';'):
            record = record.strip()
            if not record:
                continue
            
            self._parse_record(record)

    def _parse_record(self, record: str):
        """Parses a single entity record from the CTY.DAT file."""
        parts = record.split(':', 8)
        if len(parts) < 8:
            return # Skip malformed records

        entity_info_base = [p.strip() for p in parts[0:8]]
        entity_info = self.CtyInfo(*entity_info_base, portableid="") # Add blank portableid
        
        primary_prefix = entity_info.DXCC
        aliases_str = parts[8] if len(parts) > 8 else ""
        
        is_wae = primary_prefix.startswith('*')
        target_dict = self.waeprefixes if is_wae else self.dxccprefixes
        
        # Store the primary prefix (without the '*' if WAE)
        key = primary_prefix[1:] if is_wae else primary_prefix
        target_dict[key] = entity_info

        # Parse and store all aliases for this entity
        for alias in aliases_str.split(','):
            alias = alias.strip()
            if not alias:
                continue

            is_exact = alias.startswith('=') or re.search(r'[\[({]', alias)
            
            # Extract base prefix and any overrides
            match = re.match(r'=?([A-Z0-9\-\/]+)', alias)
            if not match:
                continue
            base_prefix = match.group(1)
            
            # Apply overrides to create a new CtyInfo object for the alias
            info_list = list(entity_info_base)
            cq_m = re.search(r'\((\d+)\)', alias)
            if cq_m: info_list[1] = cq_m.group(1)
            itu_m = re.search(r'\[(\d+)\]', alias)
            if itu_m: info_list[2] = itu_m.group(1)
            cont_m = re.search(r'\{([A-Z]{2})\}', alias)
            if cont_m: info_list[3] = cont_m.group(1)
            final_info = self.CtyInfo(*info_list, portableid="") # Add blank portableid
            
            if is_exact:
                target_dict["=" + base_prefix] = final_info
            
            # A non-exact alias is also a prefix match
            if not alias.startswith('='):
                target_dict[base_prefix] = final_info

    def _validate_patterns(self):
        """Validates US/CA prefixes from the CTY file against regex patterns."""
        us_mismatches, ca_mismatches = [], []
        for pfx, info in self.dxccprefixes.items():
            if pfx.startswith(('=', 'VER')): continue
            test_call = f"{pfx}1A" # Create a structurally valid test call
            if info.name == "United States" and not self._US_PATTERN.match(test_call):
                us_mismatches.append(pfx)
            elif info.name == "Canada" and not self._CA_PATTERN.match(test_call):
                ca_mismatches.append(pfx)
        if us_mismatches:
            print(f"Warning: US prefixes from '{self.filename}' fail pattern match: {', '.join(us_mismatches)}", file=sys.stderr)
        if ca_mismatches:
            print(f"Warning: Canadian prefixes from '{self.filename}' fail pattern match: {', '.join(ca_mismatches)}", file=sys.stderr)

    def get_cty_DXCC_WAE(self, callsign: str) -> FullCtyInfo:
        """
        Primary entry point. Performs two lookups and merges the results
        according to the specification.
        """
        # 1. Perform DXCC-Only Lookup
        dxcc_res_obj = self.get_cty(callsign, wae=False)

        # 2. Perform WAE-Priority Lookup
        wae_res_obj = self.get_cty(callsign, wae=True)

        # 3. Merge Results
        base_info = self.UNKNOWN_ENTITY._asdict()
        dxcc_name, cq, itu, cont, lat, lon, tz, dxcc_pfx = (
            base_info['name'], base_info['CQZone'], base_info['ITUZone'], base_info['Continent'],
            base_info['Lat'], base_info['Lon'], base_info['Tzone'], base_info['DXCC']
        )
        wae_name, wae_pfx = "", ""
        portableid = ""

        if dxcc_res_obj.name != "Unknown":
            dxcc_name = dxcc_res_obj.name
            cq = dxcc_res_obj.CQZone
            itu = dxcc_res_obj.ITUZone
            cont = dxcc_res_obj.Continent
            lat = dxcc_res_obj.Lat
            lon = dxcc_res_obj.Lon
            tz = dxcc_res_obj.Tzone
            dxcc_pfx = dxcc_res_obj.DXCC

        if wae_res_obj.name != "Unknown":
            cq = wae_res_obj.CQZone
            itu = wae_res_obj.ITUZone
            cont = wae_res_obj.Continent
            lat = wae_res_obj.Lat
            lon = wae_res_obj.Lon
            tz = wae_res_obj.Tzone
            portableid = wae_res_obj.portableid
            
            if wae_res_obj.DXCC.startswith('*'):
                wae_name = wae_res_obj.name
                wae_pfx = wae_res_obj.DXCC
        
        return self.FullCtyInfo(dxcc_name, dxcc_pfx, cq, itu, cont, lat, lon, tz, wae_name, wae_pfx, portableid)

    def get_cty(self, callsign: str, wae: bool = True) -> CtyInfo:
        """
        Core logic function that implements the ordered lookup algorithm.
        """
        # Step 1: Pre-processing
        processed_call = self._preprocess_callsign(callsign)

        # Step 2: Exact Match
        result = self._check_exact_match(processed_call, wae)
        if result: return result

        # Step 3: Hardcoded Special Cases
        result = self._check_special_cases(processed_call)
        if result: return result

        # Step 4: Portable Callsign Logic
        if '/' in processed_call:
            result = self._handle_portable_call(processed_call, wae)
            if result: return result

        # Step 5: Longest Prefix Match
        result = self._find_longest_prefix(processed_call, wae)
        if result: return result

        return self.UNKNOWN_ENTITY

    def _preprocess_callsign(self, call: str) -> str:
        """Implements Step 1 of the algorithm."""
        call = call.upper().strip()
        call = call.partition('-')[0]
        for suffix in ["/P", "/B", "/M", "/QRP"]:
            if call.endswith(suffix):
                call = call[:-len(suffix)]
                break
        return call

    def _check_exact_match(self, call: str, wae: bool) -> Optional[CtyInfo]:
        """Implements Step 2 of the algorithm."""
        if wae:
            if (entity := self.waeprefixes.get("=" + call)): return entity
        if (entity := self.dxccprefixes.get("=" + call)): return entity
        return None

    def _check_special_cases(self, call: str) -> Optional[CtyInfo]:
        """Implements Step 3 of the algorithm."""
        if call.endswith("/MM"):
            return self.UNKNOWN_ENTITY

        # Guantanamo Bay Rule (corrected logic)
        if re.fullmatch(r'KG4[A-Z]{2}', call):
            return self.dxccprefixes.get("KG4")
        if '/' in call and any(re.fullmatch(r'KG4[A-Z]{2}', part) for part in call.split('/')):
            return self.UNKNOWN_ENTITY
        
        return None

    def _handle_portable_call(self, call: str, wae: bool) -> Optional[CtyInfo]:
        """Implements Step 4 of the algorithm."""
        parts = call.split('/')
        p1, p2 = parts[0], parts[-1]

        # New high-priority check for invalid digit/call format
        if len(p1) == 1 and p1.isdigit() and not p2.isdigit():
            return self.UNKNOWN_ENTITY

        def is_valid_prefix(p):
            if p in self.dxccprefixes: return True
            if wae and p in self.waeprefixes: return True
            return False

        # 4a. Unambiguous Prefix Rule
        p1_is_pfx, p2_is_pfx = is_valid_prefix(p1), is_valid_prefix(p2)
        if p1_is_pfx and not p2_is_pfx:
            return self._get_prefix_entity(p1, wae)._replace(portableid=p1)
        if p2_is_pfx and not p1_is_pfx:
            return self._get_prefix_entity(p2, wae)._replace(portableid=p2)

        # 4b. "Strip the Digit" Heuristic
        p1s = p1[:-1] if len(p1) > 1 and p1[-1].isdigit() and not p1[-2].isdigit() else None
        p2s = p2[:-1] if len(p2) > 1 and p2[-1].isdigit() and not p2[-2].isdigit() else None
        if p1s or p2s:
            p1s_is_pfx = is_valid_prefix(p1s) if p1s else False
            p2s_is_pfx = is_valid_prefix(p2s) if p2s else False
            if p1s_is_pfx and not p2s_is_pfx:
                return self._get_prefix_entity(p1s, wae)._replace(portableid=p1)
            if p2s_is_pfx and not p1s_is_pfx:
                return self._get_prefix_entity(p2s, wae)._replace(portableid=p2)

        # 4c. US/Canada Heuristic
        if len(p2) == 1 and p2.isdigit() and (self._US_PATTERN.match(p1) or self._CA_PATTERN.match(p1)):
            cty_info = self._find_longest_prefix(p1, wae)
            if cty_info:
                return cty_info._replace(portableid=p2)
            return self.UNKNOWN_ENTITY

        # 4d. Final Portable Fallback
        p1_info = self._find_longest_prefix(p1, wae)
        p2_info = self._find_longest_prefix(p2, wae)
        
        is_p1_usca = bool(self._US_PATTERN.match(p1) or self._CA_PATTERN.match(p1))
        
        if is_p1_usca:
            if p2_info: return p2_info._replace(portableid=p2)
            if p1_info: return p1_info._replace(portableid=p1)
        else:
            if p1_info: return p1_info._replace(portableid=p1)
            if p2_info: return p2_info._replace(portableid=p2)
        
        return None

    def _find_longest_prefix(self, call: str, wae: bool) -> Optional[CtyInfo]:
        """Implements Step 5 of the algorithm."""
        temp = call
        while len(temp) > 0:
            if (entity := self._get_prefix_entity(temp, wae)):
                return entity
            temp = temp[:-1]
        return None

    def _get_prefix_entity(self, prefix: str, wae: bool) -> Optional[CtyInfo]:
        """Helper to get an entity, checking WAE first if enabled."""
        if wae:
            if (entity := self.waeprefixes.get(prefix)): return entity
        if (entity := self.dxccprefixes.get(prefix)): return entity
        return None

# --- Standalone Execution for Testing ---
def _run_lookup(cty: CtyLookup, call: str):
    res = cty.get_cty_DXCC_WAE(call)
    print(f"\n> {call}\n  Comprehensive: DXCC Name: {res.DXCCName:<20}, DXCC Pfx: {res.DXCCPfx:<10}\n"
          f"                   WAE Name:  {res.WAEName:<20}, WAE Pfx:  {res.WAEPfx:<10}\n"
          f"                   Zones: CQ {res.CQZone}, ITU {res.ITUZone}, Cont: {res.Continent}\n"
          f"                   Portable ID: {res.portableid}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CTY.DAT lookup tool.")
    parser.add_argument('callsign_file', nargs='?', default=None,
                        help="Optional path to a file containing callsigns to look up, one per line.")
    args = parser.parse_args()

    data_dir = os.environ.get('CONTEST_DATA_DIR')
    if not data_dir:
        print("Error: CONTEST_DATA_DIR environment variable not set.", file=sys.stderr)
        sys.exit(1)
    
    cty_path = os.path.join(data_dir.strip().strip('"').strip("'"), 'cty.dat')

    if not os.path.exists(cty_path):
        print(f"Error: The file '{cty_path}' could not be found.", file=sys.stderr)
        sys.exit(1)
    try:
        cty_main = CtyLookup(cty_dat_path=cty_path)
        print(f"Successfully loaded CTY file from: {cty_main.filename}")
    except (FileNotFoundError, IOError) as e:
        print(f"Error initializing CtyLookup: {e}", file=sys.stderr)
        sys.exit(1)
    
    if args.callsign_file:
        infile = args.callsign_file
        if not os.path.exists(infile):
            print(f"Error: Input file '{infile}' not found.", file=sys.stderr)
            sys.exit(1)
        print(f"\n--- Processing callsigns from file: {infile} ---")
        with open(infile, 'r') as f:
            for line in f:
                if call := line.strip():
                    _run_lookup(cty_main, call)
    else:
        print("\n--- Interactive Mode ---\nEnter callsigns to lookup. Type Ctrl+D (Unix) or Ctrl+Z+Enter (Windows) to quit.")
        while True:
            try:
                call_in = input("\nEnter callsign: ").strip()
                if call_in:
                    _run_lookup(cty_main, call_in)
            except EOFError:
                print("\nExiting.")
                break
            except Exception as e:
                print(f"An error occurred: {e}", file=sys.stderr)