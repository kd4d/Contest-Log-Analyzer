# Contest Log Analyzer/contest_tools/core_annotations/get_cty.py
#
# Purpose: Provides the CtyLookup class for determining DXCC/WAE entities,
#          zones, and other geographical data from amateur radio callsigns
#          based on the CTY.DAT file.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-06
# Version: 0.30.40-Beta
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
## [0.30.40-Beta] - 2025-08-06
### Fixed
# - Updated all references to the old CONTEST_DATA_DIR environment variable
#   to use the correct CONTEST_LOGS_REPORTS variable.
## [0.29.5-Beta] - 2025-08-04
### Changed
# - Replaced all `print` statements with calls to the new logging framework.
from typing import List, Dict, Optional, Tuple
import re
from collections import namedtuple
import sys
import os
import argparse
import logging
from Utils.logger_config import setup_logging

class CtyLookup:
    """
    A class to lookup amateur radio callsigns and determine their
    associated country (DXCC entity), CQ Zone, ITU Zone, and Continent
    based on the CTY.DAT file, following a precise, ordered algorithm.
    """

    CtyInfo = namedtuple('CtyInfo', 'name CQZone ITUZone Continent Lat Lon Tzone DXCC portableid')
    FullCtyInfo = namedtuple('FullCtyInfo', 'DXCCName DXCCPfx CQZone ITUZone Continent Lat Lon Tzone WAEName WAEPfx portableid')
    UNKNOWN_ENTITY = CtyInfo("Unknown", "Unknown", "Unknown", "Unknown", "0.0", "0.0", "0.0", "Unknown", "")

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
            return

        entity_info_base = [p.strip() for p in parts[0:8]]
        entity_info = self.CtyInfo(*entity_info_base, portableid="")
        
        primary_prefix = entity_info.DXCC
        aliases_str = parts[8] if len(parts) > 8 else ""
        
        is_wae = primary_prefix.startswith('*')
        target_dict = self.waeprefixes if is_wae else self.dxccprefixes
        
        key = primary_prefix[1:] if is_wae else primary_prefix
        target_dict[key] = entity_info

        for alias in aliases_str.split(','):
            alias = alias.strip()
            if not alias:
                continue

            is_exact = alias.startswith('=') or re.search(r'[\[({]', alias)
            
            match = re.match(r'=?([A-Z0-9\-\/]+)', alias)
            if not match:
                continue
            base_prefix = match.group(1)
            
            info_list = list(entity_info_base)
            cq_m = re.search(r'\((\d+)\)', alias)
            if cq_m: info_list[1] = cq_m.group(1)
            itu_m = re.search(r'\[(\d+)\]', alias)
            if itu_m: info_list[2] = itu_m.group(1)
            cont_m = re.search(r'\{([A-Z]{2})\}', alias)
            if cont_m: info_list[3] = cont_m.group(1)
            final_info = self.CtyInfo(*info_list, portableid="")
            
            if is_exact:
                target_dict["=" + base_prefix] = final_info
            
            if not alias.startswith('='):
                target_dict[base_prefix] = final_info

    def _validate_patterns(self):
        """Validates US/CA prefixes from the CTY file against regex patterns."""
        us_mismatches, ca_mismatches = [], []
        for pfx, info in self.dxccprefixes.items():
            if pfx.startswith(('=', 'VER')): continue
            test_call = f"{pfx}1A"
            if info.name == "United States" and not self._US_PATTERN.match(test_call):
                us_mismatches.append(pfx)
            elif info.name == "Canada" and not self._CA_PATTERN.match(test_call):
                ca_mismatches.append(pfx)
        if us_mismatches:
            logging.warning(f"US prefixes from '{self.filename}' fail pattern match: {', '.join(us_mismatches)}")
        if ca_mismatches:
            logging.warning(f"Canadian prefixes from '{self.filename}' fail pattern match: {', '.join(ca_mismatches)}")

    def get_cty_DXCC_WAE(self, callsign: str) -> FullCtyInfo:
        """
        Primary entry point. Performs two lookups and merges the results.
        """
        dxcc_res_obj = self.get_cty(callsign, wae=False)
        wae_res_obj = self.get_cty(callsign, wae=True)

        base_info = self.UNKNOWN_ENTITY._asdict()
        dxcc_name, cq, itu, cont, lat, lon, tz, dxcc_pfx = (
            base_info['name'], base_info['CQZone'], base_info['ITUZone'], base_info['Continent'],
            base_info['Lat'], base_info['Lon'], base_info['Tzone'], base_info['DXCC']
        )
        wae_name, wae_pfx, portableid = "", "", ""

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
        processed_call = self._preprocess_callsign(callsign)
        result = self._check_exact_match(processed_call, wae)
        if result: return result
        result = self._check_special_cases(processed_call)
        if result: return result
        if '/' in processed_call:
            result = self._handle_portable_call(processed_call, wae)
            if result: return result
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
        if re.fullmatch(r'KG4[A-Z]{2}', call):
            return self.dxccprefixes.get("KG4")
        if '/' in call and any(re.fullmatch(r'KG4[A-Z]{2}', part) for part in call.split('/')):
            return self.UNKNOWN_ENTITY
        return None

    def _handle_portable_call(self, call: str, wae: bool) -> Optional[CtyInfo]:
        """Implements Step 4 of the algorithm."""
        parts = call.split('/')
        p1, p2 = parts[0], parts[-1]

        if len(p1) == 1 and p1.isdigit() and len(p2) > 1 and not p2.isdigit():
            return self.UNKNOWN_ENTITY
        
        def determine_portable_id(part1, part2, chosen_part):
            if len(part2) == 1 and part2.isdigit():
                return part2
            return chosen_part

        def is_valid_prefix(p):
            if p in self.dxccprefixes: return True
            if wae and p in self.waeprefixes: return True
            return False

        p1_is_pfx, p2_is_pfx = is_valid_prefix(p1), is_valid_prefix(p2)
        if p1_is_pfx and not p2_is_pfx:
            pid = determine_portable_id(p1, p2, p1)
            return self._get_prefix_entity(p1, wae)._replace(portableid=pid)
        if p2_is_pfx and not p1_is_pfx:
            pid = determine_portable_id(p1, p2, p2)
            return self._get_prefix_entity(p2, wae)._replace(portableid=pid)

        p1s = p1[:-1] if len(p1) > 1 and p1[-1].isdigit() and not p1[-2].isdigit() else None
        p2s = p2[:-1] if len(p2) > 1 and p2[-1].isdigit() and not p2[-2].isdigit() else None
        if p1s or p2s:
            p1s_is_pfx = is_valid_prefix(p1s) if p1s else False
            p2s_is_pfx = is_valid_prefix(p2s) if p2s else False
            if p1s_is_pfx and not p2s_is_pfx:
                pid = determine_portable_id(p1, p2, p1)
                return self._get_prefix_entity(p1s, wae)._replace(portableid=pid)
            if p2s_is_pfx and not p1s_is_pfx:
                pid = determine_portable_id(p1, p2, p2)
                return self._get_prefix_entity(p2s, wae)._replace(portableid=pid)

        if len(p2) == 1 and p2.isdigit() and (self._US_PATTERN.match(p1) or self._CA_PATTERN.match(p1)):
            cty_info = self._find_longest_prefix(p1, wae)
            if cty_info:
                return cty_info._replace(portableid=p2)
            return self.UNKNOWN_ENTITY

        p1_ends_digit = p1[-1].isdigit()
        p2_ends_digit = p2[-1].isdigit()
        if p1_ends_digit and not p2_ends_digit:
            cty_info = self._find_longest_prefix(p1, wae)
            if cty_info: return cty_info._replace(portableid=p1)
        if p2_ends_digit and not p1_ends_digit:
            cty_info = self._find_longest_prefix(p2, wae)
            if cty_info: return cty_info._replace(portableid=p2)

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CTY.DAT lookup tool.")
    parser.add_argument('callsign_file', nargs='?', default=None,
                        help="Optional path to a file containing callsigns to look up, one per line.")
    args = parser.parse_args()

    setup_logging(verbose=True)

    root_dir = os.environ.get('CONTEST_LOGS_REPORTS')
    if not root_dir:
        logging.critical("CONTEST_LOGS_REPORTS environment variable not set.")
        sys.exit(1)
    
    data_dir = os.path.join(root_dir.strip().strip('"').strip("'"), 'data')
    cty_path = os.path.join(data_dir, 'cty.dat')

    if not os.path.exists(cty_path):
        logging.critical(f"The file '{cty_path}' could not be found.")
        sys.exit(1)
    try:
        cty_main = CtyLookup(cty_dat_path=cty_path)
        logging.info(f"Successfully loaded CTY file from: {cty_main.filename}")
    except (FileNotFoundError, IOError) as e:
        logging.critical(f"Error initializing CtyLookup: {e}")
        sys.exit(1)
    
    if args.callsign_file:
        infile = args.callsign_file
        if not os.path.exists(infile):
            logging.critical(f"Input file '{infile}' not found.")
            sys.exit(1)
        logging.info(f"\n--- Processing callsigns from file: {infile} ---")
        with open(infile, 'r') as f:
            for line in f:
                if call := line.strip():
                    _run_lookup(cty_main, call)
    else:
        logging.info("\n--- Interactive Mode ---\nEnter callsigns to lookup. Type Ctrl+D (Unix) or Ctrl+Z+Enter (Windows) to quit.")
        while True:
            try:
                call_in = input("\nEnter callsign: ").strip()
                if call_in:
                    _run_lookup(cty_main, call_in)
            except EOFError:
                logging.info("\nExiting.")
                break
            except Exception as e:
                logging.error(f"An error occurred: {e}")