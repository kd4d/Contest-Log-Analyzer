# contest_tools/reports/plot_comparative_band_activity.py
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
# Purpose: A plot report that generates a comparative "butterfly" chart to
#          visualize the band activity of two logs side-by-side.
#
# --- Revision History ---
# [1.0.0] - 2025-11-24
# Refactored to use MatrixAggregator (DAL).
# [0.91.0-Beta] - 2025-10-11
# Initial creation of the correct "butterfly chart" implementation.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import logging
import math
from typing import List, Dict, Any

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import get_valid_dataframe, create_output_directory, save_debug_data
from ..data_aggregators.matrix_stats import MatrixAggregator

class Report(ContestReport):
    """
    Generates a comparative "butterfly" chart of band activity for two logs.
    """
    report_id: str = "comparative_band_activity"
    report_name: str = "Comparative Band Activity"
    report_type: str = "plot"
    supports_pairwise = True

    def _get_rounded_axis_limit(self, max_value: float) -> int:
        """Takes a raw maximum value and returns a sensible upper limit."""
        if max_value == 0: return 5
        if max_value <= 45:
            return int(math.ceil(max_value / 5.0)) * 5
        if max_value <= 50: return 50
        if max_value <= 60: return 60
        if max_value <= 75: return 75
        if max_value <= 80: return 80
        if max_value <= 90: return 90
        if max_value <= 100: return 100
        # For larger values, round up to the nearest 25
        return (int(max_value / 25) + 1) * 25

    def _generate_plot_for_slice(self, matrix_data: Dict, log1: ContestLog, log2: ContestLog, output_path: str, mode_filter: str, **kwargs) -> str:
        """Helper function to generate a single plot for a given data slice (DAL-based)."""
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')

        # --- 1. Data Preparation (Unpack DAL) ---
        time_bins_str = matrix_data['time_bins']
        all_bands = matrix_data['bands']
        
        if not time_bins_str or not all_bands:
            return f"Skipping {mode_filter or 'combined'} plot: No data in slice."

        time_bins = pd.to_datetime(time_bins_str)
        min_time = time_bins.min()
        max_time = time_bins.max()
        
        # Convert List[List] to DataFrame for convenient plotting logic
        pivot_dfs = {}
        for call in [call1, call2]:
            qso_grid = matrix_data['logs'][call]['qso_counts']
            # Multiply by 4 to get rate/hr (since data is 15min)
            df_grid = pd.DataFrame(qso_grid, index=all_bands, columns=time_bins) * 4
            pivot_dfs[call] = df_grid

        # --- 2. Visualization ---
        num_bands = len(all_bands)
        height = max(8.0, 2 * num_bands)
        fig, axes = plt.subplots(num_bands, 1, figsize=(12, height), sharex=True)
        if num_bands == 1: axes = [axes]

        for i, band in enumerate(all_bands):
            ax = axes[i]
            ax.grid(False)
            
            data1 = pivot_dfs[call1].loc[band]
            data2 = -pivot_dfs[call2].loc[band]
            
            band_max_rate = max(data1.max(), data2.abs().max())
            rounded_limit = self._get_rounded_axis_limit(band_max_rate)

            x_pos = np.arange(len(time_bins))
            ax.bar(x_pos, data1, width=1.0, align='center', color='blue', alpha=0.7)
            ax.bar(x_pos, data2, width=1.0, align='center', color='red', alpha=0.7)
            
            ax.axhline(0, color='black', linewidth=0.8)
            ax.set_ylabel(band, rotation=0, ha='right', va='center')
            ax.set_ylim(-rounded_limit, rounded_limit)
            ticks = np.linspace(-rounded_limit, rounded_limit, num=7, dtype=int)
            ax.set_yticks(ticks)
            ax.set_yticklabels([abs(tick) for tick in ticks])
            
            for hour_marker in range(0, len(time_bins) + 1, 4):
                ax.axvline(x=hour_marker - 0.5, color='black', linestyle='-', linewidth=1.5, alpha=0.4)

        # --- 3. Dynamic X-Axis Formatting ---
        if not time_bins.empty:
            contest_duration_hours = (max_time - min_time).total_seconds() / 3600
        else:
            contest_duration_hours = 0
            
        hour_interval = 3 if contest_duration_hours <= 24 else 4
        date_format_str = '%H:%M' if contest_duration_hours <= 24 else '%d-%H%M'
        tick_step = hour_interval * 4
        tick_positions = np.arange(0, len(time_bins), tick_step)
        tick_labels = [time_bins[i].strftime(date_format_str) for i in tick_positions]
        plt.xticks(tick_positions, tick_labels, rotation=45, ha='right')
        
        # --- 4. Titles and Legend ---
        metadata = log1.get_metadata()
        df_first_log = get_valid_dataframe(log1)
        year = df_first_log['Date'].dropna().iloc[0].split('-')[0] if not df_first_log.empty and not df_first_log['Date'].dropna().empty else "----"
        contest_name = metadata.get('ContestName', '')
        event_id = metadata.get('EventID', '')
        
        mode_title_str = f" ({mode_filter})" if mode_filter else ""
        title_line1 = f"{self.report_name}{mode_title_str}"
        context_str = f"{year} {event_id} {contest_name}".strip().replace("  ", " ")
        calls_str = f"{call1} (Up) vs. {call2} (Down)"
        title_line2 = f"{context_str} - {calls_str}"
        
        fig.suptitle(f"{title_line1}\n{title_line2}", fontsize=16, fontweight='bold')
        axes[-1].set_xlabel("Contest Time (UTC)")
        fig.supylabel("QSOs per Hour (Normalized)")
        fig.tight_layout(rect=[0.03, 0.03, 1, 0.95])

        # --- 5. Save File ---
        mode_filename_str = f"_{mode_filter.lower()}" if mode_filter else ""
        filename = f"{self.report_id}{mode_filename_str}_{call1}_vs_{call2}.png"
        filepath = os.path.join(output_path, filename)
        
        try:
            fig.savefig(filepath)
            plt.close(fig)
            return f"Plot report saved to: {filepath}"
        except Exception as e:
            logging.error(f"Error saving butterfly chart for {mode_filter or 'All Modes'}: {e}")
            plt.close(fig)
            return f"Error generating report for {mode_filter or 'All Modes'}"

    def generate(self, output_path: str, **kwargs) -> str:
        """Orchestrates the generation of the combined plot and per-mode plots."""
        if len(self.logs) != 2:
            return f"Error: Report '{self.report_name}' requires exactly two logs."
        log1, log2 = self.logs[0], self.logs[1]
        created_files = []

        # --- 1. Generate the main "All Modes" plot ---
        aggregator = MatrixAggregator(self.logs)
        matrix_data_all = aggregator.get_matrix_data(bin_size='15min', mode_filter=None)
        
        msg = self._generate_plot_for_slice(matrix_data_all, log1, log2, output_path, mode_filter=None, **kwargs)
        created_files.append(msg)
        
        # --- 2. Generate per-mode plots ---
        # Check modes present in raw data to determine if we need loops
        df1 = get_valid_dataframe(log1, include_dupes=False)
        df2 = get_valid_dataframe(log2, include_dupes=False)
        modes_present = pd.concat([df1['Mode'], df2['Mode']]).dropna().unique()

        modes_to_plot = ['CW', 'PH', 'DG']

        if len(modes_present) > 1:
            for mode in modes_to_plot:
                if mode in modes_present:
                    # Fetch specific DAL slice
                    matrix_data_mode = aggregator.get_matrix_data(bin_size='15min', mode_filter=mode)
                    
                    msg = self._generate_plot_for_slice(matrix_data_mode, log1, log2, output_path, mode_filter=mode, **kwargs)
                    created_files.append(msg)

        return "\n".join(created_files)