# Contest Log Analyzer/contest_tools/reports/_report_utils.py
#
# Purpose: A utility module providing shared helper functions for the
#          reporting engine.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-22
# Version: 0.47.1-Beta
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
## [0.47.1-Beta] - 2025-08-22
### Changed
# - Enhanced the calculate_multiplier_pivot() shared utility to support
#   an optional 'group_by_call' parameter, making it flexible enough for
#   both score and multiplier summary reports.
## [0.47.0-Beta] - 2025-08-22
### Added
# - Added the calculate_multiplier_pivot() shared utility function to
#   centralize the core multiplier counting logic for all reports.
## [0.46.1-Beta] - 2025-08-21
### Changed
# - Changed the colormap for the ComparativeHeatmapChart from 'viridis'
#   to 'hot' to match user preference and other heatmap reports.
## [0.46.0-Beta] - 2025-08-19
### Fixed
# - Modified the figsize calculation to enforce a minimum height,
#   preventing chart elements from overlapping on single-band plots.
## [0.45.0-Beta] - 2025-08-19
### Fixed
# - Replaced the layout manager with an explicit GridSpec to create a
#   dedicated, reserved space for the legend, ensuring it is centered
#   and does not overlap the title or chart.
## [0.44.0-Beta] - 2025-08-19
### Fixed
# - Corrected the legend's vertical and horizontal placement to ensure it
#   is centered and does not overlap the plot title.
## [0.43.0-Beta] - 2025-08-19
### Changed
# - Adjusted the figure aspect ratio to be taller (11 x 8.5) for better
#   readability and printing.
# - Reworked the legend to use a sample color from the heatmap's actual
#   color scale, with and without the dot pattern, to be more intuitive.
# - Implemented the standard two-line figure suptitle.
# - Changed the thin horizontal cell divider to a black line.
## [0.42.0-Beta] - 2025-08-19
### Changed
# - Adjusted the figure aspect ratio to be taller (11 x 8.5) for better
#   readability and printing.
# - Reworked the legend to use a sample color from the heatmap's actual
#   color scale, with and without the dot pattern, to be more intuitive.
## [0.41.0-Beta] - 2025-08-19
### Changed
# - Modified the ComparativeHeatmapChart to use a truncated Viridis
#   colormap, excluding the darkest colors.
# - Added a white dot hatch pattern to the cells for the second log to
#   improve visual distinction.
# - Changed the primary horizontal grid lines between bands to be heavy,
#   black, and drawn in the foreground.
## [0.40.0-Beta] - 2025-08-19
### Changed
# - Enhanced the ComparativeHeatmapChart plotting logic to dynamically
#   calculate and render correct, time-based labels for the x-axis,
#   resolving the axis formatting bug.
## [0.39.9-Beta] - 2025-08-19
### Changed
# - Rewrote the ComparativeHeatmapChart plotting logic to manually draw
#   a custom grid with thick and thin lines, per user specification,
#   to improve chart readability.
## [0.39.8-Beta] - 2025-08-19
### Changed
# - Renamed SplitHeatmapChart to ComparativeHeatmapChart and rewrote its
#   plotting logic to correctly generate a split-cell heatmap instead of
#   a butterfly chart, resolving a major implementation bug.
## [0.39.7-Beta] - 2025-08-19
### Fixed
# - Corrected the SplitHeatmapChart plotter to fix a UserWarning by
#   setting y-tick locations before labels.
# - Removed dead code from the SplitHeatmapChart plotter that was
#   causing a TypeError due to a namespace collision.
## [0.39.6-Beta] - 2025-08-18
### Added
# - Added the SplitHeatmapChart reusable plotting class to generate
#   comparative, split-cell heatmap visualizations.
## [0.39.5-Beta] - 2025-08-18
### Fixed
# - Resolved a pandas SettingWithCopyWarning by explicitly returning a
#   .copy() of the DataFrame slice in the get_valid_dataframe helper.
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
from matplotlib.patches import Rectangle
from matplotlib.colors import Normalize, ListedColormap
import os
import numpy as np
import re
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
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
    """Returns a safe copy of the log's DataFrame, excluding dupes unless specified."""
    df = log.get_processed_data()
    df_slice = df if include_dupes else df[df['Dupe'] == False]
    return df_slice.copy()

