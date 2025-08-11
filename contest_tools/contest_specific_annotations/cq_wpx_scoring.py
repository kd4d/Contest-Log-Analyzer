# Contest Log Analyzer/contest_tools/contest_specific_annotations/cq_wpx_scoring.py
#
# Purpose: Provides contest-specific scoring logic for the CQ WPX contest.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-11
# Version: 0.31.63-Beta
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
## [0.31.63-Beta] - 2025-08-11
### Fixed
# - Corrected the North American scoring rule to apply only to contacts
#   between different countries within North America, fixing inflated scores.
## [0.31.62-Beta] - 2025-08-11
### Fixed
# - Rewrote the scoring logic to precisely match the official WPX rules,
#   removing all incorrect or non-existent "standard rules".
## [0.31.61-Beta] - 2025-08-11
### Fixed
# - Corrected a fall-through bug by adding return statements to the North
#   American scoring logic, preventing points from being overwritten.
## [0.31.60-Beta] - 2025-08-11
### Added
# - Added the special scoring rule for contacts between two North
#   American stations.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
# - Standardized all project files to a common baseline version.
import pandas as pd
from typing import Dict, Any

def _calculate_points_single_qso(
    row: pd.Series,
    my_continent: str,
    my_dxcc_name: str
) -> int:
    """
    Calculates points for a single QSO based on CQ WPX rules.
    """
    if row['Dupe']:
        return 0

    band = row.get('Band', '')
    worked_continent = row.get('Continent')
    worked_dxcc_name = row.get('DXCCName')

    # Rule 1: Contacts between stations on different continents.
    if worked_continent != my_continent:
        if band in ['160M', '80M', '40M']: return 6
        if band in ['20M', '15M', '10M']: return 3

    # Rule 2: Contacts between stations on the same continent.
    elif worked_continent == my_continent:
        # Special Exception for North America (different countries only)
        if my_continent == 'NA' and worked_dxcc_name != my_dxcc_name:
            if band in ['160M', '80M', '40M']:
                return 4
            if band in ['20M', '15M', '10M']:
                return 2
        
        # Standard same-continent, different-country rule
        elif worked_dxcc_name != my_dxcc_name:
            if band in ['160M', '80M', '40M']: return 2
            if band in ['20M', '15M', '10M']: return 1

    # Rule 3: Contacts between stations in the same country.
    if worked_dxcc_name == my_dxcc_name:
        return 1

    return 0

def calculate_points(df: pd.DataFrame, my_call_info: Dict[str, Any]) -> pd.Series:
    """
    Calculates QSO points for an entire DataFrame based on CQ WPX rules.
    """
    my_continent = my_call_info.get('Continent')
    my_dxcc_name = my_call_info.get('DXCCName')

    if not my_continent or not my_dxcc_name:
        raise ValueError("Logger's Continent and DXCC Name must be provided.")

    return df.apply(
        _calculate_points_single_qso,
        axis=1,
        my_continent=my_continent,
        my_dxcc_name=my_dxcc_name
    )