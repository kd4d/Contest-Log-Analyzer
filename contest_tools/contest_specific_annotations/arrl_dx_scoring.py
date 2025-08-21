# Contest Log Analyzer/contest_tools/contest_specific_annotations/arrl_dx_scoring.py
#
# Purpose: Provides contest-specific scoring logic for the ARRL DX contest.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-21
# Version: 0.31.0-Beta
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
## [0.31.0-Beta] - 2025-08-21
### Changed
# - Reworked scoring logic to be "exchange-first", prioritizing the
#   received State/Province over the callsign's DXCC entity to align
#   with the multiplier resolver's logic.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
# - Standardized all project files to a common baseline version.
import pandas as pd
import os
import re
from typing import Dict, Any, Tuple

class AliasLookup:
    """Parses and provides lookups for the ARRLDXmults.dat file."""
    
    def __init__(self, data_dir_path: str):
        self.filepath = os.path.join(data_dir_path, 'ARRLDXmults.dat')
        self._lookup: Dict[str, Tuple[str, str]] = {}
        self._valid_mults: set = set()
        self._parse_file()

    def _parse_file(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split(':')
                    if len(parts) != 2:
                        continue

                    aliases_part, official_part = parts[0], parts[1]
                    aliases = [alias.strip().upper() for alias in aliases_part.split(',')]
                    
                    match = re.match(r'([A-Z]{2})\s+\((.*)\)', official_part.strip())
                    if not match:
                        match_no_alias = re.match(r'([A-Z]{2})\s+\((.*)\)', aliases_part.strip())
                        if match_no_alias:
                            official_abbr = match_no_alias.group(1).upper()
                            self._valid_mults.add(official_abbr)
                        continue
                    
                    official_abbr = match.group(1).upper()
                    full_name = match.group(2)
                    
                    self._valid_mults.add(official_abbr)
                    for alias in aliases:
                        self._lookup[alias] = (official_abbr, full_name)
        except FileNotFoundError:
            print(f"Warning: Multiplier alias file not found at {self.filepath}. Alias lookup will be disabled.")
        except Exception as e:
            print(f"Error reading multiplier alias file {self.filepath}: {e}")

    def get_multiplier(self, value: str) -> str:
        """
        Looks up an alias and returns the official 2-letter multiplier.
        """
        if not isinstance(value, str):
            return "Unknown"
            
        value_upper = value.upper()
        if value_upper in self._valid_mults:
            return value_upper
        
        if value_upper in self._lookup:
            return self._lookup[value_upper][0]

        return "Unknown"

def _calculate_single_qso_points(row: pd.Series, my_location_type: str, alias_lookup: AliasLookup) -> int:
    """
    Calculates the point value for a single QSO based on ARRL DX rules,
    prioritizing the received exchange over the callsign's DXCC entity.
    """
    if row['Dupe']:
        return 0

    worked_location_type = "DX" # Default assumption
    
    # --- Exchange-First Logic ---
    # First, check if the received exchange is a valid W/VE multiplier.
    rcvd_location = row.get('RcvdLocation', '')
    resolved_stprov = alias_lookup.get_multiplier(rcvd_location)
    
    if resolved_stprov != "Unknown":
        # If the exchange is a valid ST/PROV, the station is treated as W/VE for scoring.
        worked_location_type = "W/VE"
    else:
        # If the exchange is not a valid ST/PROV, fall back to the callsign's DXCC.
        worked_entity_name = row.get('DXCCName', 'Unknown')
        worked_location_type = "W/VE" if worked_entity_name in ["United States", "Canada"] else "DX"

    # --- Scoring Rules ---
    # W/VE stations can only work DX stations for points.
    if my_location_type == "W/VE":
        return 3 if worked_location_type == "DX" else 0
        
    # DX stations can only work W/VE stations for points.
    elif my_location_type == "DX":
        return 3 if worked_location_type == "W/VE" else 0
    
    return 0

def calculate_points(df: pd.DataFrame, my_call_info: Dict[str, Any]) -> pd.Series:
    """
    Calculates QSO points for an entire DataFrame based on ARRL DX rules.

    Args:
        df (pd.DataFrame): The DataFrame of QSOs to be scored.
        my_call_info (Dict[str, Any]): A dictionary containing the logger's
                                       own location info ('DXCCName').
    Returns:
        pd.Series: A Pandas Series containing the calculated points for each QSO.
    """
    my_entity_name = my_call_info.get('DXCCName')
    if not my_entity_name:
        raise ValueError("Logger's own DXCC Name must be provided for scoring.")

    my_location_type = "W/VE" if my_entity_name in ["United States", "Canada"] else "DX"

    # Initialize the alias lookup utility
    root_dir = os.environ.get('CONTEST_LOGS_REPORTS').strip().strip('"').strip("'")
    data_dir = os.path.join(root_dir, 'data')
    alias_lookup = AliasLookup(data_dir)

    # Apply the scoring logic to each row of the DataFrame.
    return df.apply(
        _calculate_single_qso_points, 
        axis=1, 
        my_location_type=my_location_type,
        alias_lookup=alias_lookup
    )