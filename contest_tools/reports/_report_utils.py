# Contest Log Analyzer/contest_tools/reports/_report_utils.py
#
# Purpose: A helper module with shared, reusable logic for report generation,
#          primarily for aligning time-series data from multiple logs.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-03
# Version: 0.28.11-Beta
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
## [0.28.11-Beta] - 2025-08-03
### Fixed
# - Explicitly set the `zorder` of the inset summary table to ensure it
#   is rendered on top of the plot's grid lines.
#
## [0.28.10-Beta] - 2025-08-03
### Fixed
# - The background color of the inset summary table in rate plots now
#   dynamically matches the plot's background color instead of being
#   hardcoded to white.
#
## [0.28.9-Beta] - 2025-08-03
### Changed
# - The inset summary table in rate plots is now opaque with a white
#   background to cover the grid lines, improving readability.
#
## [0.28.1-Beta] - 2025-08-02
### Added
# - Added a new shared helper function, _create_cumulative_rate_plot, to
#   encapsulate all logic for generating QSO and Point rate plots.
# - The inset summary table in rate plots is now opaque with a white
#   background to cover the grid lines.
# - The Point Rate plot now correctly includes the summary table.
## [0.26.3-Beta] - 2025-08-02
### Fixed
# - Corrected a time alignment bug by resampling pivot tables to an hourly
#   frequency before reindexing against the master time index.
from typing import List, Dict
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import seaborn as sns
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
        
        df['Datetime'] = pd.to_datetime(df['Datetime'], utc=True)

        pt = df.pivot_table(
            index=df['Datetime'].dt.floor(time_unit), 
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
        pt_resampled = pt.resample('h').sum()
        aligned_logs[callsign] = pt_resampled.reindex(master_index, fill_value=0)

    return aligned_logs

def _create_pie_chart_subplot(fig: plt.Figure, gs: GridSpec, band_df: pd.DataFrame, title: str, radius: float, is_not_to_scale: bool):
    """
    Generates a single pie chart "widget" within a given GridSpec.
    """
    nested_gs = gs.subgridspec(3, 1, height_ratios=[0.5, 3, 1.5])

    ax_title = fig.add_subplot(nested_gs[0, 0])
    ax_title.text(0.5, 0.5, title, ha='center', va='center', fontweight='bold', fontsize=16)
    ax_title.axis('off')

    ax_pie = fig.add_subplot(nested_gs[1, 0])
    if band_df.empty or 'QSOPoints' not in band_df.columns or band_df['QSOPoints'].sum() == 0:
        ax_pie.text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=12)
        ax_pie.axis('off')
        ax_table = fig.add_subplot(nested_gs[2, 0])
        ax_table.axis('off')
        return

    point_summary = band_df.groupby('QSOPoints').agg(
        QSOs=('Call', 'count')
    ).reset_index()
    point_summary['Points'] = point_summary['QSOPoints'] * point_summary['QSOs']
    
    pie_chart_data = point_summary[point_summary['QSOPoints'] > 0]
    
    pie_data = pie_chart_data.set_index('QSOPoints')['Points']
    labels = [f"{idx} Pts" for idx in pie_data.index]
    
    wedges, texts = ax_pie.pie(pie_data, labels=labels, autopct=None,
                               startangle=90, counterclock=False, radius=radius,
                               textprops={'fontsize': 12, 'fontweight': 'bold'})
    
    ax_pie.set_aspect('equal')

    if is_not_to_scale:
        ax_pie.text(0.5, 0.0, "*NOT TO SCALE*", ha='center', va='center',
                    transform=ax_pie.transAxes, fontsize=12, fontweight='bold')

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

def _create_cumulative_rate_plot(
    logs: List[ContestLog],
    output_path: str,
    master_index: pd.DatetimeIndex,
    band_filter: str,
    metric_name: str,
    value_column: str,
    agg_func: str,
    report_id: str
) -> str:
    """
    Generic helper to create a cumulative rate plot for QSOs or Points.
    """
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(12, 7))

    aligned_data = align_logs_by_time(
        logs=logs,
        value_column=value_column,
        agg_func=agg_func,
        master_index=master_index,
        band_filter=band_filter,
        time_unit='10min'
    )
    
    if not aligned_data:
        print(f"  - Skipping {band_filter} {metric_name} rate plot: no logs have QSOs on this band.")
        return None

    summary_data = []
    row_labels = []
    for callsign, df_aligned in aligned_data.items():
        cumulative_metric = df_aligned['Overall'].cumsum()
        ax.plot(cumulative_metric.index, cumulative_metric, marker='o', linestyle='-', markersize=4, label=callsign)
        
        row_labels.append(callsign)
        summary_data.append([
            int(df_aligned['Overall'].sum()),
            int(df_aligned['Run'].sum()),
            int(df_aligned['S&P'].sum()),
            int(df_aligned['Unknown'].sum())
        ])

    first_log_meta = logs[0].get_metadata()
    contest_name = first_log_meta.get('ContestName', '')
    year = logs[0].get_processed_data()['Date'].iloc[0].split('-')[0]
    
    main_title = f"{year} {contest_name} {metric_name} Rate Comparison"
    band_text = "All Bands" if band_filter == "All" else f"{band_filter.replace('M', '')} Meters"
    sub_title = f"{band_text} - (Does Not Include Dupes)"

    fig.suptitle(main_title, fontsize=16, fontweight='bold')
    ax.set_title(sub_title, fontsize=12)
    
    ax.set_xlabel("Contest Time")
    ax.set_ylabel(f"Total {metric_name}")
    ax.legend()
    ax.grid(True)
    
    col_labels = ['Total', 'Run', 'S&P', 'Unk']
    table = ax.table(cellText=summary_data,
                        rowLabels=row_labels,
                        colLabels=col_labels,
                        loc='lower right',
                        cellLoc='center',
                        bbox=[0.75, 0.05, 0.2, 0.25],
                        zorder=10)
    
    # --- FIX: Make table opaque and ensure it's on top of the grid ---
    plot_bg_color = ax.get_facecolor()
    table.set_alpha(1.0)
    for key, cell in table.get_celld().items():
        cell.set_facecolor(plot_bg_color)

    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

    os.makedirs(output_path, exist_ok=True)
    filename_band = band_filter.lower().replace('m', '')
    filename = f"{report_id}_{filename_band}_plot.png"
    filepath = os.path.join(output_path, filename)
    fig.savefig(filepath)
    plt.close(fig)

    return filepath