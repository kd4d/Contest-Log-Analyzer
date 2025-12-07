# contest_tools/reports/plot_cumulative_difference.py
#
# Purpose: A plot report that generates a cumulative difference graph,
#          comparing two logs.
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
#
# --- Revision History ---
# [1.0.0] - 2025-11-24
# - Refactored to use Data Abstraction Layer (TimeSeriesAggregator).
# - Enabled Run/S&P plots for Points metric via 'run_points' schema.
# [0.90.0-Beta] - 2025-10-01
# Set new baseline version for release.

from typing import List
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import create_output_directory, get_valid_dataframe, save_debug_data
from ..data_aggregators.time_series import TimeSeriesAggregator

class Report(ContestReport):
    """
    Generates a three-subplot plot showing the cumulative difference in
    QSOs or Points between two logs.
    """
    report_id: str = "cumulative_difference_plots"
    report_name: str = "Cumulative Difference Plots"
    report_type: str = "plot"
    supports_pairwise = True
    
    def _generate_single_plot(self, output_path: str, band_filter: str, mode_filter: str, **kwargs):
        """
        Helper function to generate a single cumulative difference plot.
        """
        debug_data_flag = kwargs.get("debug_data", False)
        metric = kwargs.get('metric', 'qsos')
        log1, log2 = self.logs[0], self.logs[1]
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')
        
        # --- DAL Integration (v1.3.1) ---
        agg = TimeSeriesAggregator([log1, log2])
        ts_data = agg.get_time_series_data(band_filter=band_filter, mode_filter=mode_filter)
        time_bins = [pd.Timestamp(t) for t in ts_data['time_bins']]

        # Helper to extract series
        def get_series(call_key, field):
            vals = ts_data['logs'][call_key]['cumulative'][field]
            return pd.Series(vals, index=time_bins)

        sns.set_theme(style="whitegrid")
        fig = plt.figure(figsize=(12, 9))
        gs = fig.add_gridspec(5, 1)
        ax1 = fig.add_subplot(gs[0:3, 0])
        ax2 = fig.add_subplot(gs[3, 0], sharex=ax1)
        ax3 = fig.add_subplot(gs[4, 0], sharex=ax1)
        
        if metric == 'points':
            metric_name = log1.contest_definition.points_header_label or "Points"
            
            run1 = get_series(call1, 'run_points')
            sp1 = get_series(call1, 'sp_unk_points')
            run2 = get_series(call2, 'run_points')
            sp2 = get_series(call2, 'sp_unk_points')
            
            run_diff = run1 - run2
            sp_unk_diff = sp1 - sp2
            overall_diff = (run1 + sp1) - (run2 + sp2)

            debug_df = pd.DataFrame({
                f'run_pts_{call1}': run1, f'sp_pts_{call1}': sp1,
                f'run_pts_{call2}': run2, f'sp_pts_{call2}': sp2,
                'run_diff': run_diff, 'sp_unk_diff': sp_unk_diff, 'overall_diff': overall_diff
            })
            
        else: # metric == 'qsos'
            metric_name = "QSOs"
            
            run1 = get_series(call1, 'run_qsos')
            sp1 = get_series(call1, 'sp_unk_qsos')
            run2 = get_series(call2, 'run_qsos')
            sp2 = get_series(call2, 'sp_unk_qsos')
            
            run_diff = run1 - run2
            sp_unk_diff = sp1 - sp2
            overall_diff = (run1 + sp1) - (run2 + sp2)
            
            debug_df = pd.DataFrame({
                f'run_qso_{call1}': run1, f'sp_qso_{call1}': sp1,
                f'run_qso_{call2}': run2, f'sp_qso_{call2}': sp2,
                'run_diff': run_diff, 'sp_unk_diff': sp_unk_diff, 'overall_diff': overall_diff
            })
        
        # --- Plotting ---
        if overall_diff.abs().sum() == 0 and run_diff.abs().sum() == 0 and sp_unk_diff.abs().sum() == 0:
            logging.info(f"Skipping {band_filter} difference plot: no data available for this band.")
            plt.close(fig)
            return None

        ax1.plot(overall_diff.index, overall_diff, marker='o', markersize=4)
        if ax2.get_figure() == fig: # Check if ax2 still exists
            ax2.plot(run_diff.index, run_diff, marker='o', markersize=4, color='green')
        if ax3.get_figure() == fig: # Check if ax3 still exists
            ax3.plot(sp_unk_diff.index, sp_unk_diff, marker='o', markersize=4, color='purple')
        
        # --- Formatting & Saving ---
        ax1.set_ylabel(f"Overall Diff ({metric_name})")
        if ax2.get_figure() == fig:
            ax2.set_ylabel(f"Run Diff")
        if ax3.get_figure() == fig:
            ax3.set_ylabel(f"S&P+Unk Diff")
        ax3.set_xlabel("Contest Time")

        for ax in [ax for ax in [ax1, ax2, ax3] if ax.get_figure() == fig]:
            ax.grid(True, which='both', linestyle='--')
            ax.axhline(0, color='black', linewidth=0.8, linestyle='-')
        
        if ax2.get_figure() == fig:
            plt.setp(ax1.get_xticklabels(), visible=False)
            plt.setp(ax2.get_xticklabels(), visible=False)

        metadata = log1.get_metadata()
        year = get_valid_dataframe(log1)['Date'].dropna().iloc[0].split('-')[0] if not get_valid_dataframe(log1).empty else "----"
        contest_name = metadata.get('ContestName', '')
        event_id = metadata.get('EventID', '')
        
        is_single_band = len(log1.contest_definition.valid_bands) == 1
        band_text = log1.contest_definition.valid_bands[0].replace('M', ' Meters') if is_single_band else band_filter.replace('M', ' Meters')
        mode_text = f" ({mode_filter})" if mode_filter else ""
        callsign_str = f"{call1} vs. {call2}"

        title_line1 = f"{self.report_name} - {metric_name}{mode_text}"
        title_line2 = f"{year} {event_id} {contest_name} - {callsign_str}".strip().replace("  ", " ")
        final_title = f"{title_line1}\n{title_line2}"
        
        fig.suptitle(final_title, fontsize=16, fontweight='bold')
        fig.tight_layout(rect=[0, 0.03, 1, 0.93])

        filename_band = log1.contest_definition.valid_bands[0].lower() if is_single_band else band_filter.lower().replace('m', '')
        mode_suffix = f"_{mode_filter.lower()}" if mode_filter else ""
        debug_filename = f"{self.report_id}_{metric}{mode_suffix}_{filename_band}_{call1}_vs_{call2}.txt"
        save_debug_data(debug_data_flag, output_path, debug_df, custom_filename=debug_filename)
        
        create_output_directory(output_path)
        filename = f"{self.report_id}_{metric}{mode_suffix}_{filename_band}_{call1}_vs_{call2}.png"
        filepath = os.path.join(output_path, filename)
        fig.savefig(filepath)
        plt.close(fig)

        return filepath

    def _orchestrate_plot_generation(self, dfs: List[pd.DataFrame], output_path: str, mode_filter: str, **kwargs):
        """Helper to generate the full set of plots for a given data slice."""
        if any(df.empty for df in dfs):
            return []

        bands = self.logs[0].contest_definition.valid_bands
        is_single_band = len(bands) == 1
        bands_to_plot = ['All'] if is_single_band else ['All'] + bands
        
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
            self._orchestrate_plot_generation(dfs=[df1_full, df2_full], output_path=output_path, mode_filter=None, **kwargs)
        )

        # 2. Generate plots for each mode if applicable
        modes_present = pd.concat([df1_full['Mode'], df2_full['Mode']]).dropna().unique()
        if len(modes_present) > 1:
            for mode in ['CW', 'PH', 'DG']:
                if mode in modes_present:
                    sliced_dfs = [df[df['Mode'] == mode] for df in [df1_full, df2_full]]
                    
                    all_created_files.extend(
                        self._orchestrate_plot_generation(sliced_dfs, output_path, mode_filter=mode, **kwargs)
                    )
        
        if not all_created_files:
            return f"No difference plots were generated for metric '{kwargs.get('metric', 'qsos')}'."

        return f"Cumulative difference plots for {kwargs.get('metric', 'qsos')} saved to relevant subdirectories."