# Contest Log Analyzer/contest_tools/core_annotations/get_cty.py
#
# Purpose: Provides the CtyLookup class for determining DXCC/WAE entities,
#          zones, and other geographical data from amateur radio callsigns
#          based on the CTY.DAT file.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-26
# Version: 0.16.0-Beta
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

## [0.16.0-Beta] - 2025-07-26
### Fixed
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

    _US_CANADA_PRIMARY_PREFIXES = [
        'K', 'VE', 'KL7', 'KP2', 'KP4', 'KH0', 'KH2', 'KH6', 'CY0', 'CY9',
        'VO1', 'VO2', 'VY1', 'VY2', 'KP1', 'KP3', 'KP5', 'KC6'
    ]

    def __init__(self, cty_dat_path: str, wae: bool = True):
        """
        Initializes the CtyLookup object by parsing the CTY.DAT file.
        :param cty_dat_path: Path to the CTY.DAT file.
        :param wae: Boolean, if True, includes WAE-specific prefixes for lookup.
        """
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

        lines = lines_content.split(';')

        for l in lines:
            line = l.strip()
            if not line:
                continue

            # Split by colon first to preserve spaces in names
            fields = [field.strip() for field in line.split(':')]
            
            cty_entity_info = None
            primary_dxcc_code = ""
            aliases_field_index = -1

            if len(fields) >= 8: # Standard cty.dat format
                cty_entity_info = self.CtyInfo(*fields[0:8])
                primary_dxcc_code = fields[7]
                aliases_field_index = 8
            elif len(fields) >= 3: # Simplified format (e.g., cqww.cty)
                name = fields[0]
                cq_zone = fields[1]
                primary_dxcc_code = fields[2]
                cty_entity_info = self.CtyInfo(name, cq_zone, "0", "Unknown", "0.0", "0.0", "0.0", primary_dxcc_code)
                aliases_field_index = 3

            if not cty_entity_info:
                continue

            is_wae_entity = primary_dxcc_code.startswith('*')
            primary_prefix_key_str = primary_dxcc_code[1:] if is_wae_entity else primary_dxcc_code
            target_dict = self.waeprefixes if is_wae_entity else self.dxccprefixes

            if primary_prefix_key_str == "KG4":
                self.KG4 = cty_entity_info
            else:
                target_dict[primary_prefix_key_str] = cty_entity_info

            if len(fields) > aliases_field_index:
                raw_aliases_string = fields[aliases_field_index]
                aliases = raw_aliases_string.split(",")

                for alias_entry in aliases:
                    alias_entry = alias_entry.strip()
                    if not alias_entry:
                        continue

                    is_exact_match_alias = alias_entry.startswith('=')
                    parsed_alias_entry = alias_entry[1:] if is_exact_match_alias else alias_entry
                    base_prefix_match = re.match(r'([A-Z0-9\-\/]+)', parsed_alias_entry)
                    if not base_prefix_match:
                        continue
                    base_pfx_for_alias = base_prefix_match.group(1)
                    
                    current_alias_info_list = list(cty_entity_info)

                    cq_zone_match = re.search(r'\((\d+)\)', parsed_alias_entry)
                    if cq_zone_match:
                        current_alias_info_list[1] = cq_zone_match.group(1)

                    itu_zone_match = re.search(r'\[(\d+)\]', parsed_alias_entry)
                    if itu_zone_match:
                        current_alias_info_list[2] = itu_zone_match.group(1)

                    continent_match = re.search(r'\{([A-Z]{2})\}', parsed_alias_entry)
                    if continent_match:
                        current_alias_info_list[3] = continent_match.group(1)

                    final_alias_cty_info = self.CtyInfo(*current_alias_info_list)

                    if is_exact_match_alias:
                        target_dict["=" + base_pfx_for_alias] = final_alias_cty_info
                    else:
                        target_dict[base_pfx_for_alias] = final_alias_cty_info

    def findprefix(self, callsign_segment):
        temp = callsign_segment
        while len(temp) > 0:
            if self.wae and temp in self.waeprefixes:
                return self.waeprefixes[temp]
            elif temp in self.dxccprefixes:
                return self.dxccprefixes[temp]
            temp = temp[:-1]
        return None

    def is_valid_prefix(self, segment):
        return (self.wae and segment in self.waeprefixes) or (segment in self.dxccprefixes)

    def get_cty(self, csign):
        UNKNOWN_CTY_INFO = self.CtyInfo("Unknown", "Unknown", "Unknown", "Unknown", "0.0", "0.0", "0.0", "Unknown")
        callsign = csign.upper().strip().partition('-')[0]
        
        portable_suffixes = ["/P", "/B", "/M", "/QRP"]
        for suffix in portable_suffixes:
            if callsign.endswith(suffix):
                callsign = callsign[:-len(suffix)]
                break

        if "=" + callsign in self.dxccprefixes:
            return self.dxccprefixes["=" + callsign]
        if self.wae and "=" + callsign in self.waeprefixes:
            return self.waeprefixes["=" + callsign]

        if callsign.endswith("/MM"):
            return UNKNOWN_CTY_INFO

        if callsign.startswith("KG4"):
            if len(callsign) == 5 and re.match(r"KG4[A-Z]{2}$", callsign):
                if self.KG4:
                    return self.KG4
            usa_info = self.dxccprefixes.get("K")
            return usa_info if usa_info else UNKNOWN_CTY_INFO

        parts = callsign.split('/')
        if len(parts) > 1:
            part1, part2 = parts[0], parts[-1]

            if len(part2) == 1 and part2.isdigit():
                us_call_pattern = re.compile(r'^(K|W|N|A[A-L])')
                if us_call_pattern.match(part1):
                    return self.findprefix('K')

                last_digit_match = re.search(r'\d(?=[^\d]*$)', part1)
                if last_digit_match:
                    digit_index = last_digit_match.start()
                    part_before_digit = part1[:digit_index]
                    part_after_digit = part1[digit_index + 1:]
                    cond1_followed_by_letter = re.search(r'[A-Z]', part_after_digit)
                    cond2_preceded_by_letter = re.search(r'[A-Z]', part_before_digit)
                    if cond1_followed_by_letter and cond2_preceded_by_letter:
                        new_call = part_before_digit + part2 + part_after_digit
                        special_lookup_result = self.findprefix(new_call)
                        if special_lookup_result and special_lookup_result.name != "Unknown":
                            return special_lookup_result
            
            p1_valid = self.is_valid_prefix(part1)
            p2_valid = self.is_valid_prefix(part2)
            
            if p1_valid and p2_valid: return UNKNOWN_CTY_INFO
            elif p1_valid: return self.findprefix(part1)
            elif p2_valid: return self.findprefix(part2)
            else:
                part1_info = self.findprefix(part1)

                if part1_info and part1_info.DXCC not in ('K', 'VE'):
                    return part1_info

                part2_info = self.findprefix(part2)
                if part2_info and part2_info.DXCC in self._US_CANADA_PRIMARY_PREFIXES:
                    return part2_info
                
                return part1_info if part1_info else UNKNOWN_CTY_INFO

        result = self.findprefix(callsign)
        return result if result else UNKNOWN_CTY_INFO

    def get_cty_DXCC_WAE(self, callsign):
        original_wae_setting = self.wae
        self.wae = False
        dxcc_res_obj = self.get_cty(callsign)
        self.wae = True
        wae_res_obj = self.get_cty(callsign)
        self.wae = original_wae_setting

        dxcc_name_val, dxcc_pfx_val, cq_zone_val, itu_zone_val, continent_val, lat_val, lon_val, tzone_val = \
            "Unknown", "Unknown", "Unknown", "Unknown", "Unknown", "0.0", "0.0", "0.0"
        wae_name_val, wae_pfx_val = "", ""

        primary_obj = None
        if dxcc_res_obj and dxcc_res_obj.name != "Unknown":
            primary_obj = dxcc_res_obj
        elif wae_res_obj and wae_res_obj.name != "Unknown" and not wae_res_obj.DXCC.startswith('*'):
            primary_obj = wae_res_obj

        if primary_obj:
            dxcc_name_val, cq_zone_val, itu_zone_val, continent_val, lat_val, lon_val, tzone_val, dxcc_pfx_val = primary_obj

        if wae_res_obj and wae_res_obj.name != "Unknown" and wae_res_obj.DXCC.startswith('*'):
            wae_name_val = wae_res_obj.name
            wae_pfx_val = wae_res_obj.DXCC
            if dxcc_name_val == "Unknown":
                _, cq_zone_val, itu_zone_val, continent_val, lat_val, lon_val, tzone_val, _ = wae_res_obj

        return self.FullCtyInfo(dxcc_name_val, dxcc_pfx_val, cq_zone_val, itu_zone_val, continent_val, lat_val, lon_val, tzone_val, wae_name_val, wae_pfx_val)

