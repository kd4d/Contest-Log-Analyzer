# Contest Log Analyzer/contest_tools/reports/plot_cumulative_difference.py
#
# Purpose: A plot report that generates a cumulative difference chart for
#          either QSOs or Points between two logs over time.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-07
# Version: 0.30.37-Beta
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
## [0.30.37-Beta] - 2025-08-07
### Fixed
# - Corrected a NameError by adding the missing import for 'Optional'
#   from the typing library.
## [0.30.36-Beta] - 2025-08-07
### Fixed
# - Corrected an ImportError by updating the script to use the new
#   `_prepare_time_series_data` helper function.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
from .report_interface import ContestReport
from ._report_utils import get_valid_dataframe, create_output_directory, _prepare_time_series_data, _create_time_series_figure
import matplotlib.pyplot as plt
import os
from typing import Optional

class Report(ContestReport):
    report_id = "cumulative_difference"
    report_name = "Cumulative Difference"
    report_type = "plot"
    supports_pairwise = True

    def generate(self, output_path: str, **kwargs) -> str:
        metric = kwargs.get('metric', 'qsos')
        log1, log2 = self.logs[0], self.logs[1]
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')
        
        df1_ts, df2_ts = _prepare_time_series_data(log1, log2, metric)
        diff_ts = (df1_ts - df2_ts).dropna()

        if diff_ts.empty:
            return f"Skipping 160M difference plot: no data."

        fig, ax = _create_time_series_figure(log1, self.report_name)

        ax.plot(diff_ts.index, diff_ts, label=f'{call1} vs {call2}')
        ax.axhline(0, color='gray', linestyle='--', linewidth=1)
        ax.fill_between(diff_ts.index, diff_ts, where=diff_ts >= 0, facecolor='green', interpolate=True, alpha=0.3)
        ax.fill_between(diff_ts.index, diff_ts, where=diff_ts < 0, facecolor='red', interpolate=True, alpha=0.3)
        ax.set_ylabel(f"Difference in Cumulative {metric.capitalize()}")
        ax.legend(loc='upper left')

        callsign_str = f"{call1}_vs_{call2}"
        filename = f"{self.report_id}_{metric}_{callsign_str}.png"
        filepath = os.path.join(output_path, filename)

        try:
            create_output_directory(output_path)
            plt.savefig(filepath, bbox_inches='tight')
            plt.close(fig)
            return f"'{self.report_name}' for {callsign_str} saved to {filepath}"
        except Exception as e:
            plt.close(fig)
            return f"Error generating report '{self.report_name}' for {callsign_str}: {e}"