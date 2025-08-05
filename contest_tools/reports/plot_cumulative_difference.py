# Contest Log Analyzer/contest_tools/reports/plot_cumulative_difference.py
#
# Purpose: A plot report that generates a cumulative difference graph,
#          comparing two logs.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-05
# Version: 0.30.22-Beta
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
## [0.30.22-Beta] - 2025-08-05
### Fixed
# - Corrected filename and title generation logic to properly handle
#   single-band contests, replacing "All" with the specific band name.
## [0.30.19-Beta] - 2025-08-05
### Fixed
# - Removed stray conversational text from the end of the file.
## [0.30.17-Beta] - 2025-08-05
### Changed
# - Restored the original three-panel plot style (Overall, Run, S&P).
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
from typing import List
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import create_output_directory, get_valid_dataframe

class Report(ContestReport):
    """
    Generates a three-subplot plot showing the cumulative difference in
    QSOs or Points between two logs.
    """
    report_id: str = "cumulative_difference_plots"
    report_name: str = "Cumulative Difference Plots"
    report_type: str = "plot"
    supports_pairwise = True
    
    def _prepare_data_for_plot(self, log: ContestLog, value_column: str, agg_func: str, band_filter: str) -> pd.DataFrame:
        """
        Prepares a single log's data for plotting by grouping and aggregating.
        """
        df = get_valid_dataframe(log)
        
        if band_filter != "All":
            df = df[df['Band'] == band_filter]

        if df.empty:
            return pd.DataFrame(columns=['Run', 'S&P+Unknown'])

        df_cleaned = df.dropna(subset=['Datetime', 'Run', value_column])
        rate_data = df_cleaned.groupby([df_cleaned['Datetime'].dt.floor('h'), 'Run'])[value_column].agg(agg_func).unstack(fill_value=0)

        for col in ['Run', 'S&P', 'Unknown']:
            if col not in rate_data.columns:
                rate_data[col] = 0
        
        rate_data['S&P+Unknown'] = rate_data['S&P'] + rate_data['Unknown']
        
        return rate_data[['Run', 'S&P+Unknown']]


    def _generate_single_plot(self, output_path: str, band_filter: str, metric: str):
        """
        Helper function to generate a single cumulative difference plot.
        """
        log1, log2 = self.logs[0], self.logs[1]
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')

        value_column = 'QSOPoints' if metric == 'points' else 'Call'
        agg_func = 'sum' if metric == 'points' else 'count'
        
        data1 = self._prepare_data_for_plot(log1, value_column, agg_func, band_filter)
        data2 = self._prepare_data_for_plot(log2, value_column, agg_func, band_filter)
        
        master_index = data1.index.union(data2.index)
        
        data1 = data1.reindex(master_index, fill_value=0)
        data2 = data2.reindex(master_index, fill_value=0)

        if data1.empty and data2.empty:
            print(f"  - Skipping {band_filter} difference plot: no data.")
            return None

        # --- Calculate Cumulative Differences ---
        run_diff = (data1['Run'].cumsum() - data2['Run'].cumsum())
        sp_unk_diff = (data1['S&P+Unknown'].cumsum() - data2['S&P+Unknown'].cumsum())
        overall_diff = run_diff + sp_unk_diff

        # --- Plotting ---
        sns.set_theme(style="whitegrid")
        fig = plt.figure(figsize=(12, 9))
        gs = fig.add_gridspec(5, 1)
        
        ax1 = fig.add_subplot(gs[0:3, 0])
        ax2 = fig.add_subplot(gs[3, 0], sharex=ax1)
        ax3 = fig.add_subplot(gs[4, 0], sharex=ax1)

        ax1.plot(overall_diff.index, overall_diff, marker='o', markersize=4)
        ax2.plot(run_diff.index, run_diff, marker='o', markersize=4, color='green')
        ax3.plot(sp_unk_diff.index, sp_unk_diff, marker='o', markersize=4, color='purple')

        # --- Formatting ---
        metadata = log1.get_metadata()
        year = get_valid_dataframe(log1)['Date'].dropna().iloc[0].split('-')[0] if not get_valid_dataframe(log1).empty else "----"
        contest_name = metadata.get('ContestName', '')
        event_id = metadata.get('EventID', '')
        
        metric_name = "Points" if metric == 'points' else "QSOs"
        is_single_band = len(log1.contest_definition.valid_bands) == 1
        band_text = log1.contest_definition.valid_bands[0].replace('M', ' Meters') if is_single_band else band_filter.replace('M', ' Meters')

        title_line1 = f"{event_id} {year} {contest_name}".strip()
        title_line2 = f"Cumulative {metric_name} Difference ({band_text})"
        sub_title = f"{call1} minus {call2}"
        
        fig.suptitle(f"{title_line1}\n{title_line2}", fontsize=16, fontweight='bold')
        ax1.set_title(sub_title, fontsize=12)

        ax1.set_ylabel(f"Overall Diff ({metric_name})")
        ax2.set_ylabel(f"Run Diff")
        ax3.set_ylabel(f"S&P+Unk Diff")
        ax3.set_xlabel("Contest Time")

        for ax in [ax1, ax2, ax3]:
            ax.grid(True, which='both', linestyle='--')
            ax.axhline(0, color='black', linewidth=0.8, linestyle='-')
        
        plt.setp(ax1.get_xticklabels(), visible=False)
        plt.setp(ax2.get_xticklabels(), visible=False)
        fig.tight_layout(rect=[0, 0.03, 1, 0.93])

        # --- Save File ---
        create_output_directory(output_path)
        filename_band = log1.contest_definition.valid_bands[0].lower() if is_single_band else band_filter.lower().replace('m', '')
        filename = f"{self.report_id}_{metric}_{filename_band}_{call1}_vs_{call2}.png"
        filepath = os.path.join(output_path, filename)
        fig.savefig(filepath)
        plt.close(fig)

        return filepath

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Orchestrates the generation of all cumulative difference plots.
        """
        if len(self.logs) != 2:
            return "Error: The Cumulative Difference Plot report requires exactly two logs."

        metric = kwargs.get('metric', 'qsos')
        bands = self.logs[0].contest_definition.valid_bands
        is_single_band = len(bands) == 1
        bands_to_plot = [bands[0]] if is_single_band else ['All'] + bands
        
        created_files = []
        
        for band in bands_to_plot:
            try:
                save_path = output_path
                if not is_single_band and band != 'All':
                    save_path = os.path.join(output_path, band)
                
                filepath = self._generate_single_plot(
                    output_path=save_path,
                    band_filter=band,
                    metric=metric
                )
                if filepath:
                    created_files.append(filepath)
            except Exception as e:
                print(f"  - Failed to generate difference plot for {band}: {e}")

        if not created_files:
            return f"No difference plots were generated for metric '{metric}'."

        return f"Cumulative difference plots for {metric} saved to:\n" + "\n".join([f"  - {fp}" for fp in created_files])