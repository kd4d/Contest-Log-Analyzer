# Contest Log Analyzer/contest_tools/reports/_plot_utils.py
#
# Purpose: A helper module with shared logic for generating rate plots.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-22
# Version: 0.14.0-Beta
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

## [0.14.0-Beta] - 2025-07-22
# - Initial release of the plot utilities helper module.

from typing import List, Optional
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

from ..contest_log import ContestLog

def generate_rate_plot(
    logs: List[ContestLog],
    output_path: str,
    band_filter: str,
    value_column: Optional[str],
    main_title_verb: str,
    y_axis_label: str,
    filename_prefix: str,
    include_dupes: bool = False
) -> str:
    """
    Generates a single rate plot for a specific metric (QSOs or Points).

    Args:
        logs (List[ContestLog]): The list of logs to plot.
        output_path (str): The directory to save the plot file.
        band_filter (str): The band to filter for (e.g., '20M', or 'All').
        value_column (Optional[str]): The column to sum for the rate. If None,
                                      the size of each group (QSO count) is used.
        main_title_verb (str): The verb for the main title (e.g., "QSO Rate").
        y_axis_label (str): The label for the Y-axis.
        filename_prefix (str): The prefix for the output PNG file.
        include_dupes (bool): Whether to include dupes in the calculation.

    Returns:
        str: The full path to the generated plot file.
    """
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(12, 7))

    first_log_meta = logs[0].get_metadata()
    contest_name = first_log_meta.get('ContestName', '')
    first_qso_date = logs[0].get_processed_data()['Date'].iloc[0]
    year = first_qso_date.split('-')[0] if first_qso_date else ""

    for log in logs:
        callsign = log.get_metadata().get('MyCall', 'Unknown')
        df_full = log.get_processed_data()
        
        df_band = df_full[df_full['Band'] == band_filter].copy() if band_filter != "All" else df_full.copy()

        if not include_dupes and 'Dupe' in df_band.columns:
            df = df_band[df_band['Dupe'] == False].copy()
        else:
            df = df_band.copy()
        
        if df.empty or (value_column and value_column not in df.columns):
            continue

        resampler = df.set_index('Datetime')
        if value_column:
            rate = resampler[value_column].resample('1min').sum()
        else:
            rate = resampler.resample('1min').size()

        cumulative_values = rate.cumsum()
        hourly_data = cumulative_values.resample('1h').last().dropna()
        
        ax.plot(hourly_data.index, hourly_data, marker='o', linestyle='-', markersize=5, label=f'{callsign}')

    main_title = f"{year} {contest_name} {main_title_verb} Comparison"
    band_text = "All Bands" if band_filter == "All" else f"{band_filter.replace('M', '')} Meters"
    dupe_text = "(Includes Dupes)" if include_dupes else "(Does Not Include Dupes)"
    sub_title = f"{band_text} - {dupe_text}"

    fig.suptitle(main_title, fontsize=16, fontweight='bold')
    ax.set_title(sub_title, fontsize=12)
    
    ax.set_xlabel("Contest Time")
    ax.set_ylabel(y_axis_label)
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    
    os.makedirs(output_path, exist_ok=True)
    
    filename_band = band_filter.lower().replace('m', '')
    filename = f"{filename_prefix}_{filename_band}_plot.png"
    filepath = os.path.join(output_path, filename)
    fig.savefig(filepath)
    plt.close(fig)

    return filepath
