# Contest Log Analyzer/contest_tools/reports/_report_utils.py
#
# Purpose: A helper module with shared, reusable logic for report generation,
#          primarily for aligning time-series data from multiple logs.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-25
# Version: 0.15.0-Beta
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

## [0.15.0-Beta] - 2025-07-25
# - Initial release of the report utilities helper module.
# - Includes the 'align_logs_by_time' function for robust time-series analysis.

from typing import List, Dict
import pandas as pd

from ..contest_log import ContestLog

def align_logs_by_time(
    logs: List[ContestLog],
    value_column: str,
    agg_func: str,
    band_filter: str = "All",
    time_unit: str = '1h'
) -> Dict[str, pd.DataFrame]:
    """
    Aggregates and aligns time-series data from multiple logs to a common,
    continuous time index.

    Args:
        logs (List[ContestLog]): The list of ContestLog objects to process.
        value_column (str): The column to aggregate (e.g., 'QSOPoints' or 'Call').
        agg_func (str): The aggregation function to use ('sum' or 'count').
        band_filter (str): The band to filter for (e.g., '20M', or 'All').
        time_unit (str): The time frequency for resampling (e.g., '1h', '10min').

    Returns:
        Dict[str, pd.DataFrame]: A dictionary where keys are callsigns and values
                                 are perfectly aligned DataFrames of aggregated data.
    """
    processed_logs = {}
    all_datetimes = []

    # First pass: process each log individually and find the global time range
    for log in logs:
        callsign = log.get_metadata().get('MyCall', 'Unknown')
        df_full = log.get_processed_data()[log.get_processed_data()['Dupe'] == False].copy()
        
        # Apply the band filter
        if band_filter != "All":
            df = df_full[df_full['Band'] == band_filter].copy()
        else:
            df = df_full.copy()

        if df.empty:
            continue
        
        all_datetimes.extend(df['Datetime'])
        
        # Create a pivot table for the current log
        pt = df.pivot_table(
            index='Datetime', 
            columns='Run', 
            values=value_column, 
            aggfunc=agg_func
        ).resample(time_unit).sum().fillna(0)
        
        for col in ['Run', 'S&P', 'Unknown']:
            if col not in pt.columns:
                pt[col] = 0
        
        pt['S&P+Unknown'] = pt['S&P'] + pt['Unknown']
        pt['Overall'] = pt['Run'] + pt['S&P+Unknown']
        
        processed_logs[callsign] = pt

    if not processed_logs or not all_datetimes:
        return {}

    # Second pass: align all processed logs to a master time index
    start_time = min(all_datetimes).floor(time_unit)
    end_time = max(all_datetimes).ceil(time_unit)
    master_index = pd.date_range(start=start_time, end=end_time, freq=time_unit)

    aligned_logs = {}
    for callsign, pt in processed_logs.items():
        aligned_logs[callsign] = pt.reindex(master_index, fill_value=0)

    return aligned_logs
