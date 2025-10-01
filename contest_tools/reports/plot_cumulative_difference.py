# contest_tools/reports/plot_cumulative_difference.py
#
# Purpose: A plot report that generates a cumulative difference graph,
#          comparing two logs.
#
# Author: Gemini AI
# Date: 2025-10-01
# Version: 0.90.0-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# --- Revision History ---
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

class Report(ContestReport):
    """
    Generates a three-subplot plot showing the cumulative difference in
    QSOs or Points between two logs.
    """
    report_id: str = "cumulative_difference_plots"
    report_name: str = "Cumulative Difference Plots"
    report_type: str = "plot"
    supports_pairwise = True
    
    def _prepare_qso_data_for_plot(self, log: ContestLog, df: pd.DataFrame, band_filter: str) -> pd.DataFrame:
        """
        Prepares a single log's QSO data for plotting by grouping, aggregating,
        and aligning to the master time index.
        """
        if band_filter != "All":
            df = df[df['Band'] == band_filter]

        master_time_index = log._log_manager_ref.master_time_index

        if df.empty:
            empty_data = {'Run': 0, 'S&P+Unknown': 0}
            cumulative_data = pd.DataFrame(empty_data, index=master_time_index)
            return cumulative_data
        
        df_cleaned = df.dropna(subset=['Datetime', 'Run', 'Call'])
        rate_data = df_cleaned.groupby([df_cleaned['Datetime'].dt.floor('h'), 'Run'])['Call'].count().unstack(fill_value=0)

        for col in ['Run', 'S&P', 'Unknown']:
            if col not in rate_data.columns:
                rate_data[col] = 0
        
        rate_data['S&P+Unknown'] = rate_data['S&P'] + rate_data['Unknown']
        
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
        master_time_index = log1._log_manager_ref.master_time_index
        
        sns.set_theme(style="whitegrid")
        fig = plt.figure(figsize=(12, 9))
        gs = fig.add_gridspec(5, 1)
        ax1 = fig.add_subplot(gs[0:3, 0])
        ax2 = fig.add_subplot(gs[3, 0], sharex=ax1)
        ax3 = fig.add_subplot(gs[4, 0], sharex=ax1)
        
        if metric == 'points':
            metric_name = log1.contest_definition.points_header_label or "Points"
            score1_ts = log1.time_series_score_df.reindex(master_time_index, method='pad').fillna(0)
            score2_ts = log2.time_series_score_df.reindex(master_time_index, method='pad').fillna(0)
            if log1.contest_definition.contest_name.startswith('WAE'):
                # WAE has non-linear scoring, so only show the overall difference
                fig.delaxes(ax2)
                fig.delaxes(ax3)
                gs.set_height_ratios([1])
                overall_diff = score1_ts['score'] - score2_ts['score']
                run_diff = pd.Series(0, index=overall_diff.index)
                sp_unk_diff = pd.Series(0, index=overall_diff.index)
            else:
                run_diff = score1_ts['run_score'] - score2_ts['run_score']
                sp_unk_diff = score1_ts['sp_unk_score'] - score2_ts['sp_unk_score']
                overall_diff = score1_ts['score'] - score2_ts['score']
            debug_df = pd.concat([score1_ts.add_suffix(f'_{call1}'), score2_ts.add_suffix(f'_{call2}')], axis=1)
        else: # metric == 'qsos'
            metric_name = "QSOs"
            data1 = self._prepare_qso_data_for_plot(log1, df1_slice, band_filter)
            data2 = self._prepare_qso_data_for_plot(log2, df2_slice, band_filter)

            run_diff = data1['Run'] - data2['Run']
            sp_unk_diff = data1['S&P+Unknown'] - data2['S&P+Unknown']
            overall_diff = run_diff + sp_unk_diff
            
            debug_df = pd.DataFrame({
                f'run_{call1}': data1['Run'], f'sp_unk_{call1}': data1['S&P+Unknown'],
                f'run_{call2}': data2['Run'], f'sp_unk_{call2}': data2['S&P+Unknown'],
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
                    df1_slice=dfs[0],
                    df2_slice=dfs[1],
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
