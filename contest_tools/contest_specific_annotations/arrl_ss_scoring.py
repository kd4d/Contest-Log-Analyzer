# Contest Log Analyzer/contest_tools/contest_specific_annotations/arrl_ss_scoring.py
#
# Purpose: Provides contest-specific scoring logic for the ARRL Sweepstakes contest.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-01
# Version: 0.24.0-Beta
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

## [0.24.0-Beta] - 2025-08-01
### Added
# - Initial release of the ARRL Sweepstakes contest scoring module.

import pandas as pd
from typing import Dict, Any

def calculate_points(df: pd.DataFrame, my_call_info: Dict[str, Any]) -> pd.Series:
    """
    Calculates QSO points for an entire DataFrame based on ARRL Sweepstakes rules.
    Each valid (non-dupe) QSO is worth 2 points.

    Args:
        df (pd.DataFrame): The DataFrame of QSOs to be scored.
        my_call_info (Dict[str, Any]): Not used for this contest's scoring.

    Returns:
        pd.Series: A Pandas Series containing the calculated points for each QSO.
    """
    # Create a Series of 2s for all rows
    points = pd.Series(2, index=df.index)
    
    # Set points to 0 for any row marked as a dupe
    if 'Dupe' in df.columns:
        points[df['Dupe'] == True] = 0
        
    return points
