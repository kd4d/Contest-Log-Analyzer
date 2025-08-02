# Contest Log Analyzer/contest_tools/reports/_report_utils.py
#
# Purpose: A helper module with shared, reusable logic for report generation,
#          primarily for aligning time-series data from multiple logs.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-01
# Version: 0.25.0-Beta
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

## [0.25.0-Beta] - 2025-08-01
### Changed
# - The 'align_logs_by_time' function now accepts a pre-calculated master
#   time index to ensure all reports use a consistent contest period.

## [0.22.2-Beta] - 2025-08-01
### Changed
# - The pie chart logic now excludes 0-point QSOs from the chart itself
#   to prevent clutter, while still including them in the summary table.

## [0.22.1-Beta] - 2025-08-01
### Changed
# - Removed the internal percentage labels from pie charts and made the
#   external labels larger and bold for better readability.

## [0.22.0-Beta] - 2025-08-01
### Added
# - Added the '_create_pie_chart_subplot' helper function to encapsulate
#   all pie chart drawing and layout logic into a single reusable component.

## [0.15.0-Beta] - 2025-07-25
# - Initial release of the report utilities helper module.
# - Includes the 'align_logs_by_time' function for robust time-series analysis.

from typing import List, Dict
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

from ..contest_log import ContestLog

def align_logs_by_time(
    logs: List[ContestLog],
    value_column: str,
    agg_func: str,
    master_index: pd.DatetimeIndex,
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
        master_index (pd.DatetimeIndex): The pre-calculated time index for the contest.
        band_filter (str): The band to filter for (e.g., '20M', or 'All').
        time_unit (str): The time frequency for resampling (e.g., '1h', '10min').

    Returns:
        Dict[str, pd.DataFrame]: A dictionary where keys are callsigns and values
                                 are perfectly aligned DataFrames of aggregated data.
    """
    processed_logs = {}

    for log in logs:
        callsign = log.get_metadata().get('MyCall', 'Unknown')
        df_full = log.get_processed_data()[log.get_processed_data()['Dupe'] == False].copy()
        
        if band_filter != "All":
            df = df_full[df_full['Band'] == band_filter].copy()
        else:
            df = df_full.copy()

        if df.empty:
            continue
        
        pt = df.pivot_table(
            index=pd.to_datetime(df['Datetime']).dt.floor(time_unit), 
            columns='Run', 
            values=value_column, 
            aggfunc=agg_func
        ).fillna(0)
        
        for col in ['Run', 'S&P', 'Unknown']:
            if col not in pt.columns:
                pt[col] = 0
        
        pt['S&P+Unknown'] = pt['S&P'] + pt['Unknown']
        pt['Overall'] = pt['Run'] + pt['S&P+Unknown']
        
        processed_logs[callsign] = pt

    if not processed_logs:
        return {}

    aligned_logs = {}
    for callsign, pt in processed_logs.items():
        aligned_logs[callsign] = pt.reindex(master_index, fill_value=0)

    return aligned_logs

def _create_pie_chart_subplot(fig: plt.Figure, gs: GridSpec, band_df: pd.DataFrame, title: str, radius: float, is_not_to_scale: bool):
    """
    Generates a single pie chart "widget" within a given GridSpec.
    """
    # Create a nested GridSpec for this widget (3 rows: title, chart, table)
    nested_gs = gs.subgridspec(3, 1, height_ratios=[0.5, 3, 1.5])

    # --- Title ---
    ax_title = fig.add_subplot(nested_gs[0, 0])
    ax_title.text(0.5, 0.5, title, ha='center', va='center', fontweight='bold', fontsize=16)
    ax_title.axis('off')

    # --- Pie Chart ---
    ax_pie = fig.add_subplot(nested_gs[1, 0])
    if band_df.empty or 'QSOPoints' not in band_df.columns or band_df['QSOPoints'].sum() == 0:
        ax_pie.text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=12)
        ax_pie.axis('off')
        # Turn off the table axis as well
        ax_table = fig.add_subplot(nested_gs[2, 0])
        ax_table.axis('off')
        return

    point_summary = band_df.groupby('QSOPoints').agg(
        QSOs=('Call', 'count')
    ).reset_index()
    point_summary['Points'] = point_summary['QSOPoints'] * point_summary['QSOs']
    
    # Exclude 0-point QSOs from the pie chart visualization
    pie_chart_data = point_summary[point_summary['QSOPoints'] > 0]
    
    pie_data = pie_chart_data.set_index('QSOPoints')['Points']
    labels = [f"{idx} Pts" for idx in pie_data.index]
    
    wedges, texts = ax_pie.pie(pie_data, labels=labels, autopct=None,
                               startangle=90, counterclock=False, radius=radius,
                               textprops={'fontsize': 12, 'fontweight': 'bold'})
    
    ax_pie.set_aspect('equal') # Ensure the pie is a circle

    # --- "Not to Scale" Note ---
    if is_not_to_scale:
        ax_pie.text(0.5, 0.0, "*NOT TO SCALE*", ha='center', va='center',
                    transform=ax_pie.transAxes, fontsize=12, fontweight='bold')

    # --- Summary Table ---
    ax_table = fig.add_subplot(nested_gs[2, 0])
    ax_table.axis('off')
    
    total_row = pd.DataFrame({
        'QSOPoints': ['Total'],
        'QSOs': [point_summary['QSOs'].sum()],
        'Points': [point_summary['Points'].sum()],
        'AVG': [point_summary['Points'].sum() / point_summary['QSOs'].sum() if point_summary['QSOs'].sum() > 0 else 0]
    })
    
    point_summary['AVG'] = point_summary['QSOPoints']
    table_data = pd.concat([point_summary, total_row], ignore_index=True)
    table_data['AVG'] = table_data['AVG'].map('{:.2f}'.format)
    
    cell_text = table_data[['QSOPoints', 'QSOs', 'Points', 'AVG']].values
    col_labels = ['Pts/QSO', 'QSOs', 'Points', 'Avg']
    
    table = ax_table.table(cellText=cell_text, colLabels=col_labels, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
