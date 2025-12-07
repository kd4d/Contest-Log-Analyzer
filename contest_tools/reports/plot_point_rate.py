# contest_tools/reports/plot_point_rate.py
#
# Purpose: A plot report that generates a point rate graph for all bands
#          and for each individual band.
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
# [0.90.0-Beta] - 2025-10-01
# Set new baseline version for release.

from typing import List
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import create_output_directory, get_valid_dataframe, save_debug_data
from ..data_aggregators.time_series import TimeSeriesAggregator

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
        Orchestrates the generation of all point rate plots, including per-mode breakdowns.
        """
        all_created_files = []
        
        # Prepare full dataframes once
        full_dfs = [get_valid_dataframe(log) for log in self.logs]
        if any(df.empty for df in full_dfs):
            return "Skipping report: At least one log has no valid QSO data."

        # 1. Generate plots for "All Modes"
        all_created_files.extend(
            self._orchestrate_plot_generation(full_dfs, output_path, mode_filter=None, **kwargs)
        )

        # 2. Generate plots for each mode if applicable
        modes_present = pd.concat([df['Mode'] for df in full_dfs]).dropna().unique()
        if len(modes_present) > 1:
            for mode in ['CW', 'PH', 'DG']:
                if mode in modes_present:
                    sliced_dfs = [df[df['Mode'] == mode] for df in full_dfs]
                    all_created_files.extend(
                        self._orchestrate_plot_generation(sliced_dfs, output_path, mode_filter=mode, **kwargs)
                    )
        
        if not all_created_files:
            return "No point rate plots were generated."

        return "Point rate plots saved to:\n" + "\n".join([f"  - {fp}" for fp in all_created_files])

    def _orchestrate_plot_generation(self, dfs: List[pd.DataFrame], output_path: str, mode_filter: str, **kwargs) -> List[str]:
        """Helper to generate the full set of plots for a given data slice."""
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
                
                filepath = self._create_plot(
                    dfs=dfs,
                    output_path=save_path,
                    band_filter=band,
                    mode_filter=mode_filter,
                    **kwargs
                )
                if filepath:
                    created_files.append(filepath)
            except Exception as e:
                print(f"  - Failed to generate point rate plot for {band}: {e}")
        
        return created_files

    def _create_plot(self, dfs: List[pd.DataFrame], output_path: str, band_filter: str, mode_filter: str, **kwargs) -> str:
        debug_data_flag = kwargs.get("debug_data", False)
        bands = self.logs[0].contest_definition.valid_bands
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.set_theme(style="whitegrid")

        all_calls = []
        summary_data = []
        all_series = []
        
        metric_name = self.logs[0].contest_definition.points_header_label
        if not metric_name:
            metric_name = "Points"

        # --- DAL Integration (v1.3.1) ---
        agg = TimeSeriesAggregator(self.logs)
        ts_data = agg.get_time_series_data(band_filter=band_filter, mode_filter=mode_filter)
        time_bins = [pd.Timestamp(t) for t in ts_data['time_bins']]

        for i, df in enumerate(dfs):
            log = self.logs[i]
            call = log.get_metadata().get('MyCall', 'Unknown')
            all_calls.append(call)
            
            log_data = ts_data['logs'].get(call)
            if not log_data:
                continue

            # NEW LOGIC: Use 'points' from aggregator (Raw Sum)
            cumulative_values = log_data['cumulative']['points']
            scalars = log_data['scalars']

            if scalars['net_qsos'] == 0:
                 continue
            
            # Plot
            series = pd.Series(cumulative_values, index=time_bins, name=call)
            ax.plot(series.index, series.values, marker='o', linestyle='-', markersize=4, label=call)
            all_series.append(series)

            # NOTE: Run/S&P split for summary table calculation
            if band_filter != "All":
                 df_filtered = df[df['Band'] == band_filter]
            else:
                 df_filtered = df

            total_value = scalars.get('points_sum', 0)

            summary_data.append([
                call,
                f"{total_value:,}",
                f"{(df_filtered['Run'] == 'Run').sum():,}",
                f"{(df_filtered['Run'] == 'S&P').sum():,}",
                f"{(df_filtered['Run'] == 'Unknown').sum():,}"
            ])

        metadata = self.logs[0].get_metadata()
        year = get_valid_dataframe(self.logs[0])['Date'].dropna().iloc[0].split('-')[0] if not get_valid_dataframe(self.logs[0]).empty and not get_valid_dataframe(self.logs[0])['Date'].dropna().empty else "----"
        contest_name = metadata.get('ContestName', '')
        event_id = metadata.get('EventID', '')
        
        is_single_band = len(self.logs[0].contest_definition.valid_bands) == 1
        band_text = self.logs[0].contest_definition.valid_bands[0].replace('M', ' Meters') if is_single_band else band_filter.replace('M', ' Meters')
        mode_text = f" ({mode_filter})" if mode_filter else ""
        callsign_str = ", ".join(all_calls)

        title_line1 = f"{self.report_name}{mode_text}"
        title_line2 = f"{year} {event_id} {contest_name} - {callsign_str}".strip().replace("  ", " ")
        final_title = f"{title_line1}\n{title_line2}"
        
        ax.set_title(final_title, fontsize=16, fontweight='bold')
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
        mode_suffix = f"_{mode_filter.lower()}" if mode_filter else ""
        
        # --- Save Debug Data ---
        if all_series:
            # Start with the score data
            debug_df = pd.concat(all_series, axis=1).fillna(0).copy()
             
            # Add multiplier data if it exists (using local access to log until mults moved to aggregation in later batch)
            for i, log in enumerate(self.logs):
                call = all_calls[i]
                if hasattr(log, 'time_series_score_df') and log.time_series_score_df is not None:
                    score_ts = log.time_series_score_df
                    if 'total_mults' in score_ts.columns:
                        debug_df[f'mults_{call}'] = score_ts['total_mults']
                    for band in bands:
                        band_col = f'total_mults_{band}'
                        if band_col in score_ts.columns:
                            debug_df[f'mults_{band}_{call}'] = score_ts[band_col]
            
            debug_filename = f"{self.report_id}_{filename_band}{mode_suffix}_{filename_calls}.txt"
            save_debug_data(debug_data_flag, output_path, debug_df, custom_filename=debug_filename)
        
        filename = f"{self.report_id}_{filename_band}{mode_suffix}_{filename_calls}.png"
        filepath = os.path.join(output_path, filename)
        fig.savefig(filepath)
        plt.close(fig)
        return filepath