# Contest Log Analyzer/contest_tools/contest_specific_annotations/arrl_fd_scoring.py
#
# Version: 0.39.0-Beta
# Date: 2025-08-18
#
# Purpose: Provides contest-specific scoring logic for the ARRL Field Day contest.
#
import pandas as pd
from typing import Dict, Any

def calculate_points(df: pd.DataFrame, my_call_info: Dict[str, Any]) -> pd.Series:
    """
    Calculates QSO points for an entire DataFrame based on ARRL Field Day rules.
    """
    points = pd.Series(0, index=df.index)

    # Create boolean masks for each mode category
    is_cw_dg = (df['Mode'] == 'CW') | (df['Mode'] == 'DG')
    is_ph = (df['Mode'] == 'PH')
    is_dupe = (df['Dupe'] == True)

    # Assign points based on mode
    points[is_cw_dg] = 2
    points[is_ph] = 1

    # Overwrite points to 0 for any row marked as a dupe
    points[is_dupe] = 0

    return points