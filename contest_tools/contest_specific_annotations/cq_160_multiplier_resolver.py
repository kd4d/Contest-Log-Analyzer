# Contest Log Analyzer/contest_tools/contest_specific_annotations/cq_160_multiplier_resolver.py
#
# Purpose: A contest-specific annotation module to resolve multipliers for the
#          CQ 160 contest.
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
#   column name and to handle missing CTY data gracefully.
## [0.30.63-Beta] - 2025-08-07
### Added
# - Added a diagnostic try/except block to debug a recurring KeyError.
## [0.30.62-Beta] - 2025-08-07
### Fixed
# - Corrected an ImportError and implemented the correct multiplier logic
#   for the CQ 160 contest.
# ---
import pandas as pd
import os
import logging

def resolve_multipliers(qsos_df: pd.DataFrame, my_location_type: str) -> pd.DataFrame:
    """
    Adds STPROV and DXCC multiplier columns to the DataFrame.
    """
    def get_mult(row):
        is_sp = isinstance(row['Exch'], str) and not row['Exch'].isdigit()
        
        if is_sp:
            row['STPROV_Mult'] = row['Exch']
            row['STPROV_MultName'] = row['Exch']
        else:
            if pd.notna(row['DXCCPfx']):
                row['DXCC_Mult'] = row['DXCCPfx']
                row['DXCC_MultName'] = row['DXCCName']
        
        return row

    qsos_df = qsos_df.apply(get_mult, axis=1)
    return qsos_df