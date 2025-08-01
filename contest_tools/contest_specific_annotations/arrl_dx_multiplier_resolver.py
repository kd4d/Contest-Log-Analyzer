# Contest Log Analyzer/contest_tools/contest_specific_annotations/arrl_dx_multiplier_resolver.py
#
# Purpose: Provides contest-specific logic to resolve ARRL DX Contest multipliers
#          (States/Provinces) from callsigns or explicit exchange fields.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-01
# Version: 0.23.0-Beta
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

## [0.23.0-Beta] - 2025-08-01
### Added
# - Initial release of the ARRL DX multiplier resolver module.

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
                        # Handle cases with no aliases
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
        If the value is already a valid multiplier, it's returned directly.
        """
        if not isinstance(value, str):
            return "Unknown"
            
        value_upper = value.upper()
        if value_upper in self._valid_mults:
            return value_upper
        
        # Check prefixes for callsigns
        temp = value_upper
        while len(temp) > 0:
            if temp in self._lookup:
                return self._lookup[temp][0]
            temp = temp[:-1]

        return "Unknown"

def resolve_multipliers(df: pd.DataFrame, my_location_type: str) -> pd.DataFrame:
    """
    Resolves the final State/Province multiplier for ARRL DX Contest QSOs.
    """
    if df.empty:
        return df

    data_dir = os.environ.get('CONTEST_DATA_DIR').strip().strip('"').strip("'")
    alias_lookup = AliasLookup(data_dir)
    
    # Determine which column holds the multiplier info based on logger's location
    if my_location_type == "W/VE":
        # I am a W/VE, so the multiplier is the DXCC of the station I worked.
        # This is already handled by the core annotations. No action needed here.
        df['FinalMultiplier'] = df['DXCCPfx']
        return df
    
    elif my_location_type == "DX":
        # I am DX, so the multiplier is the State/Prov of the W/VE station I worked.
        # This comes from the received exchange ('RcvdLocation').
        # However, we must also check the callsign for an alias if the location is invalid.
        
        def determine_mult(row):
            location = row.get('RcvdLocation', '')
            # Try the location from the exchange first
            mult = alias_lookup.get_multiplier(location)
            
            # If the exchange didn't yield a valid mult, try the callsign
            if mult == "Unknown":
                return alias_lookup.get_multiplier(row.get('Call', ''))
            return mult

        df['FinalMultiplier'] = df.apply(determine_mult, axis=1)
        return df

    return df