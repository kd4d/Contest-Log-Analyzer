# Contest Log Analyzer/contest_tools/contest_specific_annotations/arrl_ss_multiplier_resolver.py
#
# Purpose: Provides contest-specific logic to resolve ARRL Sweepstakes multipliers
#          (Sections) from the explicit exchange field.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-01
# Version: 0.24.5-Beta
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

## [0.24.5-Beta] - 2025-08-01
### Removed
# - Removed temporary diagnostic print statements.

## [0.24.4-Beta] - 2025-08-01
### Added
# - Added temporary diagnostic print statements to debug section file parsing.

## [0.24.3-Beta] - 2025-08-01
### Fixed
# - Corrected the regular expression used to parse the SweepstakesSections.dat
#   file, which was preventing any sections from being loaded.

## [0.24.0-Beta] - 2025-08-01
### Added
# - Initial release of the ARRL Sweepstakes multiplier resolver module.

import pandas as pd
import os
import re
from typing import Dict, Tuple, Optional

class SectionAliasLookup:
    """Parses and provides lookups for the SweepstakesSections.dat file."""
    
    def __init__(self, data_dir_path: str):
        self.filepath = os.path.join(data_dir_path, 'SweepstakesSections.dat')
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
                    
                    match = re.match(r'([A-Z]{2,3})\s+\((.*)\)', official_part.strip())
                    if not match:
                        continue
                    
                    official_abbr = match.group(1).upper()
                    full_name = match.group(2)
                    
                    self._valid_mults.add(official_abbr)
                    for alias in aliases:
                        self._lookup[alias] = (official_abbr, full_name)
        except FileNotFoundError:
            print(f"Warning: Section alias file not found at {self.filepath}. Alias lookup will be disabled.")
        except Exception as e:
            print(f"Error reading section alias file {self.filepath}: {e}")

    def get_section(self, value: str) -> str:
        """
        Looks up an alias and returns the official section abbreviation.
        If the value is already a valid section, it's returned directly.
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
    Resolves the final Section multiplier for ARRL Sweepstakes QSOs.
    The multiplier is always taken from the received exchange.
    """
    if df.empty or 'RcvdSection' not in df.columns:
        df['FinalMultiplier'] = "Unknown"
        return df

    data_dir = os.environ.get('CONTEST_DATA_DIR').strip().strip('"').strip("'")
    alias_lookup = SectionAliasLookup(data_dir)
    
    df['FinalMultiplier'] = df['RcvdSection'].apply(alias_lookup.get_section)
    return df
