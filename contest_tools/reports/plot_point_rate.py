# Contest Log Analyzer/contest_tools/reports/plot_point_rate.py
#
# Purpose: Generates a plot showing the cumulative point rate for one or more logs.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-05
# Version: 0.30.12-Beta
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
## [0.30.12-Beta] - 2025-08-05
### Fixed
# - Standardized the output filename generation for consistency.
## [0.30.8-Beta] - 2025-08-05
### Fixed
# - Corrected a TypeError.
## [0.30.1-Beta] - 2025-08-05
### Fixed
# - Changed import from 'ReportInterface' to 'ContestReport'.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
from .report_interface import ContestReport
from ._report_utils import get_valid_dataframe, create_output_directory
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import os
import logging

class Report(ContestReport):
    report_id = "point_rate_plots"
    report_name = "Cumulative Point Rate Plot"
    report_type = "plot"
    supports_single = True
    supports_pairwise = False
    supports_multi = True

    def generate(self, output_path: str, **kwargs) -> str:
        create_output_directory(output_path)
        include_dupes = kwargs.get('include_dupes', False)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        all_calls = []
        table_data = []

        for log in self.logs:
            callsign = log.get_metadata().get('MyCall', 'Unknown')
            all_calls.append(callsign)
            df = get_valid_dataframe(log, include_dupes)

            if df.empty or 'QSOPoints' not in df.columns or df['QSOPoints'].sum() == 0:
                logging.warning(f"Skipping {callsign} in '{self.report_name}': No point data available.")
                continue
                
            df = df.set_index('Datetime')
            
            master_time_index = log._log_manager_ref.master_time_index
            if master_time_index is None:
                return f"Skipping '{self.report_name}': Master time index not available."

            point_rate = df.resample('h')['QSOPoints'].sum().reindex(master_time_index, fill_value=0)
            cumulative_points = point_rate.cumsum()
            
            ax.plot(cumulative_points.index, cumulative_points, label=callsign, marker='o', markersize=2, linestyle='-')
            
            total_points = df['QSOPoints'].sum()
            total_qsos = len(df)
            avg_ppq = total_points / total_qsos if total_qsos > 0 else 0
            table_data.append([callsign, f'{total_points:,.0f}', f'{total_qsos:,.0f}', f'{avg_ppq:.2f}'])

        if not table_data:
            plt.close(fig)
            return f"Skipping '{self.report_name}': No logs had sufficient data to plot."

        # Formatting the plot
        ax.set_title(f'Cumulative Point Rate: {", ".join(all_calls)}', fontsize=16)
        ax.set_xlabel('Contest Time (UTC)')
        ax.set_ylabel('Cumulative Points')
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.legend(loc='upper left')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        plt.xticks(rotation=45)

        # Adding summary table
        col_labels = ['Callsign', 'Total Points', 'Total QSOs', 'Avg Pts/QSO']
        the_table = plt.table(cellText=table_data, colLabels=col_labels, loc='bottom', bbox=[0, -0.25, 1, 0.15])
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(10)
        
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)
        
        filename_calls = '_'.join(all_calls)
        output_filename = os.path.join(output_path, f"{self.report_id}_{filename_calls}.png")
        try:
            plt.savefig(output_filename, dpi=150)
            plt.close(fig)
            return f"'{self.report_name}' saved to {output_filename}"
        except Exception as e:
            logging.error(f"Error saving plot: {e}")
            plt.close(fig)
            return f"Error generating report '{self.report_name}'"