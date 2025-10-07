# contest_tools/reports/plot_qso_rate.py
#
# Purpose: A plot report that generates a QSO rate graph for all bands
#          and for each individual band.
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
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import create_output_directory, get_valid_dataframe, save_debug_data

class Report(ContestReport):
    """
    Generates a series of plots comparing QSO rates: one for all bands
    combined, and one for each individual contest band.
    """
    report_id: str = "qso_rate_plots"
    report_name: str = "QSO Rate Comparison Plots"
    report_type: str = "plot"
    supports_multi = True
    
    def generate(self, output_path: str, **kwargs) -> str:
        """
        Orchestrates the generation of all QSO rate plots, including per-mode breakdowns.
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
            return "No QSO rate plots were generated."

        return "QSO rate plots saved to:\n" + "\n".join([f"  - {fp}" for fp in all_created_files])

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
                print(f"  - Failed to generate QSO rate plot for {band}: {e}")
        
        return created_files

    def _create_plot(self, dfs: List[pd.DataFrame], output_path: str, band_filter: str, mode_filter: str, **kwargs) -> str:
        debug_data_flag = kwargs.get("debug_data", False)
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.set_theme(style="whitegrid")

        all_calls = []
        summary_data = []
        all_series = []
        
        value_column = 'Call'
        agg_func = 'count'
        metric_name = "QSOs"

        for i, df in enumerate(dfs):
            log = self.logs[i]
            call = log.get_metadata().get('MyCall', 'Unknown')
            all_calls.append(call)

            if band_filter != "All":
                df = df[df['Band'] == band_filter]
            
            if df.empty:
                continue
            
            df_cleaned = df.dropna(subset=['Datetime', value_column]).set_index('Datetime')
            
            hourly_rate = df_cleaned.resample('h')[value_column].agg(agg_func)
            cumulative_rate = hourly_rate.cumsum()
            
            master_time_index = log._log_manager_ref.master_time_index
            if master_time_index is not None:
                cumulative_rate = cumulative_rate.reindex(master_time_index, method='pad').fillna(0)
            
            ax.plot(cumulative_rate.index, cumulative_rate.values, marker='o', linestyle='-', markersize=4, label=call)
            
            cumulative_rate.name = call
            all_series.append(cumulative_rate)

            total_value = len(df)

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
            debug_df = pd.concat(all_series, axis=1).fillna(0)
            debug_filename = f"{self.report_id}_{filename_band}{mode_suffix}_{filename_calls}.txt"
            save_debug_data(debug_data_flag, output_path, debug_df, custom_filename=debug_filename)
        
        filename = f"{self.report_id}_{filename_band}{mode_suffix}_{filename_calls}.png"
        filepath = os.path.join(output_path, filename)
        fig.savefig(filepath)
        plt.close(fig)
        return filepath
