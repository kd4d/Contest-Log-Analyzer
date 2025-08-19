# Contest Log Analyzer/contest_tools/reports/plot_comparative_band_activity.py
#
# Version: 0.40.6-Beta
# Date: 2025-08-19
#
# Purpose: A plot report that generates a comparative "butterfly" chart to
#          visualize the band activity of two logs side-by-side.
#
# --- Revision History ---
## [0.40.6-Beta] - 2025-08-19
### Fixed
# - Restored the timezone localization step that was lost during a previous
#   refactoring, fixing the critical bug that caused plots to be empty.
## [0.40.5-Beta] - 2025-08-19
### Added
# - Report now generates additional, per-mode plots for CW, PH, and DG if
#   data for those modes exists.
## [0.40.4-Beta] - 2025-08-19
### Fixed
# - Refined Y-axis scaling logic to use 5-QSO increments for rates below 45,
#   improving chart readability on low-rate bands.
## [0.40.3-Beta] - 2025-08-19
### Fixed
# - Correctly applied the rounded Y-axis limit to the plot, fixing a bug
#   from the previous version.
## [0.40.2-Beta] - 2025-08-19
### Fixed
# - Implemented an intelligent Y-axis scaling logic to select more
#   readable upper limits, particularly for rates between 50 and 100.
## [0.40.1-Beta] - 2025-08-19
### Fixed
# - Bands are now sorted in ascending order by frequency.
# - Bands with no QSOs by either station are now correctly skipped.
# - The Y-axis of each band's subplot is now scaled independently to the
#   maximum rate on that specific band, improving readability.
## [0.40.0-Beta] - 2025-08-19
### Fixed
# - Modified the figure size calculation to enforce a minimum height,
#   preventing the layout manager from failing on single-band contests.
## [0.39.8-Beta] - 2025-08-19
### Fixed
# - Corrected the plotting logic to fix a UserWarning by setting y-tick
#   locations before setting the labels.
## [0.39.7-Beta] - 2025-08-18
# - Initial release of the Comparative Band Activity report.
#
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
        if max_value == 0: return 5 # Prevent a zero-height axis
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

    def _generate_plot_for_slice(self, df1_slice: pd.DataFrame, df2_slice: pd.DataFrame, log1: ContestLog, log2: ContestLog, output_path: str, mode_filter: str, **kwargs) -> str:
        """Helper function to generate a single plot for a given data slice."""
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')

        # --- 1. Data Preparation ---
        dfs = {call1: df1_slice, call2: df2_slice}
        
        if df1_slice.empty and df2_slice.empty:
            return f"Skipping {mode_filter or 'combined'} plot: No QSO data in slice."

        min_time = min(df['Datetime'].min() for df in dfs.values() if not df.empty).floor('h')
        max_time = max(df['Datetime'].max() for df in dfs.values() if not df.empty).ceil('h')
        time_bins = pd.date_range(start=min_time, end=max_time, freq='15min', tz='UTC')

        all_bands_in_logs = pd.concat([dfs[call1]['Band'], dfs[call2]['Band']]).dropna().unique()
        canonical_band_order = [band[1] for band in ContestLog._HF_BANDS]
        all_bands = sorted(list(all_bands_in_logs), key=lambda b: canonical_band_order.index(b) if b in canonical_band_order else -1)
        
        if not all_bands:
            return f"Skipping {mode_filter or 'combined'} plot: No bands with activity found."

        pivot_dfs = {}
        for call, df in dfs.items():
            pivot = df.pivot_table(index='Band', columns=pd.Grouper(key='Datetime', freq='15min'), aggfunc='size', fill_value=0)
            pivot = pivot.reindex(index=all_bands, columns=time_bins, fill_value=0)
            pivot_dfs[call] = pivot

        # --- 2. Visualization ---
        num_bands = len(all_bands)
        height = max(8.0, 2 * num_bands)
        fig, axes = plt.subplots(num_bands, 1, figsize=(12, height), sharex=True)
        if num_bands == 1: axes = [axes]

        for i, band in enumerate(all_bands):
            ax = axes[i]
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

        # --- 3. Dynamic X-Axis Formatting ---
        contest_duration_hours = (max_time - min_time).total_seconds() / 3600
        hour_interval = 3 if contest_duration_hours <= 24 else 4
        date_format_str = '%H:%M' if contest_duration_hours <= 24 else '%d-%H%M'
        tick_step = hour_interval * 4
        tick_positions = np.arange(0, len(time_bins), tick_step)
        tick_labels = [time_bins[i].strftime(date_format_str) for i in tick_positions]
        plt.xticks(tick_positions, tick_labels, rotation=45, ha='right')
        
        # --- 4. Titles and Legend ---
        mode_title_str = f" ({mode_filter})" if mode_filter else ""
        fig.suptitle(f"{self.report_name}{mode_title_str}\n{call1} (Up) vs. {call2} (Down)", fontsize=16, fontweight='bold')
        axes[-1].set_xlabel("Contest Time (UTC)")
        fig.supylabel("QSOs per 15 min")
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

        # --- Prepare base dataframes ---
        df1 = get_valid_dataframe(log1, include_dupes=False)
        df2 = get_valid_dataframe(log2, include_dupes=False)

        if df1.empty or df2.empty:
            return "Skipping report: At least one log has no valid, non-dupe QSO data."
        
        # --- MODIFICATION: Restore timezone localization ---
        df1['Datetime'] = df1['Datetime'].dt.tz_localize('UTC')
        df2['Datetime'] = df2['Datetime'].dt.tz_localize('UTC')
        
        # --- 1. Generate the main "All Modes" plot ---
        msg = self._generate_plot_for_slice(df1, df2, log1, log2, output_path, mode_filter=None, **kwargs)
        created_files.append(msg)
        
        # --- 2. Generate per-mode plots ---
        modes_to_plot = ['CW', 'PH', 'DG']
        modes_present = pd.concat([df1['Mode'], df2['Mode']]).dropna().unique()

        for mode in modes_to_plot:
            if mode in modes_present:
                df1_slice = df1[df1['Mode'] == mode]
                df2_slice = df2[df2['Mode'] == mode]

                if not df1_slice.empty or not df2_slice.empty:
                    msg = self._generate_plot_for_slice(df1_slice, df2_slice, log1, log2, output_path, mode_filter=mode, **kwargs)
                    created_files.append(msg)

        return "\n".join(created_files)