# Contest Log Analyzer/contest_tools/contest_specific_annotations/cq_ww_multiplier_resolver.py
#
# Purpose: A contest-specific annotation module to resolve multipliers for the
#          CQ WW contest.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-07
# Version: 0.30.64-Beta
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
## [0.30.64-Beta] - 2025-08-07
### Fixed
# - Corrected a KeyError by updating the script to use the correct 'DXCCPfx'
#   column name from the CTY lookup.
## [0.30.60-Beta] - 2025-08-07
# - Initial release of the CQ WW multiplier resolver.
# ---
import pandas as pd

def resolve_multipliers(qsos_df: pd.DataFrame, my_location_type: str) -> pd.DataFrame:
    """
    Adds Zone and DXCC multiplier columns to the DataFrame.
    """
    # --- Zone Multiplier (Simple) ---
    qsos_df['Zone_Mult'] = qsos_df['Exch']
    qsos_df['Zone_MultName'] = qsos_df['Exch']
    
    # --- DXCC Multiplier (Complex) ---
    if 'DXCCPfx' in qsos_df.columns:
        qsos_df['DXCC_Mult'] = qsos_df['DXCCPfx']
        if 'DXCCName' in qsos_df.columns:
            qsos_df['DXCC_MultName'] = qsos_df['DXCCName']

    return qsos_df