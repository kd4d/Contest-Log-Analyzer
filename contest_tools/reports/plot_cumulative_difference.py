# Contest Log Analyzer/contest_tools/reports/plot_cumulative_difference.py
#
# Purpose: A plot report that generates a cumulative difference graph,
#          comparing two logs.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-09-03
# Version: 0.57.5-Beta
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
## [0.57.5-Beta] - 2025-09-03
### Changed
# - Updated the chart title to the standard two-line format to conform
#   to the official CLA Reports Style Guide.
## [0.52.2-Beta] - 2025-08-26
### Changed
# - Report now generates individual plots by mode (CW, PH, DG) for both
#   the "All Bands" and per-band summaries on multi-mode contests.
## [0.38.1-Beta] - 2025-08-18
### Fixed
# - Resolved a TypeError by removing the redundant 'metric' keyword from a
#   function call and retrieving it from kwargs instead.
## [0.38.0-Beta] - 2025-08-18
### Added
# - Added call to the save_debug_data helper function to dump the source
#   dataframe when the --debug-data flag is enabled.
## [0.31.31-Beta] - 2025-08-10
### Fixed
# - Refactored time-series logic to calculate cumulative sum before
#   reindexing, fixing phantom rate changes during inactive hours.
## [0.31.30-Beta] - 2025-08-10
### Fixed
# - Corrected logic to properly skip generating empty plots for bands with
#   no QSO data.
## [0.31.29-Beta] - 2025-08-10
### Fixed
# - Corrected a TypeError by creating a correctly-indexed placeholder for
#   logs with no data on a given band.
## [0.31.28-Beta] - 2025-08-10
### Fixed
# - Resolved a TypeError by localizing naive datetimes to UTC before
#   comparing them with the timezone-aware master time index.
## [0.31.27-Beta] - 2025-08-10
### Fixed
# - Corrected time-series logic to use the master time index and
#   forward-filling to ensure all hours of the contest are displayed.
## [0.31.26-Beta] - 2025-08-10
### Changed
# - Replaced print statement with logging.info for "no data" messages.
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
import logging

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import create_output_directory, get_valid_dataframe, save_debug_data

