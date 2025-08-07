# Contest Log Analyzer/contest_tools/reports/_report_utils.py
#
# Purpose: A utility module providing shared helper functions for the
#          reporting engine.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-07
# Version: 0.30.39-Beta
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
## [0.30.39-Beta] - 2025-08-07
### Fixed
# - Corrected a ValueError by pre-processing the time-series data to
#   resolve duplicate timestamps before reindexing.
## [0.30.38-Beta] - 2025-08-07
### Fixed
# - Corrected a TypeError in _prepare_time_series_data by properly
#   calculating the cumulative QSO count instead of treating 'qsos' as
#   a column.
## [0.30.37-Beta] - 2025-08-07
### Fixed
# - Corrected a NameError by adding the missing import for 'Optional'
#   from the typing library.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os
import numpy as np
from typing import Optional
from ..contest_log import ContestLog

def get_valid_dataframe(log: ContestLog, include_dupes: bool = False) -> pd.DataFrame:
    """Returns the log's DataFrame, excluding dupes unless specified."""
    df = log.get_processed_data()
    return df if include_dupes else df[df['Dupe'] == False]

def create_output_directory(path: str):
    """Creates the output directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)

def _prepare_time_series_data(log1: ContestLog, log2: Optional[ContestLog], metric: str) -> tuple:
    """Prepares time-series data for one or two logs."""
    def _process_log_for_ts(df: pd.DataFrame, metric_col: str) -> pd.Series:
        if metric_col == 'qsos':
            ts = pd.Series(1, index=df['Datetime']).cumsum()
        else:
            ts = df.set_index('Datetime')[metric_col].cumsum()
        
        # --- FIX: Resolve duplicate timestamps before reindexing ---
        return ts.groupby(ts.index).last()

    df1 = get_valid_dataframe(log1).copy()
    df1_ts = _process_log_for_ts(df1, metric)
    
    df2_ts = None
    if log2:
        df2 = get_valid_dataframe(log2).copy()
        df2_ts = _process_log_for_ts(df2, metric)

    master_index = log1._log_manager_ref.master_time_index
    if master_index is not None:
        df1_ts = df1_ts.reindex(master_index, method='ffill').fillna(0)
        if df2_ts is not None:
            df2_ts = df2_ts.reindex(master_index, method='ffill').fillna(0)
            
    return df1_ts, df2_ts

def _create_time_series_figure(log: ContestLog, report_name: str) -> tuple:
    """Creates a standard figure and axes for time-series plots."""
    fig, ax = plt.subplots(figsize=(12, 7))
    
    metadata = log.get_metadata()
    year = get_valid_dataframe(log)['Date'].dropna().iloc[0].split('-')[0]
    contest_name = metadata.get('ContestName', '')
    event_id = metadata.get('EventID', '')
    
    title_line1 = f"{event_id} {year} {contest_name}".strip()
    title_line2 = f"{report_name}"
    fig.suptitle(f"{title_line1}\n{title_line2}", fontsize=16, fontweight='bold')
    
    ax.set_xlabel("Contest Time")
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    return fig, ax

class ChartComponent:
    """A factory class to create and draw a standardized pie chart component."""
    
    def __init__(self, df: pd.DataFrame, title: str, radius: float, is_not_to_scale: bool):
        self.df = df
        self.title = title
        self.radius = radius
        self.is_not_to_scale = is_not_to_scale

    def draw_on(self, fig, gridspec):
        subgrid = gridspec.subgridspec(2, 1, height_ratios=[3, 1])
        
        ax_pie = fig.add_subplot(subgrid[0])
        ax_table = fig.add_subplot(subgrid[1])
        ax_table.axis('off')

        point_counts = self.df['QSOPoints'].value_counts()
        total_points = self.df['QSOPoints'].sum()
        
        labels = [f'{val} Pts' for val in point_counts.index]
        sizes = point_counts.values
        
        colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(point_counts)))

        wedges, texts, autotexts = ax_pie.pie(
            sizes, labels=labels, autopct='%1.1f%%', startangle=140, 
            radius=self.radius, colors=colors, pctdistance=0.85, 
            wedgeprops=dict(width=0.4, edgecolor='w')
        )
        plt.setp(autotexts, size=10, weight="bold", color="white")
        
        ax_pie.set_title(self.title, fontsize=14, fontweight='bold')

        if self.is_not_to_scale:
            ax_pie.text(0, 0, "Not to Scale", ha='center', va='center', fontsize=12, color='red', alpha=0.7)

        table_data = [
            ["Total QSOs", f"{len(self.df)}"],
            ["Total Points", f"{total_points}"],
            ["Avg Pts/QSO", f"{total_points / len(self.df):.2f}" if len(self.df) > 0 else "0.00"]
        ]
        table = ax_table.table(cellText=table_data, colWidths=[0.4, 0.2], loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1.2, 1.2)