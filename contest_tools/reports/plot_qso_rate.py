# Contest Log Analyzer/contest_tools/reports/plot_qso_rate.py
#
# Purpose: A plot report that generates a cumulative QSO rate chart for one
#          or more logs over time.
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
    report_id = "qso_rate"
    report_name = "QSO Rate"
    report_type = "plot"
    supports_multi = True

    def generate(self, output_path: str, **kwargs) -> str:
        fig, ax = _create_time_series_figure(self.logs[0], self.report_name)
        
        all_calls = []
        for log in self.logs:
            callsign = log.get_metadata().get('MyCall', 'Log')
            all_calls.append(callsign)
            df_ts, _ = _prepare_time_series_data(log, None, 'qsos')
            ax.plot(df_ts.index, df_ts, label=callsign)

        ax.set_ylabel("Cumulative QSOs")
        ax.legend(loc='upper left')
        
        callsign_str = '_'.join(sorted(all_calls))
        filename = f"{self.report_id}_{callsign_str}.png"
        filepath = os.path.join(output_path, filename)
        
        try:
            create_output_directory(output_path)
            plt.savefig(filepath, bbox_inches='tight')
            plt.close(fig)
            return f"'{self.report_name}' for {callsign_str} saved to {filepath}"
        except Exception as e:
            plt.close(fig)
            return f"Error generating report '{self.report_name}' for {callsign_str}: {e}"