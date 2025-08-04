# Contest Log Analyzer/contest_tools/reports/_report_utils.py
#
# Purpose: A utility module containing shared helper functions used by various
#          report generation scripts.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-04
# Version: 0.30.4-Beta
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
## [0.30.4-Beta] - 2025-08-04
### Changed
# - Reverted plotting functions from Plotly back to Matplotlib and Seaborn.
# - Removed Plotly-specific saving logic from the ReportInterface.
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from typing import Optional, List

def create_report_string(header: List[str], body: str, footer: List[str]) -> str:
    """Combines header, body, and footer into a single formatted string."""
    return "\n".join(header) + "\n\n" + body + "\n\n" + "\n".join(footer)

def get_default_band_summary(df: pd.DataFrame, valid_bands: List[str]) -> pd.DataFrame:
    """Creates a default band summary DataFrame with QSOs, Dupes, and Points."""
    df_no_dupes = df[df['Dupe'] == False]
    
    qso_counts = df_no_dupes['Band'].value_counts()
    dupe_counts = df[df['Dupe'] == True]['Band'].value_counts()
    point_counts = df_no_dupes.groupby('Band')['QSOPoints'].sum()

    summary = pd.DataFrame(index=valid_bands)
    summary['QSOs'] = qso_counts
    summary['Dupes'] = dupe_counts
    summary['Points'] = point_counts
    summary.fillna(0, inplace=True)
    summary = summary.astype(int)
    
    return summary

def format_qso_summary(summary_df: pd.DataFrame, column_order: List[str]) -> str:
    """Formats a QSO summary DataFrame into a fixed-width string table."""
    summary_df_copy = summary_df.copy()
    
    total_row = summary_df_copy.sum(numeric_only=True)
    total_row['AVG'] = (total_row['Points'] / total_row['QSOs']) if total_row['QSOs'] > 0 else 0
    total_row.name = "TOTAL"
    
    # Append the total row
    summary_df_copy = pd.concat([summary_df_copy, pd.DataFrame(total_row).T])
    
    # Ensure all columns exist, fill missing with 0
    for col in column_order:
        if col not in summary_df_copy.columns:
            summary_df_copy[col] = 0
            
    summary_df_copy = summary_df_copy[column_order].fillna(0)
    
    # Convert appropriate columns to int for formatting
    int_cols = [col for col in summary_df_copy.columns if col != 'AVG']
    summary_df_copy[int_cols] = summary_df_copy[int_cols].astype(int)
    
    return summary_df_copy.to_string(formatters={'AVG': '{:,.2f}'.format})

def get_multiplier_source_column(log, mult_name: str) -> Optional[str]:
    """Finds the source column for a given multiplier name."""
    for rule in log.contest_definition.multiplier_rules:
        if rule.get('name', '').lower() == mult_name.lower():
            return rule.get('source_column')
    return None