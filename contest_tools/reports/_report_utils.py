# Contest Log Analyzer/contest_tools/reports/_report_utils.py
#
# Purpose: A utility module providing shared helper functions for the
#          reporting engine.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-18
# Version: 0.38.1-Beta
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
## [0.38.1-Beta] - 2025-08-18
### Fixed
# - Added a custom NpEncoder class to the save_debug_data helper to
#   correctly handle JSON serialization of NumPy integer and float types.
## [0.38.0-Beta] - 2025-08-18
### Added
# - Added the save_debug_data() helper function to handle the creation of
#   debug data files for visual reports.
## [0.31.18-Beta] - 2025-08-08
### Changed
# - Removed percentage labels from donut charts for a cleaner appearance.
## [0.31.17-Beta] - 2025-08-08
### Changed
# - Renamed ChartComponent to DonutChartComponent and added logic to handle
#   dynamic radius scaling and "Not to scale" annotations.
## [0.31.4-Beta] - 2025-08-07
### Changed
# - Renamed ChartComponent to DonutChartComponent for clarity.
## [0.31.0-Beta] - 2025-08-07
# - Initial release of Version 0.31.0-Beta.
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os
import numpy as np
import re
import json
import logging
from pathlib import Path
from typing import Optional, Dict
from ..contest_log import ContestLog

class NpEncoder(json.JSONEncoder):
    """ Custom JSON encoder to handle NumPy data types. """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

def get_valid_dataframe(log: ContestLog, include_dupes: bool = False) -> pd.DataFrame:
    """Returns the log's DataFrame, excluding dupes unless specified."""
    df = log.get_processed_data()
    return df if include_dupes else df[df['Dupe'] == False]

def create_output_directory(path: str):
    """Creates the output directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)

def _sanitize_filename_part(part: str) -> str:
    """Sanitizes a string to be used as part of a filename."""
    return re.sub(r'[\s/\\:]+', '_', part.lower())

def _prepare_time_series_data(log1: ContestLog, log2: Optional[ContestLog], metric: str) -> tuple:
    """Prepares time-series data for one or two logs."""
    metrics_map = log1.contest_definition.metrics_map
    metric_col = metrics_map.get(metric)
    
    all_ts = []
    for log in [log1, log2]:
        if log is None:
            all_ts.append(None)
            continue
            
        df = get_valid_dataframe(log).copy()
        
        if metric_col is None: # Row count metric like 'qsos'
            ts = pd.Series(1, index=df['Datetime']).cumsum()
        else:
            ts = df.set_index('Datetime')[metric_col].cumsum()
        
        processed_ts = ts.groupby(ts.index).last()
        all_ts.append(processed_ts)

    df1_ts, df2_ts = all_ts

    # --- Reindex against master timeline ---
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

class DonutChartComponent:
    """A factory class to create and draw a standardized donut chart component."""
    
    def __init__(self, df: pd.DataFrame, title: str, radius: float, is_not_to_scale: bool):
        self.df = df
        self.title = title
        self.radius = radius
        self.is_not_to_scale = is_not_to_scale

    def draw_on(self, fig, gridspec):
        subgrid = gridspec.subgridspec(2, 1, height_ratios=[3, 1], hspace=0.3)
        
        ax_pie = fig.add_subplot(subgrid[0])
        ax_table = fig.add_subplot(subgrid[1])
        ax_table.axis('off')

        point_counts = self.df['QSOPoints'].value_counts()
        total_points = self.df['QSOPoints'].sum()
        
        labels = [f'{val} Pts' for val in point_counts.index]
        sizes = point_counts.values
        
        colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(point_counts)))

        wedges, texts = ax_pie.pie(
            sizes, labels=labels, autopct=None, startangle=140, 
            radius=self.radius, colors=colors, 
            wedgeprops=dict(width=0.4, edgecolor='w')
        )
        
        ax_pie.set_title(self.title, fontsize=14, fontweight='bold', pad=20)

        if self.is_not_to_scale:
            ax_pie.text(0, -self.radius - 0.3, "*Not to scale", ha='center', va='center', fontsize=10, color='red', alpha=0.7)

        table_data = [
            ["Total QSOs", f"{len(self.df)}"],
            ["Total Points", f"{total_points}"],
            ["Avg Pts/QSO", f"{total_points / len(self.df):.2f}" if len(self.df) > 0 else "0.00"]
        ]
        table = ax_table.table(cellText=table_data, colWidths=[0.4, 0.2], loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1.2, 1.2)

def save_debug_data(debug_flag: bool, output_path: str, data, custom_filename: str = None):
    """
    Saves the source data for a report to a .txt file if the debug flag is set.

    Args:
        debug_flag (bool): The value of the --debug-data flag.
        output_path (str): The original output path for the report (e.g., .../charts).
        data: The data to save (can be a pandas DataFrame or a dictionary).
        custom_filename (str, optional): A specific filename to use. Defaults to None.
    """
    if not debug_flag:
        return

    # Create the 'Debug' subdirectory inside the specific report output path
    debug_dir = Path(output_path) / "Debug"
    debug_dir.mkdir(parents=True, exist_ok=True)

    # Determine the output filename
    if custom_filename:
        filename = custom_filename
    else:
        # This part needs a bit of thought; assuming output_path is a directory
        # and we need a base name for the file. Let's construct one.
        # A more robust solution might require the original intended filename.
        # For now, let's create a generic name if no custom name is given.
        # This will be refined when each report is modified.
        filename = "debug_data.txt" # Placeholder, will be passed from report
    
    debug_filepath = debug_dir / filename

    # Format the data into a human-readable string
    content = ""
    if isinstance(data, pd.DataFrame):
        content = data.to_string()
    elif isinstance(data, dict):
        content = json.dumps(data, indent=4, cls=NpEncoder)
    else:
        content = str(data)

    # Write the formatted data to the debug file
    with open(debug_filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        logging.info(f"Debug data saved to {debug_filepath}")