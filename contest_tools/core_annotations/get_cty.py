# Contest Log Analyzer/contest_tools/core_annotations/get_cty.py
#
# Purpose: Provides the CtyLookup class for determining DXCC/WAE entities,
#          zones, and other geographical data from amateur radio callsigns
#          based on the CTY.DAT file.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-29
# Version: 0.21.8-Beta
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

## [0.21.8-Beta] - 2025-07-29
### Fixed
# - Corrected the order of exact-match lookups to prioritize the WAE list
#   when WAE lookups are enabled. This ensures that callsigns that are aliases
#   for both a DXCC and a WAE entity (e.g., 4U1A) are resolved correctly.

## [0.21.7-Beta] - 2025-07-28
### Fixed
# - Corrected the logic in 'get_cty_DXCC_WAE' to properly prioritize the
#   continent, CQ zone, and ITU zone from the WAE lookup result when one is
#   available. This ensures correct scoring for entities like *TA1 and *IG9.

## [0.21.6-Beta] - 2025-07-28
### Removed
# - Removed the '--cty-file' command-line argument from the standalone
#   execution block to ensure it relies solely on the CTY_DAT_PATH
#   environment variable, consistent with the main application.

## [0.21.5-Beta] - 2025-07-28
### Added
# - Added a '--cty-file' command-line argument to the standalone execution
#   block (__main__) to allow specifying a country file, overriding the
#   CTY_DAT_PATH environment variable for easier debugging.

## [0.21.4-Beta] - 2025-07-28
### Changed
# - Implemented a "strip the digit" heuristic for portable callsigns. If an
#   unambiguous location cannot be found, the logic will now strip a single
#   trailing digit from a prefix and re-check, correctly resolving calls
#   like 'CT7/VA3FH' to Portugal.

## [0.21.1-Beta] - 2025-07-27
### Changed
# - Implemented a new high-priority rule for portable callsigns (A/B). If
#   exactly one of A or B is a direct prefix match in the CTY file, it is
#   now immediately used as the location, fixing lookups for calls like
#   'KH0/4Z5LA'. The more complex pattern-matching logic is now only used
#   as a fallback for ambiguous cases.

## [0.20.3-Beta] - 2025-07-27
### Fixed
# - Corrected a regression bug in the CTY.DAT parser. Prefixes with overrides
#   (e.g., 'VO2(2)') are now correctly stored as both an exact match AND a
#   regular prefix. This restores the ability to look up callsigns like
#   'VO2AC' while preserving the special override rules.

## [0.20.2-Beta] - 2025-07-27
### Fixed
# - Corrected the Canadian callsign regex pattern to include the full range of
#   official prefixes (CZ and XO), resolving validation warnings.
# - Added a hard-coded exception to the validation logic to ignore special
#   versioning prefixes (e.g., 'VER20250718') found in some cty.dat files.

## [0.20.1-Beta] - 2025-07-27
### Fixed
# - Corrected the comprehensive pattern validation logic. It now creates a
#   structurally valid test callsign (e.g., 'K1A') from each prefix,
#   preventing false negative warnings.

## [0.20.0-Beta] - 2025-07-27
### Changed
# - Expanded the pattern validation logic to be comprehensive. It now checks
#   all non-exact US and Canadian aliases from the loaded cty.dat file against
#   the internal regex patterns, reporting any discrepancies.

## [0.19.1-Beta] - 2025-07-27
### Fixed
# - Corrected the pattern validation logic to ensure it only tests the primary
#   DXCC prefix for the USA and Canada, ignoring aliases (e.g., '=WZ8X').
#   This prevents erroneous warnings when loading a valid cty.dat file.

## [0.18.0-Beta] - 2025-07-27
### Changed
# - Eliminated the hard-coded '_US_CANADA_PRIMARY_PREFIXES' list. The logic
#   for resolving portable callsigns now uses a more robust and accurate
#   pattern-based approach to identify US and Canadian callsign structures.

## [0.17.0-Beta] - 2025-07-27
### Changed
# - Refactored the internal list of US/Canada prefixes to remove redundant
#   aliases and corrected several entries to match their primary DXCC prefix
#   (e.g., KL7 -> KL).
# - Added comments clarifying the list's purpose in resolving portable
#   callsign ambiguity (e.g., W1AW/KP4).

