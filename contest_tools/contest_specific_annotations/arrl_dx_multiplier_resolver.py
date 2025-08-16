# Contest Log Analyzer/contest_tools/contest_specific_annotations/arrl_dx_multiplier_resolver.py
#
# Purpose: Provides contest-specific logic to resolve ARRL DX Contest multipliers
#          [cite_start](States/Provinces) from callsigns or explicit exchange fields. [cite: 263-264]
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-15
# Version: 0.30.41-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# [cite_start]License, v. 2.0. [cite: 264-265] If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# --- Revision History ---
## [0.30.41-Beta] - 2025-08-15
### Changed
# - Refactored logic to calculate and populate two new, dedicated columns
#   (`Mult_STPROV` and `Mult_DXCC`) based on the worked station's location,
#   resolving the upstream data issue for the score report.
## [0.30.40-Beta] - 2025-08-06
### Fixed
# - Updated all references to the old CONTEST_DATA_DIR environment variable
#   [cite_start]to use the correct CONTEST_LOGS_REPORTS variable. [cite: 266-267]
## [0.30.0-Beta] - 2025-08-05
# [cite_start]- Initial release of Version 0.30.0-Beta. [cite: 267]
import pandas as pd
import os
import re
from typing import Dict, Tuple

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
            print(f"Warning: Multiplier alias file not found at {self.filepath}. [cite_start]Alias lookup will be disabled.") [cite: 275-276]
        except Exception as e:
            print(f"Error reading multiplier alias file {self.filepath}: {e}")

    def get_multiplier(self, value: str) -> str:
        """
        [cite_start]Looks up an alias and returns the official 2-letter multiplier. [cite: 276-277]
        """
        if not isinstance(value, str):
            return "Unknown"
            
        value_upper = value.upper()
        if value_upper in self._valid_mults:
            return value_upper
        
        temp = value_upper
        while len(temp) > 0:
            if temp in self._lookup:
                return self._lookup[temp][0]
            temp = temp[:-1]

        return "Unknown"

def resolve_multipliers(df: pd.DataFrame, my_location_type: str) -> pd.DataFrame:
    """
    Resolves multipliers by creating two new columns, `Mult_STPROV` and
    `Mult_DXCC`, based on the location of the station worked in each QSO.
    """
    if df.empty:
        return df

    root_dir = os.environ.get('CONTEST_LOGS_REPORTS').strip().strip('"').strip("'")
    data_dir = os.path.join(root_dir, 'data')
    alias_lookup = AliasLookup(data_dir)

    def _get_multipliers_for_row(row):
        stprov_mult = pd.NA
        dxcc_mult = pd.NA

        worked_dxcc_name = row.get('DXCCName', 'Unknown')
        is_wve_contact = worked_dxcc_name in ["United States", "Canada"]

        if is_wve_contact:
            location = row.get('RcvdLocation', '')
            mult = alias_lookup.get_multiplier(location)
            if mult == "Unknown":
                 mult = alias_lookup.get_multiplier(row.get('Call', ''))

            if mult != "Unknown":
                stprov_mult = mult
        else:
            dxcc_mult = row.get('DXCCPfx')

        return stprov_mult, dxcc_mult

    df[['Mult_STPROV', 'Mult_DXCC']] = df.apply(_get_multipliers_for_row, axis=1, result_type='expand')

    # Clean up old column if it exists to avoid downstream confusion
    if 'FinalMultiplier' in df.columns:
        df.drop(columns=['FinalMultiplier'], inplace=True)

    return df