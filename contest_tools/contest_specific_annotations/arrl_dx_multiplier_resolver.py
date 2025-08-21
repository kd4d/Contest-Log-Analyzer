# Contest Log Analyzer/contest_tools/contest_specific_annotations/arrl_dx_multiplier_resolver.py
#
# Purpose: Provides contest-specific logic to resolve ARRL DX Contest multipliers
#          (States/Provinces) from callsigns or explicit exchange fields.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-21
# Version: 0.30.43-Beta
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
## [0.30.43-Beta] - 2025-08-21
### Changed
# - Completely refactored the resolver to correctly implement the
#   asymmetric ARRL DX multiplier rules based on logger location.
### Fixed
# - Implemented "exchange-first" logic, where the received State/Province
#   overrides the callsign's DXCC entity.
# - Correctly excludes non-contiguous states (AK, HI) as multipliers
#   for DX stations, per official contest rules.
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
        
        if value_upper in self._lookup:
            return self._lookup[value_upper][0]

        return "Unknown"

def resolve_multipliers(df: pd.DataFrame, my_location_type: str) -> pd.DataFrame:
    """
    Resolves multipliers for ARRL DX based on the logger's location, prioritizing
    the received exchange over the callsign's prefix.
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
    seen_stprov_per_band = {band: set() for band in df['Band'].unique() if pd.notna(band)}
    seen_dxcc_per_band = {band: set() for band in df['Band'].unique() if pd.notna(band)}
    
    NON_CONTIGUOUS_STATES = {'AK', 'HI'}

    # Process QSOs chronologically to correctly identify the "first" multiplier
    df_sorted = df.sort_values(by='Datetime')

    for idx, row in df_sorted.iterrows():
        band = row.get('Band')
        if not band: continue
            
        # --- Algorithm Step 1: Prioritize the received exchange field ---
        rcvd_location = row.get('RcvdLocation', '')
        resolved_stprov = alias_lookup.get_multiplier(rcvd_location)
        is_valid_stprov = resolved_stprov != "Unknown"
        
        # --- Algorithm Step 2: Apply rules based on LOGGER's location ---
        if my_location_type == 'DX':
            # DX loggers only care about STPROV multipliers from the contiguous 48 + DC + VE.
            if is_valid_stprov and resolved_stprov not in NON_CONTIGUOUS_STATES:
                df.loc[idx, 'Mult_STPROV'] = resolved_stprov
                if resolved_stprov not in seen_stprov_per_band[band]:
                    df.loc[idx, 'STPROV_IsNewMult'] = 1
                    seen_stprov_per_band[band].add(resolved_stprov)
        
        elif my_location_type == 'W/VE':
            # W/VE loggers only care about DXCC multipliers.
            if is_valid_stprov:
                # If a valid ST/PROV was sent, it's a W/VE contact and not a multiplier.
                # The exception for portable DX calls is handled here.
                pass
            else:
                # The exchange was not a valid ST/PROV, so now we check the callsign's
                # DXCC entity to see if it's a DXCC multiplier.
                worked_dxcc_name = row.get('DXCCName', 'Unknown')
                
                # A multiplier is any DXCC entity that is NOT the contiguous US or Canada.
                # This correctly includes AK, HI, KP4, etc., as well as all other DX.
                if worked_dxcc_name not in ["United States", "Canada"]:
                    dxcc_mult = row.get('DXCCPfx')
                    df.loc[idx, 'Mult_DXCC'] = dxcc_mult
                    if pd.notna(dxcc_mult) and dxcc_mult not in seen_dxcc_per_band[band]:
                        df.loc[idx, 'DXCC_IsNewMult'] = 1
                        seen_dxcc_per_band[band].add(dxcc_mult)
    
    return df