## [0.16.6-Beta] - 2025-07-27
### Fixed
# - Corrected the CTY file parser to properly handle end-of-line comments
#   (e.g., '; NA'). The new logic strips all text between a semicolon and
#   a newline, preventing comments from being merged with the next record.

## [0.16.5-Beta] - 2025-07-26
### Fixed
# - Rewrote the CTY file parsing logic to be more robust. It now correctly
#   handles complex, multi-line alias definitions (e.g., for Canada) in
#   standard cty.dat files, fixing a regression bug that caused lookups
#   for prefixes like VO2 and VY0 to fail.

## [0.16.4-Beta] - 2025-07-26
### Fixed
# - Corrected the CTY file parser to treat any alias with a zone, ITU, or
#   continent override (e.g., 'WN4AAA(3)') as an exact callsign match, even
#   if it lacks a leading '='. This resolves critical lookup failures with
#   simplified country files like cqww.cty.

## [0.16.0-Beta] - 2025-07-26
### Fixed
# - Corrected the CTY file parser to properly handle multi-line alias
#   definitions that use the '&' continuation character.
# - Corrected the CTY file parser to properly handle spaces within country
#   names, preventing names like "Rodriguez Island" from being compressed.

## [0.13.0-Beta] - 2025-07-22
### Fixed
# - The CTY.DAT parser is now flexible and can handle both the standard
#   8-field format and simplified contest-specific formats (like cqww.cty).

## [1.0.0-Final] - 2025-07-19
### Fixed
# - Finalized the slash-handling logic for portable callsigns, including
#   special rules for US/Canada, numeric suffixes, and exact matches.
# - Added logic to strip surrounding quotes from the CTY_DAT_PATH environment
#   variable in the standalone __main__ block.

## [0.9.0-Beta] - 2025-07-18
# - Initial release of the CtyLookup class.

from typing import List
import re
from collections import namedtuple
import sys
import os
import argparse

