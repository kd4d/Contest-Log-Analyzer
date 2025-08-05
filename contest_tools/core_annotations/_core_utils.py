# Contest Log Analyzer/contest_tools/core_annotations/_core_utils.py
#
# Purpose: A utility module containing shared helper functions used by various
#          core annotation and resolver modules.
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
import os
import re
import logging
from typing import Dict, Tuple, Optional

class AliasLookup:
    """
    Parses a standard multiplier alias file (e.g., NAQPmults.dat) and provides
    a lookup method to resolve aliases to their official abbreviation and full name.
    """
    def __init__(self, data_dir_path: str, alias_filename: str):
        self.filepath = os.path.join(data_dir_path, alias_filename)
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
                    
                    match = re.match(r'([A-Z0-9]{1,4})\s+\((.*)\)', official_part.strip())
                    if not match:
                        continue
                    
                    official_abbr = match.group(1).upper()
                    full_name = match.group(2)
                    
                    self._valid_mults.add(official_abbr)
                    for alias in aliases:
                        self._lookup[alias] = (official_abbr, full_name)
        except FileNotFoundError:
            logging.warning(f"Multiplier alias file not found at {self.filepath}. Alias lookup will be disabled.")
        except Exception as e:
            logging.error(f"Error reading multiplier alias file {self.filepath}: {e}")

    def get_multiplier(self, value: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Looks up an alias and returns the official multiplier abbreviation and full name.
        """
        if not isinstance(value, str):
            return pd.NA, pd.NA
            
        value_upper = value.upper()
        if value_upper in self._lookup:
            return self._lookup[value_upper]
        
        # Fallback for values that are already official abbreviations
        if value_upper in self._valid_mults:
            for abbr, (official_abbr, full_name) in self._lookup.items():
                if value_upper == official_abbr:
                    return official_abbr, full_name

        return pd.NA, pd.NA