if __name__ == "__main__":
    raw_path = os.environ.get('CTY_DAT_PATH')
    if not raw_path:
        print("Environment variable CTY_DAT_PATH not set.")
        try:
            raw_path = input("Please enter the full path to your cty.dat file: ").strip()
        except EOFError:
            print("\nNo input provided. Exiting.")
            sys.exit(1)

    cty_dat_file_path = raw_path.strip().strip('"').strip("'")

    if not cty_dat_file_path or not os.path.exists(cty_dat_file_path):
        print(f"Error: The file '{cty_dat_file_path}' could not be found.")
        sys.exit(1)

    try:
        cty_main = CtyLookup(cty_dat_path=cty_dat_file_path)
        print(f"Successfully loaded CTY.DAT from: {cty_main.filename}")
    except (FileNotFoundError, IOError) as e:
        print(f"Error initializing CtyLookup: {e}")
        sys.exit(1)

    print("\n--- Interactive Mode ---")
    print("Enter callsigns to lookup. Type Ctrl+D (Unix) or Ctrl+Z+Enter (Windows) to quit.")

    while True:
        try:
            callsign_input = input("\nEnter callsign: ").strip()
            if not callsign_input:
                continue

            full_result = cty_main.get_cty_DXCC_WAE(callsign_input)
            print(f"  > Comprehensive: DXCC Name: {full_result.DXCCName:<20}, DXCC Pfx: {full_result.DXCCPfx:<10}")
            print(f"                   WAE Name:  {full_result.WAEName:<20}, WAE Pfx:  {full_result.WAEPfx:<10}")
            print(f"                   Zones: CQ {full_result.CQZone}, ITU {full_result.ITUZone}, Cont: {full_result.Continent}")

        except EOFError:
            print("\nExiting.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
