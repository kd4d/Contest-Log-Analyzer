# Contest Log Analyzer/contest_tools/contest_specific_annotations/arrl_dx_multiplier_resolver.py
#
# Purpose: Provides contest-specific logic to resolve ARRL DX Contest multipliers
#          (States/Provinces) from callsigns or explicit exchange fields.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-21
# Version: 0.30.42-Beta
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
## [0.30.42-Beta] - 2025-08-21
### Changed
# - Refactored the resolver to be stateful, tracking multipliers per band.
### Added
# - Added logic to generate new `STPROV_IsNewMult` and `DXCC_IsNewMult`
#   columns to flag the first time a multiplier is worked.
## [0.30.41-Beta] - 2025-08-15
### Changed
# - Refactored logic to calculate and populate two new, dedicated columns
#   (`Mult_STPROV` and `Mult_DXCC`) based on the worked station's location,
#   resolving the upstream data issue for the score report.
## [0.30.40-Beta] - 2025-08-06
### Fixed
# - Updated all references to the old CONTEST_DATA_DIR environment variable
#   to use the correct CONTEST_LOGS_REPORTS variable.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
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
        
        temp = value_upper
        while len(temp) > 0:
            if temp in self._lookup:
                return self._lookup[temp][0]
            temp = temp[:-1]

        return "Unknown"

def resolve_multipliers(df: pd.DataFrame, my_location_type: str) -> pd.DataFrame:
    """
    Resolves multipliers and adds IsNewMult flags by creating four new columns:
    `Mult_STPROV`, `Mult_DXCC`, `STPROV_IsNewMult`, and `DXCC_IsNewMult`.
    """
    if df.empty:
        return df

    root_dir = os.environ.get('CONTEST_LOGS_REPORTS').strip().strip('"').strip("'")
    data_dir = os.path.join(root_dir, 'data')
    alias_lookup = AliasLookup(data_dir)

    # Initialize new columns
    df['Mult_STPROV'] = pd.NA
    df['Mult_DXCC'] = pd.NA
    df['STPROV_IsNewMult'] = 0
    df['DXCC_IsNewMult'] = 0
    
    # Keep track of seen mults per band
    seen_stprov_per_band = {}
    seen_dxcc_per_band = {}

    # Process QSOs chronologically to correctly identify the "first" multiplier
    df_sorted = df.sort_values(by='Datetime')

    for idx, row in df_sorted.iterrows():
        band = row.get('Band')
        if not band:
            continue
        
        # Initialize sets for new bands as they are encountered
        if band not in seen_stprov_per_band:
            seen_stprov_per_band[band] = set()
        if band not in seen_dxcc_per_band:
            seen_dxcc_per_band[band] = set()
            
        # --- Determine the multiplier value for the current QSO ---
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
            
        # --- New Stateful Logic: Check if multiplier is new and set flag ---
        if pd.notna(stprov_mult):
            df.loc[idx, 'Mult_STPROV'] = stprov_mult
            if stprov_mult not in seen_stprov_per_band[band]:
                df.loc[idx, 'STPROV_IsNewMult'] = 1
                seen_stprov_per_band[band].add(stprov_mult)

        if pd.notna(dxcc_mult):
            df.loc[idx, 'Mult_DXCC'] = dxcc_mult
            if dxcc_mult not in seen_dxcc_per_band[band]:
                df.loc[idx, 'DXCC_IsNewMult'] = 1
                seen_dxcc_per_band[band].add(dxcc_mult)
    
    # Clean up old column if it exists to avoid downstream confusion
    if 'FinalMultiplier' in df.columns:
        df.drop(columns=['FinalMultiplier'], inplace=True)
        
    return df