class CtyLookup:
    """
    A class to lookup amateur radio callsigns and determine their
    associated country (DXCC entity), CQ Zone, ITU Zone, and Continent
    based on the CTY.DAT file.
    """

    CtyInfo = namedtuple('CtyInfo', 'name CQZone ITUZone Continent Lat Lon Tzone DXCC')
    FullCtyInfo = namedtuple('FullCtyInfo', 'DXCCName DXCCPfx CQZone ITUZone Continent Lat Lon Tzone WAEName WAEPfx')

    _US_PATTERN = re.compile(r'^(A[A-L]|K|N|W)[A-Z]?[0-9]')
    _CA_PATTERN = re.compile(r'^(C[F-Z]|V[A-G]|V[O-Y]|X[J-O])[0-9]')


    def __init__(self, cty_dat_path: str, wae: bool = True):
        self.filename = cty_dat_path
        self.wae = wae
        self.KG4 = None
        self.dxccprefixes = {}
        self.waeprefixes = {}
        if not os.path.exists(self.filename): raise FileNotFoundError(f"CTY.DAT file not found: {self.filename}")
        try:
            with open(self.filename, 'r', encoding='utf-8', errors='ignore') as f: lines_content = f.read()
        except Exception as e: raise IOError(f"Error reading CTY.DAT file {self.filename}: {e}")
        lines_content = re.sub(r';[^\n\r]*', ';', lines_content)
        lines_content = re.sub(r'\s*&\s*', ',', lines_content)
        lines = lines_content.split(';')
        for l in lines:
            line = l.strip()
            if not line: continue
            fields = line.split(':', 8)
            cty_entity_info, primary_dxcc_code, raw_aliases_string = None, "", ""
            if len(fields) >= 8:
                cty_entity_info = self.CtyInfo(*[f.strip() for f in fields[0:8]])
                primary_dxcc_code = fields[7].strip()
                if len(fields) > 8: raw_aliases_string = fields[8]
            else:
                fields = line.split(':', 3)
                if len(fields) >= 3:
                    name, cq_zone, p_code = fields[0].strip(), fields[1].strip(), fields[2].strip()
                    cty_entity_info = self.CtyInfo(name, cq_zone, "0", "Unknown", "0.0", "0.0", "0.0", p_code)
                    if len(fields) > 3: raw_aliases_string = fields[3]
            if not cty_entity_info: continue
            is_wae = primary_dxcc_code.startswith('*')
            p_key = primary_dxcc_code[1:] if is_wae else primary_dxcc_code
            target = self.waeprefixes if is_wae else self.dxccprefixes
            if p_key == "KG4": self.KG4 = cty_entity_info
            else: target[p_key] = cty_entity_info
            if raw_aliases_string:
                for alias in raw_aliases_string.split(","):
                    alias = alias.strip()
                    if not alias: continue
                    is_exact = alias.startswith('=') or re.search(r'[\(\[\{]', alias)
                    parsed_alias = alias[1:] if alias.startswith('=') else alias
                    match = re.match(r'([A-Z0-9\-\/]+)', parsed_alias)
                    if not match: continue
                    base_pfx = match.group(1)
                    info_list = list(cty_entity_info)
                    cq_m = re.search(r'\((\d+)\)', parsed_alias);
                    if cq_m: info_list[1] = cq_m.group(1)
                    itu_m = re.search(r'\[(\d+)\]', parsed_alias);
                    if itu_m: info_list[2] = itu_m.group(1)
                    cont_m = re.search(r'\{([A-Z]{2})\}', parsed_alias);
                    if cont_m: info_list[3] = cont_m.group(1)
                    final_info = self.CtyInfo(*info_list)
                    if is_exact: target["=" + base_pfx] = final_info
                    if not alias.startswith('='): target[base_pfx] = final_info
        self._validate_patterns()

    def _validate_patterns(self):
        us_mismatches, ca_mismatches = [], []
        for pfx, info in self.dxccprefixes.items():
            if pfx.startswith(('=', 'VER')): continue
            test_call = f"{pfx}1A" 
            if info.name == "United States" and not self._US_PATTERN.match(test_call): us_mismatches.append(pfx)
            elif info.name == "Canada" and not self._CA_PATTERN.match(test_call): ca_mismatches.append(pfx)
        if us_mismatches: print(f"Warning: US prefixes from '{self.filename}' fail pattern match: {', '.join(us_mismatches)}", file=sys.stderr)
        if ca_mismatches: print(f"Warning: Canadian prefixes from '{self.filename}' fail pattern match: {', '.join(ca_mismatches)}", file=sys.stderr)

    def findprefix(self, call):
        temp = call
        while len(temp) > 0:
            if self.wae and temp in self.waeprefixes: return self.waeprefixes[temp]
            elif temp in self.dxccprefixes: return self.dxccprefixes[temp]
            temp = temp[:-1]
        return None

    def get_cty(self, csign):
        UNKNOWN = self.CtyInfo("Unknown", "Unknown", "Unknown", "Unknown", "0.0", "0.0", "0.0", "Unknown")
        call = csign.upper().strip().partition('-')[0]
        for s in ["/P", "/B", "/M", "/QRP"]:
            if call.endswith(s): call = call[:-len(s)]; break
        
        if self.wae and "=" + call in self.waeprefixes: return self.waeprefixes["=" + call]
        if "=" + call in self.dxccprefixes: return self.dxccprefixes["=" + call]

        if call.endswith("/MM"): return UNKNOWN
        if call.startswith("KG4"):
            if len(call) == 5 and re.match(r"KG4[A-Z]{2}$", call):
                if self.KG4: return self.KG4
            return self.dxccprefixes.get("K", UNKNOWN)
        parts = call.split('/')
        if len(parts) > 1:
            p1, p2 = parts[0], parts[-1]
            p1_is_pfx = p1 in self.dxccprefixes or (self.wae and p1 in self.waeprefixes)
            p2_is_pfx = p2 in self.dxccprefixes or (self.wae and p2 in self.waeprefixes)
            if p1_is_pfx and not p2_is_pfx: return self.dxccprefixes.get(p1) or self.waeprefixes.get(p1)
            if p2_is_pfx and not p1_is_pfx: return self.dxccprefixes.get(p2) or self.waeprefixes.get(p2)
            p1s = p1[:-1] if len(p1) > 1 and p1[-1].isdigit() and not p1[-2].isdigit() else None
            p2s = p2[:-1] if len(p2) > 1 and p2[-1].isdigit() and not p2[-2].isdigit() else None
            p1s_is_pfx = p1s and (p1s in self.dxccprefixes or (self.wae and p1s in self.waeprefixes))
            p2s_is_pfx = p2s and (p2s in self.dxccprefixes or (self.wae and p2s in self.waeprefixes))
            if p1s_is_pfx and not p2s_is_pfx: return self.dxccprefixes.get(p1s) or self.waeprefixes.get(p1s)
            if p2s_is_pfx and not p1s_is_pfx: return self.dxccprefixes.get(p2s) or self.waeprefixes.get(p2s)
            def is_usca(s): return bool(self._US_PATTERN.match(s) or self._CA_PATTERN.match(s))
            if len(p2) == 1 and p2.isdigit() and is_usca(p1): return self.findprefix(p1)
            p1_info, p2_info = self.findprefix(p1), self.findprefix(p2)
            if is_usca(p1): return p2_info if p2_info else p1_info
            if p1_info: return p1_info
            if p2_info: return p2_info
            return UNKNOWN
        result = self.findprefix(call)
        return result if result else UNKNOWN

    def get_cty_DXCC_WAE(self, callsign):
        original_wae_setting = self.wae
        self.wae = False
        dxcc_res_obj = self.get_cty(callsign)
        self.wae = True
        wae_res_obj = self.get_cty(callsign)
        self.wae = original_wae_setting
        dxcc_name, dxcc_pfx, cq, itu, cont, lat, lon, tz = "Unknown", "Unknown", "Unknown", "Unknown", "Unknown", "0.0", "0.0", "0.0"
        wae_name, wae_pfx = "", ""
        if dxcc_res_obj and dxcc_res_obj.name != "Unknown":
            dxcc_name, cq, itu, cont, lat, lon, tz, dxcc_pfx = dxcc_res_obj
        if wae_res_obj and wae_res_obj.name != "Unknown":
            _, cq, itu, cont, lat, lon, tz, _ = wae_res_obj
            if wae_res_obj.DXCC.startswith('*'):
                wae_name = wae_res_obj.name
                wae_pfx = wae_res_obj.DXCC
                if dxcc_name == "Unknown":
                    dxcc_name = wae_res_obj.name
        return self.FullCtyInfo(dxcc_name, dxcc_pfx, cq, itu, cont, lat, lon, tz, wae_name, wae_pfx)

