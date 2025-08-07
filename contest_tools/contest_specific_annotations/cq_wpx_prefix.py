# Contest Log Analyzer/contest_tools/contest_specific_annotations/cq_wpx_prefix.py
#
# Purpose: A contest-specific annotation module to resolve the prefix for
#          each QSO in a CQ WPX contest log.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-07
# Version: 0.30.41-Beta
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
## [0.30.41-Beta] - 2025-08-07
### Fixed
# - Added the missing 'Prefix_MultName' column to ensure data
#   consistency with other multiplier modules.
## [0.30.31-Beta] - 2025-08-07
### Fixed
# - Corrected an AttributeError by adding a check for pandas NA values
#   before attempting string operations.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
import pandas as pd
import re

def _get_prefix(call: str) -> str:
    """
    Extracts the contest prefix from a callsign.
    Handles portable identifiers and removes digits from the end.
    """
    if pd.isna(call) or not isinstance(call, str):
        return pd.NA
        
    call = call.split('/')[0]
    
    # Find the last letter in the callsign
    last_letter_index = -1
    for i in range(len(call) - 1, -1, -1):
        if call[i].isalpha():
            last_letter_index = i
            break
            
    if last_letter_index != -1:
        return call[:last_letter_index + 1]
    else:
        return call

def resolve_multipliers(qsos_df: pd.DataFrame, my_location_type: str) -> pd.DataFrame:
    """
    Adds 'Prefix_Mult' and 'Prefix_MultName' columns to the DataFrame.
    """
    qsos_df['Prefix_Mult'] = qsos_df['Call'].apply(_get_prefix)
    qsos_df['Prefix_MultName'] = qsos_df['Prefix_Mult']
    return qsos_df