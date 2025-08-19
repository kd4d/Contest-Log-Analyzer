# Contest Log Analyzer/contest_tools/reports/plot_comparative_band_activity.py
#
# Version: 0.39.8-Beta
# Date: 2025-08-19
#
# Purpose: A plot report that generates a comparative "butterfly" chart to
#          visualize the band activity of two logs side-by-side.
#
# --- Revision History ---
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

    def generate(self, output_path: str, **kwargs) -> str:
        """Generates the report content."""
        if len(self.logs) != 2:
            return f"Error: Report '{self.report_name}' requires exactly two logs."

        log1, log2 = self.logs[0], self.logs[1]
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')

        # --- 1. Data Preparation ---
        dfs = {}
        for call, log in [(call1, log1), (call2, log2)]:
            df = get_valid_dataframe(log, include_dupes=False)
            if df.empty or 'Datetime' not in df.columns or df['Datetime'].isna().all():
                return f"Skipping report: Log for {call} has no valid QSO data with timestamps."
            df['Datetime'] = df['Datetime'].dt.tz_localize('UTC')
            dfs[call] = df

        interval = '15min'
        min_time = min(df['Datetime'].min() for df in dfs.values()).floor('h')
        max_time = max(df['Datetime'].max() for df in dfs.values()).ceil('h')
        time_bins = pd.date_range(start=min_time, end=max_time, freq=interval, tz='UTC')

        all_bands = sorted(list(set(log1.contest_definition.valid_bands) | set(log2.contest_definition.valid_bands)))

        pivot_dfs = {}
        for call, df in dfs.items():
            pivot = df.pivot_table(index='Band', columns=pd.Grouper(key='Datetime', freq=interval), aggfunc='size', fill_value=0)
            pivot = pivot.reindex(index=all_bands, columns=time_bins, fill_value=0)
            pivot_dfs[call] = pivot

        # --- 2. Visualization ---
        num_bands = len(all_bands)
        fig, axes = plt.subplots(num_bands, 1, figsize=(12, 2 * num_bands), sharex=True)
        if num_bands == 1:
            axes = [axes] # Make it iterable

        max_rate = max(pivot.max().max() for pivot in pivot_dfs.values())

        for i, band in enumerate(all_bands):
            ax = axes[i]
            data1 = pivot_dfs[call1].loc[band]
            data2 = -pivot_dfs[call2].loc[band] # Negate for downward bars

            x_pos = np.arange(len(time_bins))

            ax.bar(x_pos, data1, width=1.0, align='center', color='blue', alpha=0.7)
            ax.bar(x_pos, data2, width=1.0, align='center', color='red', alpha=0.7)
            
            ax.axhline(0, color='black', linewidth=0.8)
            ax.set_ylabel(band, rotation=0, ha='right', va='center')
            ax.set_ylim(-max_rate, max_rate)
            
            # Format Y-axis to show positive numbers
            ticks = ax.get_yticks()
            ax.set_yticks(ticks) # Explicitly set the tick locations first
            ax.set_yticklabels([int(abs(tick)) for tick in ticks])

        # --- 3. Dynamic X-Axis Formatting ---
        contest_duration_hours = (max_time - min_time).total_seconds() / 3600
        if contest_duration_hours <= 24:
            hour_interval = 3
            date_format_str = '%H:%M'
        else:
            hour_interval = 4
            date_format_str = '%d-%H%M'

        tick_step = hour_interval * 4
        tick_positions = np.arange(0, len(time_bins), tick_step)
        tick_labels = [time_bins[i].strftime(date_format_str) for i in tick_positions]
        
        plt.xticks(tick_positions, tick_labels, rotation=45, ha='right')
        
        # --- 4. Titles and Legend ---
        fig.suptitle(f"{self.report_name}\n{call1} (Up) vs. {call2} (Down)", fontsize=16, fontweight='bold')
        axes[-1].set_xlabel("Contest Time (UTC)")
        fig.supylabel("QSOs per 15 min")

        fig.tight_layout(rect=[0.03, 0.03, 1, 0.95])

        # --- 5. Save File ---
        create_output_directory(output_path)
        filename = f"{self.report_id}_{call1}_vs_{call2}.png"
        filepath = os.path.join(output_path, filename)
        
        try:
            fig.savefig(filepath)
            plt.close(fig)
            return f"Plot report saved to: {filepath}"
        except Exception as e:
            logging.error(f"Error saving butterfly chart: {e}")
            plt.close(fig)
            return f"Error generating report '{self.report_name}'"