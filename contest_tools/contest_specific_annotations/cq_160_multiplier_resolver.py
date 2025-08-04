# Contest Log Analyzer/contest_tools/contest_specific_annotations/cq_160_multiplier_resolver.py
#
# Purpose: Provides contest-specific logic to resolve CQ 160 multipliers
#          (States/Provinces/DXCC) from the log exchange and CTY data.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-04
# Version: 0.29.3-Beta
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
## [0.29.3-Beta] - 2025-08-04
### Fixed
# - The resolver now correctly checks for and uses WAE prefixes for DXCC
#   multipliers, per the official CQ 160 contest rules.
## [0.29.2-Beta] - 2025-08-04
### Changed
# - Reworked the resolver to be the single source of truth for multipliers.
# - The resolver now outputs two distinct, clean columns (STPROV_Mult, DXCC_Mult)
#   to permanently fix all double-counting and mis-categorization bugs.
import pandas as pd
import os
import re
from typing import Dict, Tuple, Optional

# TODO: This class is a candidate for refactoring into a shared utility
# in a future update to avoid code duplication.
class CQ160MultiplierLookup:
    """Parses and provides lookups for the CQ160mults.dat file."""
    
    def __init__(self, data_dir_path: str):
        self.filepath = os.path.join(data_dir_path, 'CQ160mults.dat')
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
                    
                    match = re.match(r'([A-Z0-9]{1,3})\s+\((.*)\)', official_part.strip())
                    if not match:
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
        Looks up an alias and returns the official multiplier abbreviation.
        If the value is already a valid multiplier, it's returned directly.
        """
        if not isinstance(value, str):
            return pd.NA
            
        value_upper = value.upper()
        if value_upper in self._valid_mults:
            return value_upper
        
        if value_upper in self._lookup:
            return self._lookup[value_upper][0]

        return pd.NA

def resolve_multipliers(df: pd.DataFrame, my_location_type: Optional[str]) -> pd.DataFrame:
    """
    Resolves multipliers for CQ 160, creating two separate columns for the two
    distinct multiplier types to prevent double-counting.
    """
    if df.empty:
        df['STPROV_Mult'] = pd.NA
        df['DXCC_Mult'] = pd.NA
        return df

    data_dir = os.environ.get('CONTEST_DATA_DIR').strip().strip('"').strip("'")
    alias_lookup = CQ160MultiplierLookup(data_dir)
    
    stprov_mults = []
    dxcc_mults = []

    for index, row in df.iterrows():
        stprov_val = pd.NA
        dxcc_val = pd.NA

        # Logic for all stations: check for State/Province multiplier first.
        location = row.get('RcvdLocation', '')
        st_prov_mult = alias_lookup.get_multiplier(location)
        
        if pd.notna(st_prov_mult):
            stprov_val = st_prov_mult
        else:
            # If it's not a State/Province, it might be a DXCC multiplier.
            # This is only valid for W/VE stations.
            if my_location_type == "W/VE":
                worked_entity = row.get('DXCCName', '')
                if worked_entity not in ["United States", "Canada"]:
                    # Per CQ rules, check for a WAE prefix first, then fall back to DXCC.
                    wae_pfx = row.get('WAEPfx')
                    if pd.notna(wae_pfx) and wae_pfx != '':
                         dxcc_val = wae_pfx
                    else:
                         dxcc_val = row.get('DXCCPfx', pd.NA)

        stprov_mults.append(stprov_val)
        dxcc_mults.append(dxcc_val)

    df['STPROV_Mult'] = stprov_mults
    df['DXCC_Mult'] = dxcc_mults
    
    return df