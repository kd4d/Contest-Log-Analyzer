# Contest Log Analyzer/contest_tools/contest_specific_annotations/arrl_ss_multiplier_resolver.py
#
# Purpose: A contest-specific annotation module to resolve section multipliers
#          for the ARRL Sweepstakes contest.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-07
# Version: 0.30.36-Beta
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
## [0.30.36-Beta] - 2025-08-07
### Fixed
# - Corrected an ImportError by moving the `load_arrl_sections` helper
#   function into this module.
# - Standardized the column name to 'SECName' to align with the master
#   column list.
## [0.30.35-Beta] - 2025-08-07
### Fixed
# - Added logic to look up and populate the 'SECName' column, resolving a
#   warning in the contest log processing.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
import pandas as pd
import os

def load_arrl_sections(filepath: str) -> dict:
    """Loads ARRL section abbreviations and names from the DAT file."""
    sections = {}
    with open(filepath, 'r') as f:
        for line in f:
            if not line.strip() or line.startswith('#'):
                continue
            parts = line.split(':')
            if len(parts) == 2:
                sections[parts[0].strip()] = parts[1].strip()
    return sections

def resolve_multipliers(qsos_df: pd.DataFrame, my_location_type: str) -> pd.DataFrame:
    """
    Adds a 'STPROV_MultName' column by looking up the full section name.
    """
    data_dir = os.environ.get('CONTEST_DATA_DIR').strip().strip('"').strip("'")
    sections_filepath = os.path.join(data_dir, 'SweepstakesSections.dat')
    sections_map = load_arrl_sections(sections_filepath)
    
    qsos_df['STPROV_MultName'] = qsos_df['SEC'].map(sections_map)
    qsos_df['SECName'] = qsos_df['STPROV_MultName']

    return qsos_df