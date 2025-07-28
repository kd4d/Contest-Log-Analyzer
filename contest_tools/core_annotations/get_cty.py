# Contest Log Analyzer/contest_tools/core_annotations/get_cty.py
#
# Purpose: Provides the CtyLookup class for determining DXCC/WAE entities,
#          zones, and other geographical data from amateur radio callsigns
#          based on the CTY.DAT file.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-28
# Version: 0.21.4-Beta
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

## [0.21.4-Beta] - 2025-07-28
### Changed
# - Implemented a "strip the digit" heuristic for portable callsigns. If an
#   unambiguous location cannot be found, the logic will now strip a single
#   trailing digit from a prefix and re-check, correctly resolving calls
#   like 'CT7/VA3FH' to Portugal.

## [0.21.3-Beta] - 2025-07-28
### Fixed
# - The inset summary table now has a solid background color, which makes it
#   opaque and prevents the plot's grid lines from showing through.

## [0.21.2-Beta] - 2025-07-28
### Changed
# - The standalone execution block (__main__) now supports two modes:
#   1. If a filename is provided as a command-line argument, it processes
#      callsigns from that file.
#   2. If no filename is provided, it enters an interactive prompt for
#      individual callsign lookups.

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

class CtyLookup:
    """
    A class to lookup amateur radio callsigns and determine their
    associated country (DXCC entity), CQ Zone, ITU Zone, and Continent
    based on the CTY.DAT file.
    """

    CtyInfo = namedtuple('CtyInfo', 'name CQZone ITUZone Continent Lat Lon Tzone DXCC')
    FullCtyInfo = namedtuple('FullCtyInfo', 'DXCCName DXCCPfx CQZone ITUZone Continent Lat Lon Tzone WAEName WAEPfx')

    # --- Patterns for identifying US and Canadian callsign structures ---
    # Used to resolve ambiguity in portable callsigns (e.g., W1AW/KP4 vs. EA8/W1AW)
    _US_PATTERN = re.compile(r'^(A[A-L]|K|N|W)[A-Z]?[0-9]')
    _CA_PATTERN = re.compile(r'^(C[F-Z]|V[A-G]|V[O-Y]|X[J-O])[0-9]')


    def __init__(self, cty_dat_path: str, wae: bool = True):
        self.filename = cty_dat_path
        self.wae = wae
        self.KG4 = None

        self.dxccprefixes = {}
        self.waeprefixes = {}

        if not os.path.exists(self.filename):
            raise FileNotFoundError(f"CTY.DAT file not found at the specified path: {self.filename}")

        try:
            with open(self.filename, 'r', encoding='utf-8', errors='ignore') as fcty:
                lines_content = fcty.read()
        except Exception as e:
            raise IOError(f"Error reading CTY.DAT file {self.filename}: {e}")

        lines_content = re.sub(r';[^\n\r]*', ';', lines_content)
        lines_content = re.sub(r'\s*&\s*', ',', lines_content)
        lines = lines_content.split(';')

        for l in lines:
            line = l.strip()
            if not line:
                continue

            fields = line.split(':', 8)
            
            cty_entity_info = None
            primary_dxcc_code = ""
            raw_aliases_string = ""

            if len(fields) >= 8:
                cty_entity_info = self.CtyInfo(*[f.strip() for f in fields[0:8]])
                primary_dxcc_code = fields[7].strip()
                if len(fields) > 8:
                    raw_aliases_string = fields[8]
            else:
                fields = line.split(':', 3)
                if len(fields) >= 3:
                    name = fields[0].strip()
                    cq_zone = fields[1].strip()
                    primary_dxcc_code = fields[2].strip()
                    cty_entity_info = self.CtyInfo(name, cq_zone, "0", "Unknown", "0.0", "0.0", "0.0", primary_dxcc_code)
                    if len(fields) > 3:
                        raw_aliases_string = fields[3]

            if not cty_entity_info:
                continue

            is_wae_entity = primary_dxcc_code.startswith('*')
            primary_prefix_key_str = primary_dxcc_code[1:] if is_wae_entity else primary_dxcc_code
            target_dict = self.waeprefixes if is_wae_entity else self.dxccprefixes

            if primary_prefix_key_str == "KG4":
                self.KG4 = cty_entity_info
            else:
                target_dict[primary_prefix_key_str] = cty_entity_info

            if raw_aliases_string:
                aliases = raw_aliases_string.split(",")
                for alias_entry in aliases:
                    alias_entry = alias_entry.strip()
                    if not alias_entry:
                        continue

                    is_forced_exact = alias_entry.startswith('=')
                    has_override = re.search(r'[\(\[\{]', alias_entry)
                    is_exact_match = is_forced_exact or has_override
                    parsed_alias_entry = alias_entry[1:] if is_forced_exact else alias_entry
                    base_prefix_match = re.match(r'([A-Z0-9\-\/]+)', parsed_alias_entry)
                    if not base_prefix_match:
                        continue
                    base_pfx_for_alias = base_prefix_match.group(1)
                    current_alias_info_list = list(cty_entity_info)
                    cq_zone_match = re.search(r'\((\d+)\)', parsed_alias_entry)
                    if cq_zone_match: current_alias_info_list[1] = cq_zone_match.group(1)
                    itu_zone_match = re.search(r'\[(\d+)\]', parsed_alias_entry)
                    if itu_zone_match: current_alias_info_list[2] = itu_zone_match.group(1)
                    continent_match = re.search(r'\{([A-Z]{2})\}', parsed_alias_entry)
                    if continent_match: current_alias_info_list[3] = continent_match.group(1)
                    final_alias_cty_info = self.CtyInfo(*current_alias_info_list)
                    if is_exact_match: target_dict["=" + base_pfx_for_alias] = final_alias_cty_info
                    if not is_forced_exact: target_dict[base_pfx_for_alias] = final_alias_cty_info
        self._validate_patterns()

    def _validate_patterns(self):
        us_mismatches, ca_mismatches = [], []
        for prefix, info in self.dxccprefixes.items():
            if prefix.startswith(('=', 'VER')): continue
            test_call = f"{prefix}1A" 
            if info.name == "United States":
                if not self._US_PATTERN.match(test_call): us_mismatches.append(prefix)
            elif info.name == "Canada":
                if not self._CA_PATTERN.match(test_call): ca_mismatches.append(prefix)
        if us_mismatches: print(f"Warning: US prefixes from '{self.filename}' fail pattern match: {', '.join(us_mismatches)}", file=sys.stderr)
        if ca_mismatches: print(f"Warning: Canadian prefixes from '{self.filename}' fail pattern match: {', '.join(ca_mismatches)}", file=sys.stderr)

    def findprefix(self, callsign_segment):
        temp = callsign_segment
        while len(temp) > 0:
            if self.wae and temp in self.waeprefixes: return self.waeprefixes[temp]
            elif temp in self.dxccprefixes: return self.dxccprefixes[temp]
            temp = temp[:-1]
        return None

    def get_cty(self, csign):
        UNKNOWN_CTY_INFO = self.CtyInfo("Unknown", "Unknown", "Unknown", "Unknown", "0.0", "0.0", "0.0", "Unknown")
        callsign = csign.upper().strip().partition('-')[0]
        for suffix in ["/P", "/B", "/M", "/QRP"]:
            if callsign.endswith(suffix):
                callsign = callsign[:-len(suffix)]
                break
        if "=" + callsign in self.dxccprefixes: return self.dxccprefixes["=" + callsign]
        if self.wae and "=" + callsign in self.waeprefixes: return self.waeprefixes["=" + callsign]
        if callsign.endswith("/MM"): return UNKNOWN_CTY_INFO
        if callsign.startswith("KG4"):
            if len(callsign) == 5 and re.match(r"KG4[A-Z]{2}$", callsign):
                if self.KG4: return self.KG4
            return self.dxccprefixes.get("K", UNKNOWN_CTY_INFO)

        parts = callsign.split('/')
        if len(parts) > 1:
            part1, part2 = parts[0], parts[-1]
            
            # --- Heuristic 1: Unambiguous Prefix Match ---
            part1_is_prefix = part1 in self.dxccprefixes or (self.wae and part1 in self.waeprefixes)
            part2_is_prefix = part2 in self.dxccprefixes or (self.wae and part2 in self.waeprefixes)
            if part1_is_prefix and not part2_is_prefix: return self.dxccprefixes.get(part1) or self.waeprefixes.get(part1)
            if part2_is_prefix and not part1_is_prefix: return self.dxccprefixes.get(part2) or self.waeprefixes.get(part2)

            # --- Heuristic 2: Strip Trailing Digit ---
            part1_stripped = part1[:-1] if len(part1) > 1 and part1[-1].isdigit() and not part1[-2].isdigit() else None
            part2_stripped = part2[:-1] if len(part2) > 1 and part2[-1].isdigit() and not part2[-2].isdigit() else None
            
            part1_strip_is_prefix = part1_stripped and (part1_stripped in self.dxccprefixes or (self.wae and part1_stripped in self.waeprefixes))
            part2_strip_is_prefix = part2_stripped and (part2_stripped in self.dxccprefixes or (self.wae and part2_stripped in self.waeprefixes))
            
            if part1_strip_is_prefix and not part2_strip_is_prefix: return self.dxccprefixes.get(part1_stripped) or self.waeprefixes.get(part1_stripped)
            if part2_strip_is_prefix and not part1_strip_is_prefix: return self.dxccprefixes.get(part2_stripped) or self.waeprefixes.get(part2_stripped)

            # --- Heuristic 3: Fallback to Structural Patterns ---
            def is_us_ca_system(pfx_str): return bool(self._US_PATTERN.match(pfx_str) or self._CA_PATTERN.match(pfx_str))
            if len(part2) == 1 and part2.isdigit() and is_us_ca_system(part1): return self.findprefix(part1)
            
            part1_info = self.findprefix(part1)
            part2_info = self.findprefix(part2)
            
            if is_us_ca_system(part1): return part2_info if part2_info else part1_info
            if part1_info: return part1_info
            if part2_info: return part2_info
            return UNKNOWN_CTY_INFO

        result = self.findprefix(callsign)
        return result if result else UNKNOWN_CTY_INFO

    def get_cty_DXCC_WAE(self, callsign):
        original_wae_setting = self.wae
        self.wae = False
        dxcc_res_obj = self.get_cty(callsign)
        self.wae = True
        wae_res_obj = self.get_cty(callsign)
        self.wae = original_wae_setting
        dxcc_name_val, dxcc_pfx_val, cq_zone_val, itu_zone_val, continent_val, lat_val, lon_val, tzone_val = "Unknown", "Unknown", "Unknown", "Unknown", "Unknown", "0.0", "0.0", "0.0"
        wae_name_val, wae_pfx_val = "", ""
        primary_obj = None
        if dxcc_res_obj and dxcc_res_obj.name != "Unknown": primary_obj = dxcc_res_obj
        elif wae_res_obj and wae_res_obj.name != "Unknown" and not wae_res_obj.DXCC.startswith('*'): primary_obj = wae_res_obj
        if primary_obj: dxcc_name_val, cq_zone_val, itu_zone_val, continent_val, lat_val, lon_val, tzone_val, dxcc_pfx_val = primary_obj
        if wae_res_obj and wae_res_obj.name != "Unknown" and wae_res_obj.DXCC.startswith('*'):
            wae_name_val = wae_res_obj.name
            wae_pfx_val = wae_res_obj.DXCC
            if dxcc_name_val == "Unknown": _, cq_zone_val, itu_zone_val, continent_val, lat_val, lon_val, tzone_val, _ = wae_res_obj
        return self.FullCtyInfo(dxcc_name_val, dxcc_pfx_val, cq_zone_val, itu_zone_val, continent_val, lat_val, lon_val, tzone_val, wae_name_val, wae_pfx_val)

