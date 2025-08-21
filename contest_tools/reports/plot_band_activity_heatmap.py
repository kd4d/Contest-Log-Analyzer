# Contest Log Analyzer/contest_tools/reports/plot_band_activity_heatmap.py
#
# Version: 0.39.7-Beta
# Date: 2025-08-21
#
# Purpose: A plot report that generates a heatmap of band activity over time.
#
# --- Revision History ---
## [0.39.7-Beta] - 2025-08-21
### Changed
# - Changed the colormap from 'viridis' to 'hot' to provide a more
#   traditional and intuitive color scheme for the heatmap.
## [0.39.6-Beta] - 2025-08-18
### Changed
# - Modified the heatmap plot to use a mask, rendering zero-QSO intervals
#   as white to improve readability and highlight band activity.
## [0.39.5-Beta] - 2025-08-18
### Fixed
# - Resolved the empty heatmap bug by localizing the Datetime column to
#   UTC before performing time-based operations, fixing a timezone-
#   naive vs. timezone-aware conflict.
## [0.39.4-Beta] - 2025-08-18
### Added
# - Integrated the --debug-data flag functionality to save the report's
#   source data matrix to a text file.
## [0.39.3-Beta] - 2025-08-18
### Fixed
# - Replaced the automatic matplotlib date locator with a manual calculation
#   for tick positions and labels in the heatmap report. This resolves
#   the "Locator attempting to generate too many ticks" warning.
## [0.39.2-Beta] - 2025-08-18
# - Initial release of the Band Activity Heatmap report.
#
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

            df['Datetime'] = df['Datetime'].dt.tz_localize('UTC')

            # --- 1. Data Preparation ---
            interval = '15min'
            min_time = df['Datetime'].min().floor('h')
            max_time = df['Datetime'].max().ceil('h')
            
            pivot_df = df.pivot_table(
                index='Band',
                columns=pd.Grouper(key='Datetime', freq=interval),
                aggfunc='size',
                fill_value=0
            )
            
            all_bands = log.contest_definition.valid_bands
            canonical_band_order_tuples = ContestLog._HF_BANDS
            canonical_band_order = [band[1] for band in canonical_band_order_tuples]
            sorted_bands = sorted(all_bands, key=lambda b: canonical_band_order.index(b) if b in canonical_band_order else -1)
            time_bins = pd.date_range(start=min_time, end=max_time, freq=interval, tz='UTC')
            
            pivot_df = pivot_df.reindex(index=sorted_bands, columns=time_bins, fill_value=0)

            # --- 2. Dynamic Axis Formatting (Manual Calculation) ---
            num_columns = len(pivot_df.columns)
            contest_duration_hours = (max_time - min_time).total_seconds() / 3600

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
            
            ax.set_title(f"{self.report_name} for {callsign}\n{contest_name}", fontsize=16, fontweight='bold')
            ax.set_xlabel("Contest Time (UTC)")
            ax.set_ylabel("Band")
            
            ax.set_xticks(tick_positions)
            ax.set_xticklabels(tick_labels, rotation=45, ha='right')
            
            fig.tight_layout()
            
            # --- Save Debug Data ---
            debug_filename = f"{self.report_id}_{callsign}.txt"
            save_debug_data(debug_data_flag, output_path, pivot_df, custom_filename=debug_filename)

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