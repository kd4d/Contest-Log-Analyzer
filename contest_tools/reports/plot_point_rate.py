# Contest Log Analyzer/contest_tools/reports/plot_point_rate.py
#
# Purpose: A plot report that generates a point rate graph for all bands
#          and for each individual band.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-10
# Version: 0.31.26-Beta
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
## [0.31.26-Beta] - 2025-08-10
### Changed
# - Improved robustness by adding a check for empty plots and logging an
#   info message instead of saving a blank file.
## [0.31.25-Beta] - 2025-08-10
### Fixed
# - Added a conditional check to prevent a UserWarning when creating a
#   legend for an empty plot.
## [0.31.19-Beta] - 2025-08-08
### Fixed
# - Refactored report to be self-contained after the removal of the
#   `_create_cumulative_rate_plot` helper, resolving an ImportError.
## [0.30.20-Beta] - 2025-08-05
### Fixed
# - No functional changes, but inherits fix from _report_utils to prevent
#   a timezone-related TypeError.
## [0.30.16-Beta] - 2025-08-05
### Changed
# - Refactored to use the restored `_create_cumulative_rate_plot` helper.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
from typing import List
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import create_output_directory, get_valid_dataframe

class Report(ContestReport):
    """
    Generates a series of plots comparing cumulative points: one for all bands
    combined, and one for each individual contest band.
    """
    report_id: str = "point_rate_plots"
    report_name: str = "Point Rate Comparison Plots"
    report_type: str = "plot"
    supports_multi = True
    
    def generate(self, output_path: str, **kwargs) -> str:
        """
        Orchestrates the generation of all point rate plots.
        """
        bands = self.logs[0].contest_definition.valid_bands
        is_single_band = len(bands) == 1
        bands_to_plot = ['All'] if is_single_band else ['All'] + bands
        
        created_files = []
        
        for band in bands_to_plot:
            try:
                save_path = os.path.join(output_path, band) if band != "All" else output_path
                
                filepath = self._create_plot(
                    output_path=save_path,
                    band_filter=band,
                )
                if filepath:
                    created_files.append(filepath)
            except Exception as e:
                 print(f"  - Failed to generate point rate plot for {band}: {e}")

        if not created_files:
            return "No point rate plots were generated."
            
        return "Point rate plots saved to:\n" + "\n".join([f"  - {fp}" for fp in created_files])

    def _create_plot(self, output_path: str, band_filter: str) -> str:
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.set_theme(style="whitegrid")

        all_calls = []
        summary_data = []
        
        value_column = 'QSOPoints'
        agg_func = 'sum'
        metric_name = "Points"

        for log in self.logs:
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

            total_value = df[value_column].sum()

            summary_data.append([
                call,
                f"{total_value:,}",
                f"{(df['Run'] == 'Run').sum():,}",
                f"{(df['Run'] == 'S&P').sum():,}",
                f"{(df['Run'] == 'Unknown').sum():,}"
            ])

        metadata = self.logs[0].get_metadata()
        year = get_valid_dataframe(self.logs[0])['Date'].dropna().iloc[0].split('-')[0] if not get_valid_dataframe(self.logs[0]).empty and not get_valid_dataframe(self.logs[0])['Date'].dropna().empty else "----"
        contest_name = metadata.get('ContestName', '')
        event_id = metadata.get('EventID', '')
        
        is_single_band = len(self.logs[0].contest_definition.valid_bands) == 1
        band_text = self.logs[0].contest_definition.valid_bands[0].replace('M', ' Meters') if is_single_band else band_filter.replace('M', ' Meters')
        
        title_line1 = f"{event_id} {year} {contest_name}".strip()
        title_line2 = f"Cumulative {metric_name} ({band_text})"
        
        ax.set_title(f"{title_line1}\n{title_line2}", fontsize=16, fontweight='bold')
        ax.set_xlabel("Contest Time")
        ax.set_ylabel(f"Cumulative {metric_name}")
        
        if ax.get_lines():
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

        # Check if any data was actually plotted before saving
        if not ax.get_lines():
            logging.info(f"Skipping {metric_name} plot for {band_filter}: No data available for any log on this band.")
            plt.close(fig)
            return None
            
        fig.tight_layout()
        create_output_directory(output_path)
        
        filename_band = self.logs[0].contest_definition.valid_bands[0].lower() if is_single_band else band_filter.lower().replace('m', '')
        filename_calls = '_vs_'.join(sorted(all_calls))
        filename = f"{self.report_id}_{filename_band}_{filename_calls}.png"
        filepath = os.path.join(output_path, filename)
        fig.savefig(filepath)
        plt.close(fig)
        return filepath