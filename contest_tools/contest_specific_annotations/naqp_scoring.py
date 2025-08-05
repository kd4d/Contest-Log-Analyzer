# Contest Log Analyzer/contest_tools/contest_specific_annotations/naqp_scoring.py
#
# Purpose: Provides contest-specific scoring logic for the NAQP contest.
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
from typing import Dict, Any

def calculate_points(df: pd.DataFrame, my_call_info: Dict[str, Any]) -> pd.Series:
    """
    Calculates QSO points for an entire DataFrame based on NAQP rules.
    - Each valid (non-dupe) QSO with a North American station is worth 1 point.
    - QSOs with stations outside North America are worth 0 points.
    """
    if df.empty or 'Dupe' not in df.columns or 'WAEName' not in df.columns:
        return pd.Series(0, index=df.index)

    # Assume 0 points by default
    points = pd.Series(0, index=df.index)
    
    # Conditions for a valid, 1-point QSO:
    # 1. Not a dupe.
    # 2. Worked station's 'WAEName' from cty.dat is 'North America'.
    valid_qso_mask = (df['Dupe'] == False) & (df['WAEName'] == 'North America')
    
    # Assign 1 point to all valid QSOs
    points[valid_qso_mask] = 1
        
    return points