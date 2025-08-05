# Contest Log Analyzer/contest_tools/reports/plot_cumulative_difference.py
#
# Purpose: Generates a plot showing the cumulative difference in QSOs and Points
#          between two logs over time. It provides a clear visualization of how
#          the lead changes throughout the contest.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-05
# Version: 0.30.0-Beta
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
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
# - Standardized all project files to a common baseline version.
from .report_interface import ContestReport
from ._report_utils import get_valid_dataframe, create_output_directory
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import os
import logging

class Report(ContestReport):
    report_id = "cumulative_difference_plots"
    report_name = "Cumulative Difference Plot"
    report_type = "plot"
    supports_single = False
    supports_pairwise = True
    supports_multi = False

    def generate(self, output_path: str, **kwargs) -> str:
        create_output_directory(output_path)
        metric = kwargs.get('metric', 'qsos')
        include_dupes = kwargs.get('include_dupes', False)
        
        if len(self.logs) != 2:
            return f"Report '{self.report_name}' requires exactly two logs for comparison. Skipping."

        log1, log2 = self.logs[0], self.logs[1]
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')
        
        df1 = get_valid_dataframe(log1, include_dupes).set_index('Datetime')
        df2 = get_valid_dataframe(log2, include_dupes).set_index('Datetime')

        if df1.empty or df2.empty:
            return f"Skipping '{self.report_name}': At least one log has no valid QSOs."
            
        # Use the master time index from the log manager
        master_time_index = log1._log_manager_ref.master_time_index
        if master_time_index is None:
            return f"Skipping '{self.report_name}': Master time index not available."

        # Prepare dataframes aligned to the master index
        rate1 = self._prepare_rate_data(df1, master_time_index, metric)
        rate2 = self._prepare_rate_data(df2, master_time_index, metric)

        # Calculate differences
        diff = rate1 - rate2
        diff_run = self._prepare_rate_data(df1[df1['Run']], master_time_index, metric) - \
                   self._prepare_rate_data(df2[df2['Run']], master_time_index, metric)
        diff_sp = self._prepare_rate_data(df1[~df1['Run']], master_time_index, metric) - \
                  self._prepare_rate_data(df2[~df2['Run']], master_time_index, metric)
                  
        # Plotting
        fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
        metric_label = 'Point' if metric == 'points' else 'QSO'
        fig.suptitle(f'Cumulative {metric_label} Difference: {call1} vs {call2}', fontsize=16)

        self._plot_difference(axes[0], diff, f'Overall Diff ({call1} - {call2})', call1, call2)
        self._plot_difference(axes[1], diff_run, f'Run {metric_label} Diff', call1, call2)
        self._plot_difference(axes[2], diff_sp, f'S&P {metric_label} Diff', call1, call2)

        # Formatting X-axis
        axes[2].xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        plt.xticks(rotation=45)
        plt.xlabel('Contest Time (UTC)')
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        
        output_filename = os.path.join(output_path, f"{self.report_id}_{metric}_{call1}_{call2}.png")
        try:
            plt.savefig(output_filename, dpi=150)
            plt.close(fig)
            return f"'{self.report_name}' ({metric}) saved to {output_filename}"
        except Exception as e:
            logging.error(f"Error saving plot: {e}")
            plt.close(fig)
            return f"Error generating report '{self.report_name}'"
            
    def _prepare_rate_data(self, df, index, metric):
        col = 'QSOPoints' if metric == 'points' else 'Band' # Use 'Band' for QSO count
        if col not in df.columns:
            return pd.Series(0, index=index)
            
        rate = df.resample('h')[col].count() if metric == 'qsos' else df.resample('h')[col].sum()
        return rate.reindex(index, fill_value=0).cumsum()

    def _plot_difference(self, ax, data, title, call1, call2):
        ax.plot(data.index, data, label=title)
        ax.fill_between(data.index, data, where=data >= 0, facecolor='green', alpha=0.5, interpolate=True)
        ax.fill_between(data.index, data, where=data <= 0, facecolor='red', alpha=0.5, interpolate=True)
        ax.axhline(0, color='black', linestyle='--', linewidth=0.8)
        ax.set_ylabel('Difference')
        ax.set_title(title, fontsize=10)
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.legend([f'{call1} Ahead', f'{call2} Ahead'], loc='upper left')