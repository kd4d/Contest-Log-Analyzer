# Contest Log Analyzer/contest_tools/contest_specific_annotations/arrl_dx_scoring.py
#
# Purpose: Provides contest-specific scoring logic for the ARRL DX contest.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-01
# Version: 0.23.0-Beta
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

## [0.23.0-Beta] - 2025-08-01
### Added
# - Initial release of the ARRL DX contest scoring module.

import pandas as pd
from typing import Dict, Any

def _calculate_single_qso_points(row: pd.Series, my_location_type: str) -> int:
    """
    Calculates the point value for a single QSO based on ARRL DX rules.
    """
    # Rule: Dupes are always 0 points.
    if row['Dupe']:
        return 0

    # Determine worked station's location type from its DXCC entity name
    worked_entity_name = row.get('DXCCName', 'Unknown')
    worked_location_type = "W/VE" if worked_entity_name in ["United States", "Canada"] else "DX"

    # W/VE stations can only work DX stations for points
    if my_location_type == "W/VE":
        return 3 if worked_location_type == "DX" else 0
        
    # DX stations can only work W/VE stations for points
    elif my_location_type == "DX":
        return 3 if worked_location_type == "W/VE" else 0
    
    # Fallback case, should not be reached
    return 0

def calculate_points(df: pd.DataFrame, my_call_info: Dict[str, Any]) -> pd.Series:
    """
    Calculates QSO points for an entire DataFrame based on ARRL DX rules.

    Args:
        df (pd.DataFrame): The DataFrame of QSOs to be scored.
        my_call_info (Dict[str, Any]): A dictionary containing the logger's
                                       own location info ('DXCCName').

    Returns:
        pd.Series: A Pandas Series containing the calculated points for each QSO.
    """
    my_entity_name = my_call_info.get('DXCCName')
    if not my_entity_name:
        raise ValueError("Logger's own DXCC Name must be provided for scoring.")

    my_location_type = "W/VE" if my_entity_name in ["United States", "Canada"] else "DX"

    # Apply the scoring logic to each row of the DataFrame.
    return df.apply(
        _calculate_single_qso_points, 
        axis=1, 
        my_location_type=my_location_type
    )