def _run_lookup(cty_instance, callsign_to_check):
    """Helper function to run and print a single lookup."""
    full_result = cty_instance.get_cty_DXCC_WAE(callsign_to_check)
    print(f"\n> {callsign_to_check}")
    print(f"  Comprehensive: DXCC Name: {full_result.DXCCName:<20}, DXCC Pfx: {full_result.DXCCPfx:<10}")
    print(f"                   WAE Name:  {full_result.WAEName:<20}, WAE Pfx:  {full_result.WAEPfx:<10}")
    print(f"                   Zones: CQ {full_result.CQZone}, ITU {full_result.ITUZone}, Cont: {full_result.Continent}")

if __name__ == "__main__":
    raw_path = os.environ.get('CTY_DAT_PATH')
    if not raw_path:
        print("Environment variable CTY_DAT_PATH not set.")
        sys.exit(1)
    
    cty_dat_file_path = raw_path.strip().strip('"').strip("'")
    if not os.path.exists(cty_dat_file_path):
        print(f"Error: The file '{cty_dat_file_path}' could not be found.")
        sys.exit(1)

    try:
        cty_main = CtyLookup(cty_dat_path=cty_dat_file_path)
        print(f"Successfully loaded CTY.DAT from: {cty_main.filename}")
    except (FileNotFoundError, IOError) as e:
        print(f"Error initializing CtyLookup: {e}")
        sys.exit(1)

    if len(sys.argv) > 1:
        input_filename = sys.argv[1]
        if not os.path.exists(input_filename):
            print(f"Error: Input file '{input_filename}' not found.")
            sys.exit(1)
        
        print(f"\n--- Processing callsigns from file: {input_filename} ---")
        with open(input_filename, 'r') as f:
            for line in f:
                callsign = line.strip()
                if callsign:
                    _run_lookup(cty_main, callsign)
    
    else:
        print("\n--- Interactive Mode ---")
        print("Enter callsigns to lookup. Type Ctrl+D (Unix) or Ctrl+Z+Enter (Windows) to quit.")
        while True:
            try:
                callsign_input = input("\nEnter callsign: ").strip()
                if not callsign_input:
                    continue
                _run_lookup(cty_main, callsign_input)
            except EOFError:
                print("\nExiting.")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
