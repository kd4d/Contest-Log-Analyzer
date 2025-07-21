# Contest Log Analyzer/contest_tools/reports/plot_qso_rate.py
#
# Purpose: An example plot report that generates a QSO rate graph.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-21
# Version: 0.10.0-Beta
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
# All notable changes to this project will be documented in this file.
# The format is based on "Keep a Changelog" (https://keepachangelog.com/en/1.0.0/),
# and this project aims to adhere to Semantic Versioning (https://semver.org/).

## [0.10.0-Beta] - 2025-07-21
# - Initial release of the QSO rate plot report.

### Changed
# - (None)

### Fixed
# - (None)

### Removed
# - (None)

from typing import List
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a plot comparing the QSO rates of the selected logs.
    """
    @property
    def report_id(self) -> str:
        return "qso_rate"

    @property
    def report_name(self) -> str:
        return "QSO Rate Comparison"

    @property
    def report_type(self) -> str:
        return "plot"

    def generate(self, output_path: str) -> str:
        sns.set_theme(style="whitegrid")
        plt.figure(figsize=(12, 7))

        for log in self.logs:
            callsign = log.get_metadata().get('MyCall', 'Unknown')
            df = log.get_processed_data()
            
            # Resample QSOs into 10-minute bins to calculate rate
            rate = df.set_index('Datetime').resample('10T').size()
            
            # Calculate cumulative QSOs for the plot
            cumulative_qsos = rate.cumsum()
            
            plt.plot(cumulative_qsos.index, cumulative_qsos, label=f'{callsign} Rate')

        plt.title(self.report_name)
        plt.xlabel("Contest Time")
        plt.ylabel("Total QSOs")
        plt.legend()
        plt.grid(True)
        
        # Ensure the output directory exists
        os.makedirs(output_path, exist_ok=True)
        
        # Save the plot to a file
        filename = f"{self.report_id}_plot.png"
        filepath = os.path.join(output_path, filename)
        plt.savefig(filepath)
        plt.close() # Close the plot to free memory

        print(f"Plot saved to: {filepath}")
        return filename