class Report(ContestReport):
    """
    Generates a three-subplot plot showing the cumulative difference in
    QSOs or Points between two logs.
    """
    report_id: str = "cumulative_difference_plots"
    report_name: str = "Cumulative Difference Plots"
    report_type: str = "plot"
    supports_pairwise = True
    
    def _prepare_data_for_plot(self, log: ContestLog, df: pd.DataFrame, value_column: str, agg_func: str, band_filter: str) -> pd.DataFrame:
        """
        Prepares a single log's data for plotting by grouping, aggregating,
        and aligning to the master time index.
        """
        if band_filter != "All":
            df = df[df['Band'] == band_filter]

        master_time_index = log._log_manager_ref.master_time_index

        if df.empty:
            empty_data = {'Run': 0, 'S&P+Unknown': 0}
            cumulative_data = pd.DataFrame(empty_data, index=master_time_index)
            return cumulative_data

        df_cleaned = df.dropna(subset=['Datetime', 'Run', value_column])
        rate_data = df_cleaned.groupby([df_cleaned['Datetime'].dt.floor('h'), 'Run'])[value_column].agg(agg_func).unstack(fill_value=0)

        for col in ['Run', 'S&P', 'Unknown']:
            if col not in rate_data.columns:
                rate_data[col] = 0
        
        rate_data['S&P+Unknown'] = rate_data['S&P'] + rate_data['Unknown']
        
        if not rate_data.empty:
            rate_data.index = rate_data.index.tz_localize('UTC')
        
        cumulative_data = rate_data.cumsum()
            
        if master_time_index is not None:
            cumulative_data = cumulative_data.reindex(master_time_index, method='pad').fillna(0)
            
        return cumulative_data[['Run', 'S&P+Unknown']]


    def _generate_single_plot(self, df1_slice: pd.DataFrame, df2_slice: pd.DataFrame, output_path: str, band_filter: str, mode_filter: str, **kwargs):
        """
        Helper function to generate a single cumulative difference plot.
        """
        debug_data_flag = kwargs.get("debug_data", False)
        metric = kwargs.get('metric', 'qsos')
        log1, log2 = self.logs[0], self.logs[1]
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')

        value_column = 'QSOPoints' if metric == 'points' else 'Call'
        agg_func = 'sum' if metric == 'points' else 'count'
        
        data1 = self._prepare_data_for_plot(log1, df1_slice, value_column, agg_func, band_filter)
        data2 = self._prepare_data_for_plot(log2, df2_slice, value_column, agg_func, band_filter)

        # --- Calculate Differences from Cumulative Data ---
        run_diff = data1['Run'] - data2['Run']
        sp_unk_diff = data1['S&P+Unknown'] - data2['S&P+Unknown']
        overall_diff = run_diff + sp_unk_diff

        # --- Save Debug Data ---
        debug_df = pd.DataFrame({
            f'run_{call1}': data1['Run'], f'sp_unk_{call1}': data1['S&P+Unknown'],
            f'run_{call2}': data2['Run'], f'sp_unk_{call2}': data2['S&P+Unknown'],
            'run_diff': run_diff, 'sp_unk_diff': sp_unk_diff, 'overall_diff': overall_diff
        })
        
        is_single_band = len(log1.contest_definition.valid_bands) == 1
        filename_band = log1.contest_definition.valid_bands[0].lower() if is_single_band else band_filter.lower().replace('m', '')
        mode_suffix = f"_{mode_filter.lower()}" if mode_filter else ""
        debug_filename = f"{self.report_id}_{metric}{mode_suffix}_{filename_band}_{call1}_vs_{call2}.txt"
        save_debug_data(debug_data_flag, output_path, debug_df, custom_filename=debug_filename)
        
        # --- Plotting ---
        sns.set_theme(style="whitegrid")
        fig = plt.figure(figsize=(12, 9))
        
        # Check if there is any actual difference to plot
        if overall_diff.abs().sum() == 0:
            logging.info(f"Skipping {band_filter} difference plot: no data available for this band.")
            plt.close(fig)
            return None

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
        band_text = log1.contest_definition.valid_bands[0].replace('M', ' Meters') if is_single_band else band_filter.replace('M', ' Meters')
        mode_text = f" ({mode_filter})" if mode_filter else ""
        callsign_str = f"{call1} vs. {call2}"

        title_line1 = f"{self.report_name} - {metric_name}{mode_text}"
        title_line2 = f"{year} {event_id} {contest_name} - {callsign_str}".strip().replace("  ", " ")
        final_title = f"{title_line1}\n{title_line2}"
        
        fig.suptitle(final_title, fontsize=16, fontweight='bold')

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
        filename = f"{self.report_id}_{metric}{mode_suffix}_{filename_band}_{call1}_vs_{call2}.png"
        filepath = os.path.join(output_path, filename)
        fig.savefig(filepath)
        plt.close(fig)

        return filepath

    def _orchestrate_plot_generation(self, df1, df2, output_path, mode_filter, **kwargs):
        """Helper to generate the full set of plots for a given data slice."""
        if df1.empty or df2.empty:
            return []

        bands = self.logs[0].contest_definition.valid_bands
        is_single_band = len(bands) == 1
        bands_to_plot = [bands[0]] if is_single_band else ['All'] + bands
        
        created_files = []
        
        for band in bands_to_plot:
            try:
                save_path = output_path
                if not is_single_band and band != 'All':
                    # For per-mode plots, create a subdirectory for the mode
                    if mode_filter:
                        save_path = os.path.join(output_path, mode_filter.lower(), band)
                    else:
                        save_path = os.path.join(output_path, band)
                
                filepath = self._generate_single_plot(
                    df1_slice=df1,
                    df2_slice=df2,
                    output_path=save_path,
                    band_filter=band,
                    mode_filter=mode_filter,
                    **kwargs
                )
                if filepath:
                    created_files.append(filepath)
            except Exception as e:
                print(f"  - Failed to generate difference plot for {band} (Mode: {mode_filter or 'All'}): {e}")
        
        return created_files

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Orchestrates the generation of all cumulative difference plots, including per-mode breakdowns.
        """
        if len(self.logs) != 2:
            return "Error: The Cumulative Difference Plot report requires exactly two logs."

        log1, log2 = self.logs[0], self.logs[1]
        df1_full = get_valid_dataframe(log1)
        df2_full = get_valid_dataframe(log2)

        if df1_full.empty or df2_full.empty:
            return "Skipping report: At least one log has no valid QSO data."

        all_created_files = []

        # 1. Generate plots for "All Modes"
        all_created_files.extend(
            self._orchestrate_plot_generation(df1_full, df2_full, output_path, mode_filter=None, **kwargs)
        )

        # 2. Generate plots for each mode if applicable
        modes_present = pd.concat([df1_full['Mode'], df2_full['Mode']]).dropna().unique()
        if len(modes_present) > 1:
            for mode in ['CW', 'PH', 'DG']:
                if mode in modes_present:
                    df1_slice = df1_full[df1_full['Mode'] == mode]
                    df2_slice = df2_full[df2_full['Mode'] == mode]
                    
                    all_created_files.extend(
                        self._orchestrate_plot_generation(df1_slice, df2_slice, output_path, mode_filter=mode, **kwargs)
                    )
        
        if not all_created_files:
            return f"No difference plots were generated for metric '{kwargs.get('metric', 'qsos')}'."

        return f"Cumulative difference plots for {kwargs.get('metric', 'qsos')} saved to relevant subdirectories."