def create_output_directory(path: str):
    """Creates the output directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)

def _sanitize_filename_part(part: str) -> str:
    """Sanitizes a string to be used as part of a filename."""
    return re.sub(r'[\s/\\:]+', '_', part.lower())

def calculate_multiplier_pivot(df: pd.DataFrame, mult_col: str, group_by_call: bool = False) -> pd.DataFrame:
    """
    Creates an authoritative pivot table for a given multiplier column.
    This is the single source of truth for multiplier counting.
    """
    if df.empty or mult_col not in df.columns:
        return pd.DataFrame()
    
    index_cols = [mult_col]
    if group_by_call and 'MyCall' in df.columns:
        index_cols.append('MyCall')
    
    return df.pivot_table(index=index_cols, columns='Band', aggfunc='size', fill_value=0)

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

class ComparativeHeatmapChart:
    """Helper class to generate a 'split cell' comparative heatmap."""
    
    def __init__(self, data1, data2, call1, call2, metadata: Dict[str, Any], output_filename: str, part_info: str = ""):
        self.data1 = data1
        self.data2 = data2
        self.call1 = call1
        self.call2 = call2
        self.metadata = metadata
        self.output_filename = output_filename
        self.part_info = part_info

    def plot(self):
        """Generates and saves the heatmap plot."""
        bands = self.data1.index
        num_bands = len(bands)
        num_cols = len(self.data1.columns)
        
        # Enforce a minimum height for single-band plots
        height = max(6.0, 1 + num_bands * 1.2)
        fig = plt.figure(figsize=(11, height))
        
        # --- Explicit Layout Control using GridSpec ---
        gs = fig.add_gridspec(2, 1, height_ratios=[1, 15], hspace=0.05)
        ax_legend = fig.add_subplot(gs[0])
        ax = fig.add_subplot(gs[1])
        ax_legend.axis('off')


        max_val = max(self.data1.max().max(), self.data2.max().max())
        norm = Normalize(vmin=0, vmax=max_val)
        
        base_cmap = plt.get_cmap('hot')
        cmap_colors = base_cmap(np.linspace(0.1, 1.0, 256)) 
        cmap = ListedColormap(cmap_colors)

        # --- Stage 1: Draw filled rectangles ---
        for band_idx, band in enumerate(bands):
            for time_idx in range(num_cols):
                qso_count1 = self.data1.iloc[band_idx, time_idx]
                qso_count2 = self.data2.iloc[band_idx, time_idx]

                if qso_count1 > 0:
                    ax.add_patch(Rectangle((time_idx, band_idx + 0.5), 1, 0.5, facecolor=cmap(norm(qso_count1)), edgecolor='none'))
                
                if qso_count2 > 0:
                    ax.add_patch(Rectangle((time_idx, band_idx), 1, 0.5, facecolor=cmap(norm(qso_count2)), edgecolor='white', hatch='..'))

        # --- Stage 2: Manually draw custom grid lines ---
        for time_idx in range(num_cols + 1):
            ax.axvline(time_idx, color='white', linewidth=1.5)
        
        for band_idx in range(num_bands):
            ax.axhline(band_idx + 0.5, color='black', linewidth=0.75)
            
        for band_idx in range(num_bands + 1):
            ax.axhline(band_idx, color='black', linewidth=2.0, zorder=10)

        # --- Formatting ---
        ax.set_xlim(0, num_cols)
        ax.set_ylim(0, num_bands)
        ax.set_yticks(np.arange(num_bands) + 0.5)
        ax.set_yticklabels(bands)
        
        min_time = self.data1.columns[0]
        max_time = self.data1.columns[-1]
        contest_duration_hours = (max_time - min_time).total_seconds() / 3600
        
        if contest_duration_hours <= 12:
            hour_interval = 2
            date_format_str = '%H:%M'
        else:
            hour_interval = 3
            date_format_str = '%H:%M'
            
        tick_step = hour_interval * 4
        tick_positions = np.arange(0.5, num_cols, tick_step)
        tick_labels = [self.data1.columns[int(i)].strftime(date_format_str) for i in tick_positions]
        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels, rotation=45, ha='right')
        
        ax.set_xlabel("Contest Time (UTC)")
        
        # --- Standard Title and Legend ---
        year = self.metadata.get('Year', '')
        contest_name = self.metadata.get('ContestName', '')
        event_id = self.metadata.get('EventID', '')
        
        title_line1 = f"{event_id} {year} {contest_name}".strip()
        title_line2 = f"Comparative Band Activity Heatmap {self.part_info}".strip()
        fig.suptitle(f"{title_line1}\n{title_line2}", fontsize=16, fontweight='bold', y=0.99)
        
        medium_color = cmap(0.5)
        legend_patches = [
            Rectangle((0, 0), 1, 1, facecolor=medium_color, label=self.call1),
            Rectangle((0, 0), 1, 1, facecolor=medium_color, hatch='..', edgecolor='white', label=self.call2),
        ]
        ax_legend.legend(handles=legend_patches, loc='center', ncol=2, frameon=False)

        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, aspect=40, pad=0.02)
        cbar.set_label('QSOs / 15 min')
        
        try:
            fig.savefig(self.output_filename)
            plt.close(fig)
            return self.output_filename
        except Exception as e:
            logging.error(f"Error saving split heatmap: {e}")
            plt.close(fig)
            return None

def save_debug_data(debug_flag: bool, output_path: str, data, custom_filename: str = None):
    """
    Saves the source data for a report to a .txt file if the debug flag is set.
    """
    if not debug_flag:
        return

    debug_dir = Path(output_path) / "Debug"
    debug_dir.mkdir(parents=True, exist_ok=True)

    if custom_filename:
        filename = custom_filename
    else:
        filename = "debug_data.txt" 
    
    debug_filepath = debug_dir / filename

    content = ""
    if isinstance(data, pd.DataFrame):
        content = data.to_string()
    elif isinstance(data, dict):
        content = json.dumps(data, indent=4, cls=NpEncoder)
    else:
        content = str(data)

    with open(debug_filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        logging.info(f"Debug data saved to {debug_filepath}")