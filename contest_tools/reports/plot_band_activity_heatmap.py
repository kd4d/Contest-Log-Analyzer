# contest_tools/reports/plot_band_activity_heatmap.py
#
# Purpose: A plot report that generates a heatmap of band activity over time.
#
# Author: Gemini AI
# Date: 2025-11-24
# Version: 1.0.0
#
# Copyright (c) 2025 Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0.
# If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# --- Revision History ---
# [1.0.0] - 2025-11-24
# Refactored to use MatrixAggregator (DAL) for data generation.
# [0.90.0-Beta] - 2025-10-01
# Set new baseline version for release.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import os
import logging
from typing import List, Dict, Any

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import get_valid_dataframe, create_output_directory, save_debug_data
from ..data_aggregators.matrix_stats import MatrixAggregator

class Report(ContestReport):
    """
    Generates a heatmap of band activity over the duration of the contest.
    """
    report_id: str = "band_activity_heatmap"
    report_name: str = "Band Activity Heatmap"
    report_type: str = "plot"
    supports_single = True

    def generate(self, output_path: str, **kwargs) -> str:
        """Generates the report content."""
        final_report_messages = []
        debug_data_flag = kwargs.get("debug_data", False)

        for log in self.logs:
            metadata = log.get_metadata()
            df_full = log.get_processed_data()
            callsign = metadata.get('MyCall', 'UnknownCall')
            contest_name = metadata.get('ContestName', 'UnknownContest')
            
            df = get_valid_dataframe(log, include_dupes=False)
            
            if df.empty or 'Datetime' not in df.columns or df['Datetime'].isna().all():
                msg = f"Skipping report for {callsign}: No valid QSOs with timestamps to report."
                final_report_messages.append(msg)
                continue

            # --- 1. Data Aggregation (DAL) ---
            aggregator = MatrixAggregator([log])
            matrix_data = aggregator.get_matrix_data(bin_size='15min')
            
            # Unpack DAL data
            time_bins_str = matrix_data['time_bins']
            sorted_bands = matrix_data['bands']
            
            if not time_bins_str or not sorted_bands:
                 msg = f"Skipping report for {callsign}: No matrix data generated."
                 final_report_messages.append(msg)
                 continue

            qso_grid = matrix_data['logs'][callsign]['qso_counts']

            # Reconstruct DataFrame for Seaborn (Presentation Layer)
            time_index = pd.to_datetime(time_bins_str)
            pivot_df = pd.DataFrame(qso_grid, index=sorted_bands, columns=time_index)

            # --- 2. Dynamic Axis Formatting ---
            num_columns = len(pivot_df.columns)
            if not time_index.empty:
                contest_duration_hours = (time_index[-1] - time_index[0]).total_seconds() / 3600
            else:
                contest_duration_hours = 0

            if contest_duration_hours <= 12:
                hour_interval = 2
                date_format_str = '%H:%M'
            elif contest_duration_hours <= 24:
                hour_interval = 3
                date_format_str = '%H:%M'
            else: 
                hour_interval = 4
                date_format_str = '%d-%H%M'

            tick_step = hour_interval * 4 
            tick_positions = np.arange(0.5, num_columns, tick_step)
            tick_labels = [pivot_df.columns[int(i)].strftime(date_format_str) for i in tick_positions]

            # --- 3. Visualization ---
            fig, ax = plt.subplots(figsize=(12, 8))
            
            mask = pivot_df == 0
            
            sns.heatmap(
                pivot_df,
                ax=ax,
                mask=mask,
                cmap="hot",
                cbar=True,
                cbar_kws={'label': 'QSOs / 15 min'},
                linewidths=.5
            )
            
            # --- Standard Two-Line Title ---
            year = df_full['Date'].dropna().iloc[0].split('-')[0] if not df_full.empty and not df_full['Date'].dropna().empty else "----"
            event_id = metadata.get('EventID', '')
            
            title_line1 = self.report_name
            title_line2 = f"{year} {contest_name} {event_id} - {callsign}".strip()
            final_title = f"{title_line1}\n{title_line2}"
            ax.set_title(final_title, fontsize=16, fontweight='bold')

            ax.set_xlabel("Contest Time (UTC)")
            ax.set_ylabel("Band")
            
            ax.set_xticks(tick_positions)
            ax.set_xticklabels(tick_labels, rotation=45, ha='right')
            
            fig.tight_layout()
            
            # --- Save Debug Data ---
            debug_filename = f"{self.report_id}_{callsign}.txt"
            save_debug_data(debug_data_flag, output_path, matrix_data, custom_filename=debug_filename)

            # --- Save File ---
            create_output_directory(output_path)
            filename = f"{self.report_id}_{callsign}.png"
            filepath = os.path.join(output_path, filename)
            
            try:
                fig.savefig(filepath)
                plt.close(fig)
                final_report_messages.append(f"Plot report saved to: {filepath}")
            except Exception as e:
                logging.error(f"Error saving heatmap for {callsign}: {e}")
                plt.close(fig)
                final_report_messages.append(f"Error generating report '{self.report_name}' for {callsign}")

        return "\n".join(final_report_messages)