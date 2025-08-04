# Contest Log Analyzer/contest_tools/reports/_report_utils.py
#
# Purpose: A utility module containing shared helper functions used by various
#          report generation scripts.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-04
# Version: 0.28.5-Beta
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
## [0.28.5-Beta] - 2025-08-04
### Fixed
# - Corrected the subplot creation logic in `_create_pie_chart_subplot` to
#   use the modern, compatible method, fixing the 'subplot_spec' TypeError.
## [0.28.4-Beta] - 2025-08-04
### Changed
# - Reduced the width of the inset summary table in cumulative rate plots by
#   approximately 20% to improve visual balance.
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
from matplotlib.gridspec import GridSpec
import numpy as np
from typing import Dict, Tuple, Optional

class AliasLookup:
    """
    Parses a standard multiplier alias file (e.g., NAQPmults.dat) and provides
    a lookup method to resolve aliases to their official abbreviation and full name.
    """
    def __init__(self, data_dir_path: str, alias_filename: str):
        self.filepath = os.path.join(data_dir_path, alias_filename)
        self._lookup: Dict[str, Tuple[str, str]] = {}
        self._valid_mults: set = set()
        self._parse_file()

    def _parse_file(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split(':')
                    if len(parts) != 2:
                        continue
                        
                    aliases_part, official_part = parts[0], parts[1]
                    aliases = [alias.strip().upper() for alias in aliases_part.split(',')]
                    
                    match = re.match(r'([A-Z0-9]{1,4})\s+\((.*)\)', official_part.strip())
                    if not match:
                        continue
                    
                    official_abbr = match.group(1).upper()
                    full_name = match.group(2)
                    
                    self._valid_mults.add(official_abbr)
                    for alias in aliases:
                        self._lookup[alias] = (official_abbr, full_name)
        except FileNotFoundError:
            print(f"Warning: Multiplier alias file not found at {self.filepath}. Alias lookup will be disabled.")
        except Exception as e:
            print(f"Error reading multiplier alias file {self.filepath}: {e}")

    def get_multiplier(self, value: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Looks up an alias and returns the official multiplier abbreviation and full name.
        """
        if not isinstance(value, str):
            return pd.NA, pd.NA
            
        value_upper = value.upper()
        if value_upper in self._lookup:
            return self._lookup[value_upper]
        
        if value_upper in self._valid_mults:
            for abbr, (official_abbr, full_name) in self._lookup.items():
                if value_upper == official_abbr:
                    return official_abbr, full_name

        return pd.NA, pd.NA

def _create_pie_chart_subplot(fig, gs, df, title, radius, is_not_to_scale=False):
    """
    Creates a single pie chart subplot with a title, data table, and proportional radius.
    """
    nested_gs = gs.subgridspec(2, 1, height_ratios=[0.7, 0.3])
    ax_pie = fig.add_subplot(nested_gs[0])
    ax_table = fig.add_subplot(nested_gs[1])


    ax_pie.set_title(title, fontsize=16, fontweight='bold')
    
    if df.empty or 'QSOPoints' not in df.columns or df['QSOPoints'].sum() == 0:
        ax_pie.text(0.5, 0.5, "No Data", ha='center', va='center', fontsize=14)
        ax_pie.axis('off')
        ax_table.axis('off')
        return

    point_counts = df['QSOPoints'].value_counts().sort_index(ascending=False)
    
    colors = sns.color_palette("viridis", len(point_counts))
    wedges, texts, autotexts = ax_pie.pie(
        point_counts,
        labels=[f"{idx} pts" for idx in point_counts.index],
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        radius=radius,
        pctdistance=0.85
    )

    plt.setp(autotexts, size=10, weight="bold", color="white")
    ax_pie.axis('equal')

    if is_not_to_scale:
        ax_pie.text(0, -radius - 0.2, "(not to scale)", ha='center', va='center', fontsize=10, style='italic')

    # --- Table ---
    ax_table.axis('off')
    total_points = df['QSOPoints'].sum()
    total_qsos = len(df)
    avg_points = total_points / total_qsos if total_qsos > 0 else 0
    
    table_data = [
        ["Total QSOs", f"{total_qsos:,}"],
        ["Total Points", f"{total_points:,}"],
        ["Avg Points/QSO", f"{avg_points:.2f}"]
    ]
    table = ax_table.table(cellText=table_data, colLabels=None, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 1.5)

def _create_cumulative_rate_plot(logs, output_path, band_filter, metric_name, value_column, agg_func, report_id):
    """
    Shared helper function to create a cumulative QSO or Point rate plot.
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.set_theme(style="whitegrid")

    all_calls = []
    summary_data = []

    for log in logs:
        call = log.get_metadata().get('MyCall', 'Unknown')
        all_calls.append(call)
        df = log.get_processed_data()[log.get_processed_data()['Dupe'] == False]

        if band_filter != "All":
            df = df[df['Band'] == band_filter]
        
        if df.empty or value_column not in df.columns:
            continue
        
        df_cleaned = df.dropna(subset=['Datetime', value_column])
        
        hourly_rate = df_cleaned.groupby(df_cleaned['Datetime'].dt.floor('h'))[value_column].agg(agg_func)
        cumulative_rate = hourly_rate.cumsum()
        
        if not hourly_rate.empty:
            full_timeline = pd.date_range(start=hourly_rate.index.min(), end=hourly_rate.index.max(), freq='h')
            cumulative_rate = cumulative_rate.reindex(full_timeline, method='pad').fillna(0)
        
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

    contest_name = logs[0].get_metadata().get('ContestName', '')
    year = logs[0].get_processed_data()['Date'].dropna().iloc[0].split('-')[0] if not logs[0].get_processed_data().empty and not logs[0].get_processed_data()['Date'].dropna().empty else "----"
    band_text = "All Bands" if band_filter == "All" else f"{band_filter.replace('M', '')} Meters"
    
    ax.set_title(f"{year} {contest_name} - Cumulative {metric_name} ({band_text})", fontsize=16, fontweight='bold')
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
    os.makedirs(output_path, exist_ok=True)
    
    filename_band = band_filter.lower().replace('m', '')
    filename = f"{report_id}_{filename_band}_plot.png"
    filepath = os.path.join(output_path, filename)
    fig.savefig(filepath)
    plt.close(fig)
    return filepath