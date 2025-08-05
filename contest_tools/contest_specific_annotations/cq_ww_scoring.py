# Contest Log Analyzer/contest_tools/contest_specific_annotations/cq_ww_scoring.py
#
# Purpose: Provides contest-specific scoring logic for the CQ WW DX contest.
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

def _calculate_single_qso_points(row: pd.Series, my_continent: str, my_dxcc_name: str) -> int:
    """
    Calculates the point value for a single QSO based on CQ WW rules.
    """
    # Rule: Dupes and contacts with own station are always 0 points.
    if row['Dupe']:
        return 0

    worked_continent = row.get('Continent')
    worked_dxcc_name = row.get('DXCCName')

    # Rule: Contacts between stations on different continents are worth 3 points.
    if worked_continent and worked_continent != my_continent:
        return 3

    # Rule: Contacts between stations on the same continent but in different countries are 1 point.
    if worked_continent and worked_continent == my_continent and worked_dxcc_name != my_dxcc_name:
        return 1

    # Rule: Contacts between stations in the same country are worth 0 points.
    if worked_dxcc_name == my_dxcc_name:
        return 0
        
    # Rule: Contacts between stations in North America are worth 2 points.
    # This is a special case that overrides the 1-point same-continent rule.
    # The 'WAEName' column from cty.dat will contain 'North America' for these stations.
    my_wae_name = row.get('MyWAEName') # This should be added to the row from my_call_info
    worked_wae_name = row.get('WAEName')
    if my_wae_name == 'North America' and worked_wae_name == 'North America':
        return 2

    # Fallback case, should not be reached often
    return 0

def calculate_points(df: pd.DataFrame, my_call_info: Dict[str, Any]) -> pd.Series:
    """
    Calculates QSO points for an entire DataFrame based on CQ WW DX rules.

    Args:
        df (pd.DataFrame): The DataFrame of QSOs to be scored.
        my_call_info (Dict[str, Any]): A dictionary containing the logger's
                                       own location info ('Continent', 'DXCCName', 'WAEName').

    Returns:
        pd.Series: A Pandas Series containing the calculated points for each QSO.
    """
    my_continent = my_call_info.get('Continent')
    my_dxcc_name = my_call_info.get('DXCCName')
    
    if not my_continent or not my_dxcc_name:
        raise ValueError("Logger's Continent and DXCC Name must be provided.")
        
    # Add my own WAE name to each row for the scoring function to use.
    # This is slightly inefficient but makes the per-row logic cleaner.
    df_temp = df.copy()
    df_temp['MyWAEName'] = my_call_info.get('WAEName')

    return df_temp.apply(
        _calculate_single_qso_points,
        axis=1,
        my_continent=my_continent,
        my_dxcc_name=my_dxcc_name
    )