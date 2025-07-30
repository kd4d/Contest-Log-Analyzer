# Contest Log Analyzer/contest_tools/contest_specific_annotations/cq_ww_scoring.py
#
# Purpose: Provides contest-specific scoring logic for the CQ WW contest.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-29
# Version: 0.21.0-Beta
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

## [0.21.0-Beta] - 2025-07-29
### Changed
# - Updated scoring logic to correctly handle Maritime Mobile (/MM) stations
#   and stations with an "Unknown" country multiplier, per the official
#   CQ WW contest rules.

## [0.15.0-Beta] - 2025-07-25
# - Standardized version for final review. No functional changes.

## [0.14.1-Beta] - 2025-07-22
### Changed
# - Added a console warning when a QSO is scored as 0 due to missing
#   DXCC or Continent information, improving debuggability.

## [0.14.0-Beta] - 2025-07-22
### Fixed
# - Added checks for missing data (pd.isna) in the scoring logic to prevent
#   "boolean value of NA is ambiguous" errors. QSOs with unresolved country
#   or continent data will now correctly be scored as 0 points.

## [0.13.0-Beta] - 2025-07-22
# - Initial release of the CQ WW scoring module.
# - Implemented the official CQ WW scoring rules, including the special
#   case for North American stations.

import pandas as pd
from typing import Dict, Any

def _calculate_single_qso_points(row: pd.Series, my_dxcc_pfx: str, my_continent: str) -> int:
    """
    Calculates the point value for a single QSO based on CQ WW rules.
    This is an internal helper function designed to be used with df.apply().
    """
    # Rule: Dupes are always 0 points.
    if row['Dupe']:
        return 0
        
    # Rule: Maritime Mobile stations are worth 5 points.
    if isinstance(row['Call'], str) and row['Call'].endswith('/MM'):
        return 5

    # If essential data is missing (and not /MM), QSO is worth 0 points.
    if pd.isna(row['DXCCPfx']) or pd.isna(row['Continent']) or row['DXCCPfx'] == 'Unknown':
        print(f"Warning: Scoring failed for QSO with {row['Call']} at {row['Datetime']}. Missing DXCC or Continent info. Assigning 0 points.")
        return 0

    # Rule: Contacts between stations in the same country have zero (0) QSO point value.
    if row['DXCCPfx'] == my_dxcc_pfx:
        return 0

    # Rule: Contacts between stations on different continents.
    if row['Continent'] != my_continent:
        return 3 # Points are the same for high and low bands in this case

    # Rule: Contacts between stations on the same continent but in different countries.
    if row['Continent'] == my_continent and row['DXCCPfx'] != my_dxcc_pfx:
        # Special rule for North American stations.
        if my_continent == 'NA':
            return 2
        # Standard rule for all other continents.
        else:
            return 1
    
    # Fallback case, should not be reached with valid data.
    return 0

def calculate_points(df: pd.DataFrame, my_call_info: Dict[str, Any]) -> pd.Series:
    """
    Calculates QSO points for an entire DataFrame based on CQ WW rules.

    Args:
        df (pd.DataFrame): The DataFrame of QSOs to be scored.
        my_call_info (Dict[str, Any]): A dictionary containing the logger's
                                      own location info ('DXCCPfx' and 'Continent').

    Returns:
        pd.Series: A Pandas Series containing the calculated points for each QSO.
    """
    my_dxcc_pfx = my_call_info.get('DXCCPfx')
    my_continent = my_call_info.get('Continent')

    if not my_dxcc_pfx or not my_continent:
        raise ValueError("Logger's own DXCC Prefix and Continent must be provided for scoring.")

    # Apply the scoring logic to each row of the DataFrame.
    return df.apply(
        _calculate_single_qso_points, 
        axis=1, 
        my_dxcc_pfx=my_dxcc_pfx, 
        my_continent=my_continent
    )