def _run_lookup(cty, call):
    res = cty.get_cty_DXCC_WAE(call)
    print(f"\n> {call}\n  Comprehensive: DXCC Name: {res.DXCCName:<20}, DXCC Pfx: {res.DXCCPfx:<10}\n"
          f"                   WAE Name:  {res.WAEName:<20}, WAE Pfx:  {res.WAEPfx:<10}\n"
          f"                   Zones: CQ {res.CQZone}, ITU {res.ITUZone}, Cont: {res.Continent}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CTY.DAT lookup tool.")
    parser.add_argument('callsign_file', nargs='?', default=None,
                        help="Optional path to a file containing callsigns to look up, one per line.")
    args = parser.parse_args()

    path = os.environ.get('CTY_DAT_PATH')
    if not path: print("Error: CTY_DAT_PATH environment variable not set.", file=sys.stderr); sys.exit(1)
    cty_path = path.strip().strip('"').strip("'")
    if not os.path.exists(cty_path): print(f"Error: The file '{cty_path}' could not be found.", file=sys.stderr); sys.exit(1)
    try:
        cty_main = CtyLookup(cty_dat_path=cty_path)
        print(f"Successfully loaded CTY file from: {cty_main.filename}")
    except (FileNotFoundError, IOError) as e: print(f"Error initializing CtyLookup: {e}", file=sys.stderr); sys.exit(1)
    
    if args.callsign_file:
        infile = args.callsign_file
        if not os.path.exists(infile): print(f"Error: Input file '{infile}' not found.", file=sys.stderr); sys.exit(1)
        print(f"\n--- Processing callsigns from file: {infile} ---")
        with open(infile, 'r') as f:
            for line in f:
                if call := line.strip(): _run_lookup(cty_main, call)
    else:
        print("\n--- Interactive Mode ---\nEnter callsigns to lookup. Type Ctrl+D (Unix) or Ctrl+Z+Enter (Windows) to quit.")
        while True:
            try:
                call_in = input("\nEnter callsign: ").strip()
                if call_in: _run_lookup(cty_main, call_in)
            except EOFError: print("\nExiting."); break
            except Exception as e: print(f"An error occurred: {e}", file=sys.stderr)
