# Contest Log Analyzer/contest_tools/reports/_report_utils.py
#
# Purpose: A utility module containing shared helper functions used by various
#          report generation scripts.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-05
# Version: 0.30.25-Beta
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
## [0.30.25-Beta] - 2025-08-05
### Changed
# - Rewrote `_create_pie_chart_subplot` to be a component factory that
#   returns a complete Figure object, fixing all layout and centering issues.
## [0.30.24-Beta] - 2025-08-05
### Fixed
# - Replaced GridSpec with a more flexible layout.
## [0.30.22-Beta] - 2025-08-05
### Fixed
# - Corrected filename and title generation for single-band contests.
## [0.30.21-Beta] - 2025-08-05
### Changed
# - Changed the pie chart color palette to "bright".
## [0.30.20-Beta] - 2025-08-05
### Fixed
# - Restored the `get_valid_dataframe` helper function.
## [0.30.19-Beta] - 2025-08-05
### Fixed
# - Restored the `create_output_directory` function.
## [0.30.15-Beta] - 2025-08-05
### Changed
# - Restored shared helper functions for plotting.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib.figure import Figure
import numpy as np
from ..contest_log import ContestLog

def create_output_directory(path: str):
    """
    Ensures that the specified output directory exists.
    """
    os.makedirs(path, exist_ok=True)

def get_valid_dataframe(log: ContestLog, include_dupes: bool = False) -> pd.DataFrame:
    """
    Returns the processed DataFrame from a ContestLog, optionally filtering out dupes.
    """
    df = log.get_processed_data()
    if not include_dupes:
        return df[df['Dupe'] == False].copy()
    return df.copy()

def _create_pie_chart_subplot(df, title, radius, is_not_to_scale=False) -> Figure:
    """
    Creates and returns a complete, self-contained Figure object for a single pie chart subplot.
    """
    fig = Figure(figsize=(7, 8))
    ax = fig.add_subplot(111)
    
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.axis('off')

    if df.empty or 'QSOPoints' not in df.columns or df['QSOPoints'].sum() == 0:
        ax.text(0.5, 0.5, "No Data", ha='center', va='center', fontsize=14, transform=ax.transAxes)
        return fig

    point_counts = df['QSOPoints'].value_counts().sort_index(ascending=False)
    
    colors = sns.color_palette("bright", len(point_counts))
    wedges, texts, autotexts = ax.pie(
        point_counts,
        labels=[f"{idx} pts" for idx in point_counts.index],
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        radius=radius,
        pctdistance=0.85,
        center=(0.5, 0.55) # Adjusted center for better vertical alignment
    )

    plt.setp(autotexts, size=10, weight="bold", color="white")

    if is_not_to_scale:
        ax.text(0.5, 0.55 - radius - 0.1, "(not to scale)", ha='center', va='center', fontsize=10, style='italic', transform=ax.transAxes)

    total_points = df['QSOPoints'].sum()
    total_qsos = len(df)
    avg_points = total_points / total_qsos if total_qsos > 0 else 0
    
    table_data = [
        ["Total QSOs", f"{total_qsos:,}"],
        ["Total Points", f"{total_points:,}"],
        ["Avg Points/QSO", f"{avg_points:.2f}"]
    ]
    table = ax.table(
        cellText=table_data, 
        colLabels=None, 
        cellLoc='center', 
        loc='bottom',
        bbox=[0.1, 0.05, 0.8, 0.2]
    )
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 1.5)

    return fig

def _create_cumulative_rate_plot(logs, output_path, band_filter, metric_name, value_column, agg_func, report_id):
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.set_theme(style="whitegrid")

    all_calls = []
    summary_data = []

    for log in logs:
        call = log.get_metadata().get('MyCall', 'Unknown')
        all_calls.append(call)
        df = get_valid_dataframe(log)

        if band_filter != "All":
            df = df[df['Band'] == band_filter]
        
        if df.empty or value_column not in df.columns:
            continue
        
        df_cleaned = df.dropna(subset=['Datetime', value_column]).set_index('Datetime')
        df_cleaned.index = df_cleaned.index.tz_localize('UTC')
        
        hourly_rate = df_cleaned.resample('h')[value_column].agg(agg_func)
        cumulative_rate = hourly_rate.cumsum()
        
        master_time_index = log._log_manager_ref.master_time_index
        if master_time_index is not None:
            cumulative_rate = cumulative_rate.reindex(master_time_index, method='pad').fillna(0)
        
        ax.plot(cumulative_rate.index, cumulative_rate.values, marker='o', linestyle='-', markersize=4, label=call)

        if metric_name == "Points":
            total_value = df[value_column].sum()
        else:
            total_value = len(df)

        summary_data.append([
            call,
            f"{total_value:,}",
            f"{(df['Run'] == 'Run').sum():,}",
            f"{(df['Run'] == 'S&P').sum():,}",
            f"{(df['Run'] == 'Unknown').sum():,}"
        ])

    metadata = logs[0].get_metadata()
    year = get_valid_dataframe(logs[0])['Date'].dropna().iloc[0].split('-')[0] if not get_valid_dataframe(logs[0]).empty and not get_valid_dataframe(logs[0])['Date'].dropna().empty else "----"
    contest_name = metadata.get('ContestName', '')
    event_id = metadata.get('EventID', '')
    
    is_single_band = len(logs[0].contest_definition.valid_bands) == 1
    band_text = logs[0].contest_definition.valid_bands[0].replace('M', ' Meters') if is_single_band else band_filter.replace('M', ' Meters')
    
    title_line1 = f"{event_id} {year} {contest_name}".strip()
    title_line2 = f"Cumulative {metric_name} ({band_text})"
    
    ax.set_title(f"{title_line1}\n{title_line2}", fontsize=16, fontweight='bold')
    ax.set_xlabel("Contest Time")
    ax.set_ylabel(f"Cumulative {metric_name}")
    ax.legend(loc='upper left')
    ax.grid(True, which='both', linestyle='--')
    
    if summary_data:
        col_labels = ["Call", f"Total {metric_name}", "Run", "S&P", "Unk"]
        table = ax.table(cellText=summary_data, colLabels=col_labels, loc='lower right', cellLoc='center', colLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(0.7, 1.2)
        table.set_zorder(10)
        
        for key, cell in table.get_celld().items():
            cell.set_facecolor('white')

    fig.tight_layout()
    create_output_directory(output_path)
    
    filename_band = logs[0].contest_definition.valid_bands[0].lower() if is_single_band else band_filter.lower().replace('m', '')
    filename_calls = '_vs_'.join(sorted(all_calls))
    filename = f"{report_id}_{filename_band}_{filename_calls}.png"
    filepath = os.path.join(output_path, filename)
    fig.savefig(filepath)
    plt.close(fig)
    return filepath