# Contest Log Analyzer/contest_tools/contest_specific_annotations/naqp_scoring.py
#
# Purpose: Provides contest-specific scoring logic for the NAQP contest.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-04
# Version: 0.29.5-Beta
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
## [0.29.5-Beta] - 2025-08-04
### Added
# - Initial Release of Version 0.29.5
import pandas as pd
from typing import Dict, Any

def calculate_points(df: pd.DataFrame, my_call_info: Dict[str, Any]) -> pd.Series:
    """
    Calculates QSO points for an entire DataFrame based on NAQP rules.
    Each valid (non-dupe) QSO is worth 1 point.
    """
    points = pd.Series(1, index=df.index)
    
    if 'Dupe' in df.columns:
        points[df['Dupe'] == True] = 0
        
    return points