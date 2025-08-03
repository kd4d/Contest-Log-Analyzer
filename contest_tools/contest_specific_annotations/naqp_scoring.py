# Contest Log Analyzer/contest_tools/contest_specific_annotations/naqp_multiplier_resolver.py
#
# Purpose: Provides contest-specific logic to resolve NAQP multipliers
#          (States/Provinces/NA DXCC) from the log exchange.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-03
# Version: 0.29.0-Beta
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
## [0.29.0-Beta] - 2025-08-03
### Added
# - Initial release of the NAQP multiplier resolver module.

import pandas as pd
import os
import re
from typing import Dict, Tuple, Optional

# TODO: This class is duplicated in other resolver modules. It should be
# refactored into a shared utility in a future update.
class NAQPMultiplierLookup:
    """Parses and provides lookups for the NAQPmults.dat file."""
    
    def __init__(self, data_dir_path: str):
        self.filepath = os.path.join(data_dir_path, 'NAQPmults.dat')
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
            return "Unknown"
            
        value_upper = value.upper()
        if value_upper in self._valid_mults:
            return value_upper
        
        if value_upper in self._lookup:
            return self._lookup[value_upper][0]

        return "Unknown"

def resolve_multipliers(df: pd.DataFrame, my_location_type: Optional[str]) -> pd.DataFrame:
    """
    Resolves the final multiplier for NAQP contest QSOs.
    
    The logic is tiered:
    1. Check if the received location is a valid US/Canada multiplier via the alias file.
    2. If not, check if the QSO partner is in North America.
    3. If they are, their DXCC prefix is the multiplier.
    4. Otherwise, it is not a multiplier.
    """
    if df.empty or 'RcvdLocation' not in df.columns:
        df['FinalMultiplier'] = "Unknown"
        return df

    data_dir = os.environ.get('CONTEST_DATA_DIR').strip().strip('"').strip("'")
    alias_lookup = NAQPMultiplierLookup(data_dir)
    
    def determine_mult(row):
        # First, try to resolve a US State or Canadian Province from the exchange
        location = row.get('RcvdLocation', '')
        mult = alias_lookup.get_multiplier(location)
        
        # If it's a valid US/Canada multiplier, we're done
        if mult != "Unknown":
            return mult
        
        # If not, check if it's another North American DXCC entity
        continent = row.get('Continent')
        if continent == 'NA':
            return row.get('DXCCPfx', 'Unknown')
            
        # If it's not a US/Canada mult and not another NA mult, it's not a multiplier
        return "Unknown"

    df['FinalMultiplier'] = df.apply(determine_mult, axis=1)
    return df