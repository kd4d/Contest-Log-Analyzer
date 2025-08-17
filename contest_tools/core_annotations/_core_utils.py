# Contest Log Analyzer/contest_tools/core_annotations/_core_utils.py
#
# Purpose: A utility module containing shared helper functions used by various
#          core annotation and resolver modules.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-17
# Version: 0.37.4-Beta
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
## [0.37.4-Beta] - 2025-08-17
### Changed
# - Added logic to detect ambiguous aliases (e.g., VE1) in .dat files,
#   log a warning, and nullify the alias to prevent incorrect lookups.
## [0.32.1-Beta] - 2025-08-12
### Changed
# - Enhanced AliasLookup to be section-aware, parsing categories like
#   "US States" from comments in the .dat file.
### Added
# - Added a `get_category` method to the AliasLookup class.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
# - Standardized all project files to a common baseline version.

import pandas as pd
import os
import re
import logging
from typing import Dict, Tuple, Optional, Set

class AliasLookup:
    """
    Parses a standard multiplier alias file (e.g., NAQPmults.dat) and provides
    a lookup method to resolve aliases to their official abbreviation and full name.
    """
    def __init__(self, data_dir_path: str, alias_filename: str):
        self.filepath = os.path.join(data_dir_path, alias_filename)
        self._lookup: Dict[str, Tuple[str, str]] = {}
        self._valid_mults: Set[str] = set()
        self.sections: Dict[str, Set[str]] = {}
        self.multiplier_to_category: Dict[str, str] = {}
        self._ambiguous_aliases: Set[str] = set()
        self._parse_file()

    def _parse_file(self):
        current_section = "Default"
        section_pattern = re.compile(r'#\s*---\s*(.*?)\s*---')

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # Check for section header
                    header_match = section_pattern.match(line)
                    if header_match:
                        current_section = header_match.group(1).strip()
                        if current_section not in self.sections:
                            self.sections[current_section] = set()
                        continue

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
                    self.sections.setdefault(current_section, set()).add(official_abbr)
                    self.multiplier_to_category[official_abbr] = current_section

                    for alias in aliases:
                        # --- Ambiguous Alias Check ---
                        if alias in self._lookup and self._lookup[alias][0] != official_abbr:
                            logging.warning(
                                f"Ambiguous alias '{alias}' found in '{os.path.basename(self.filepath)}'. "
                                f"It is mapped to both '{self._lookup[alias][0]}' and '{official_abbr}'. "
                                f"This alias will be ignored."
                            )
                            self._ambiguous_aliases.add(alias)
                            del self._lookup[alias] # Remove the original entry
                        elif alias not in self._ambiguous_aliases:
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

        if value_upper in self._ambiguous_aliases:
            return pd.NA, pd.NA
            
        if value_upper in self._lookup:
            return self._lookup[value_upper]
        
        # Fallback for values that are already official abbreviations
        if value_upper in self._valid_mults:
            for abbr, (official_abbr, full_name) in self._lookup.items():
                if value_upper == official_abbr:
                    return official_abbr, full_name

        return pd.NA, pd.NA

    def get_category(self, multiplier: str) -> Optional[str]:
        """
        Returns the section category for a given official multiplier abbreviation.
        """
        return self.multiplier_to_category.get(multiplier)
