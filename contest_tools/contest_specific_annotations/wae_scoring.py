# contest_tools/contest_specific_annotations/wae_scoring.py
#
# Purpose: This module provides the base QSO scoring logic for the WAE Contest.
#
#
# Author: Gemini AI
# Date: 2025-10-01
# Version: 0.90.0-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# --- Revision History ---
# [0.90.0-Beta] - 2025-10-01
# Set new baseline version for release.

import pandas as pd
from typing import Dict, Any

def calculate_points(df: pd.DataFrame, my_call_info: Dict[str, Any]) -> pd.Series:
    """
    Calculates QSO points for an entire DataFrame based on WAE rules.
    - Each valid (non-dupe) QSO is worth 1 point.
    - QTC points are handled separately by the time-series score calculator.

    Args:
        df (pd.DataFrame): The DataFrame of QSOs to be scored.
        my_call_info (Dict[str, Any]): Not used for this contest's scoring.

    Returns:
        pd.Series: A Pandas Series containing the calculated points for each QSO.
    """
    # Create a Series of 1s for all rows
    points = pd.Series(1, index=df.index)

    # Set points to 0 for any row marked as a dupe
    if 'Dupe' in df.columns:
        points[df['Dupe'] == True] = 0
        
    return points
