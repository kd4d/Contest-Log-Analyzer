# Contest Log Analyzer/contest_tools/contest_specific_annotations/cq_160_scoring.py
#
# Purpose: Provides contest-specific scoring logic for the CQ 160 contest.
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
# All notable changes to this project will be documented in this file.
## [0.29.5-Beta] - 2025-08-04
### Changed
# - Replaced all `print` statements with calls to the new logging framework.
## [0.29.0-Beta] - 2025-08-03
### Added
# - Initial release of the CQ 160 contest scoring module.

import pandas as pd
from typing import Dict, Any
import logging

def _calculate_single_qso_points(row: pd.Series, my_dxcc_pfx: str, my_continent: str) -> int:
    """
    Calculates the point value for a single QSO based on CQ 160 rules.
    This is an internal helper function designed to be used with df.apply().
    """
    # Rule: Dupes are always 0 points.
    if row['Dupe']:
        return 0

    # If essential data is missing, QSO is worth 0 points.
    if pd.isna(row['DXCCPfx']) or pd.isna(row['Continent']):
        logging.warning(f"Scoring failed for QSO with {row['Call']} at {row['Datetime']}. Missing DXCC or Continent info. Assigning 0 points.")
        return 0
        
    # Rule: Maritime Mobile contacts count 5 points.
    if isinstance(row['Call'], str) and row['Call'].endswith('/MM'):
        return 5

    # Rule: Contacts with stations in own country are worth 2 points.
    if row['DXCCPfx'] == my_dxcc_pfx:
        return 2

    # Rule: Contacts with other countries on same continent are worth 5 points.
    if row['Continent'] == my_continent and row['DXCCPfx'] != my_dxcc_pfx:
        return 5

    # Rule: Contacts with other continents are worth 10 points.
    if row['Continent'] != my_continent:
        return 10
    
    # Fallback case, should not be reached with valid data.
    return 0

def calculate_points(df: pd.DataFrame, my_call_info: Dict[str, Any]) -> pd.Series:
    """
    Calculates QSO points for an entire DataFrame based on CQ 160 rules.

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