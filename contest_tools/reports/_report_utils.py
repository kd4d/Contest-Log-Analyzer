# Contest Log Analyzer/contest_tools/reports/_report_utils.py
#
# Purpose: A utility module for helper functions and classes that are shared
#          across multiple report generator modules.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-05
# Version: 0.30.0-Beta
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
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
# - Standardized all project files to a common baseline version.
import pandas as pd
from ..contest_log import ContestLog
from typing import List, Dict, Tuple, Set, Optional
import os
import re

class AliasLookup:
    """
    Parses a standard multiplier alias file (e.g., NAQPmults.dat, SweepstakesSections.dat)
    and provides a lookup method to resolve aliases to their official abbreviation and full name.
    This class is intended for use by report generators.
    """
    _instances: Dict[str, 'AliasLookup'] = {}

    def __new__(cls, alias_filename: str):
        if alias_filename not in cls._instances:
            instance = super(AliasLookup, cls).__new__(cls)
            instance._initialized = False
            cls._instances[alias_filename] = instance
        return cls._instances[alias_filename]

    def __init__(self, alias_filename: str):
        if self._initialized:
            return
            
        data_dir = os.environ.get('CONTEST_DATA_DIR', '').strip().strip('"').strip("'")
        self.filepath = os.path.join(data_dir, alias_filename)
        self._lookup: Dict[str, Tuple[str, str]] = {}
        self._valid_mults: Set[str] = set()
        self._parse_file()
        self._initialized = True

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
                    
                    match = re.match(r'([A-Z0-9]{1,4})\s+\((.*)\)', official_part.strip())
                    if not match:
                        continue
                    
                    official_abbr = match.group(1).upper()
                    full_name = match.group(2)
                    
                    self._valid_mults.add(official_abbr)
                    self._lookup[official_abbr] = (official_abbr, full_name) # Map official to itself
                    for alias in aliases:
                        self._lookup[alias] = (official_abbr, full_name)
        except FileNotFoundError:
            print(f"Warning: Multiplier alias file not found at {self.filepath}.")
        except Exception as e:
            print(f"Error reading multiplier alias file {self.filepath}: {e}")

    def get_multiplier_info(self, value: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Looks up a multiplier value (alias or official) and returns the
        official abbreviation and full name.
        """
        if not isinstance(value, str):
            return pd.NA, pd.NA
            
        return self._lookup.get(value.upper(), (pd.NA, pd.NA))

def get_valid_dataframe(log: ContestLog, include_dupes: bool = False) -> pd.DataFrame:
    """
    Returns the processed DataFrame from a ContestLog, optionally filtering out dupes.
    """
    df = log.get_processed_data()
    if not include_dupes:
        return df[df['Dupe'] == False].copy()
    return df.copy()

def create_output_directory(path: str):
    """
    Ensures that the specified output directory exists.
    """
    os.makedirs(path, exist_ok=True)
