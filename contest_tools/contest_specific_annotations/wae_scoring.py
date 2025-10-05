# contest_tools/contest_specific_annotations/wae_scoring.py
#
# Purpose: This module provides the base QSO scoring logic for the WAE Contest.
#
#
# Author: Gemini AI
# Date: 2025-10-04
# Version: 0.90.1-Beta
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
# [0.90.1-Beta] - 2025-10-04
# - Rewrote scoring logic to correctly award 0 points for invalid QSOs
#   (e.g., EU-to-EU) based on the WAE contest rules.
# [0.90.0-Beta] - 2025-10-01
# - Set new baseline version for release.

import pandas as pd
from typing import Dict, Any

def calculate_points(df: pd.DataFrame, my_call_info: Dict[str, Any]) -> pd.Series:
    """
    Calculates QSO points for an entire DataFrame based on WAE rules.
    - Each valid (non-dupe) QSO between an EU and non-EU station is worth 1 point.
    - Invalid QSOs (EU-EU, non-EU-non-EU) are worth 0 points.
    - QTC points are handled separately by the time-series score calculator.
    """
    my_continent = my_call_info.get('Continent')
    if not my_continent:
        raise ValueError("Logger's own Continent must be provided for WAE scoring.")

    is_logger_eu = (my_continent == 'EU')

    def is_qso_valid(row):
        # Dupes are always 0 points
        if row['Dupe']:
            return 0
        
        is_worked_eu = (row['Continent'] == 'EU')
        
        if (is_logger_eu and not is_worked_eu) or (not is_logger_eu and is_worked_eu):
            return 1  # Valid EU to non-EU contact
        else:
            return 0  # Invalid EU-EU or non-EU-non-EU contact
            
    return df.apply(is_qso_valid, axis=1)