# Contest Log Analyzer/contest_tools/reports/plot_cumulative_difference.py
#
# Purpose: Generates a plot showing the cumulative difference in QSO/Point
#          counts over time between two logs.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-04
# Version: 0.30.4-Beta
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
## [0.30.4-Beta] - 2025-08-04
### Changed
# - Reverted plotting functions from Plotly back to Matplotlib and Seaborn.
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from .report_interface import ReportInterface

class CumulativeDifferencePlots(ReportInterface):
    report_name = "Cumulative Difference Plots"
    report_id = "cumulative_difference_plots"
    report_type = 'plot'

    supports_single = False
    supports_multi = False
    supports_pairwise = True

    def generate(self, output_path: str, **kwargs) -> str:
        if not self.logs or len(self.logs) < 2:
            return "This report requires two logs for comparison."

        log1, log2 = self.logs[0], self.logs[1]
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')
        metric = kwargs.get('metric', 'qsos') # Default to qsos

        df1 = log1.get_processed_data()
        df2 = log2.get_processed_data()
        df1_no_dupes = df1[df1['Dupe'] == False]
        df2_no_dupes = df2[df2['Dupe'] == False]

        all_times = pd.to_datetime(pd.concat([df1_no_dupes['Datetime'], df2_no_dupes['Datetime']]).unique()).sort_values()

        if metric == 'points':
            data1 = df1_no_dupes.set_index('Datetime')['QSOPoints'].reindex(all_times).fillna(0).cumsum()
            data2 = df2_no_dupes.set_index('Datetime')['QSOPoints'].reindex(all_times).fillna(0).cumsum()
            yaxis_title = 'Cumulative Point Difference'
            title = f'Cumulative Point Difference: {call1} vs {call2}'
        else:
            data1 = df1_no_dupes.set_index('Datetime').reindex(all_times).notna().cumsum()['Call']
            data2 = df2_no_dupes.set_index('Datetime').reindex(all_times).notna().cumsum()['Call']
            yaxis_title = 'Cumulative QSO Difference'
            title = f'Cumulative QSO Difference: {call1} vs {call2}'

        difference = data1 - data2

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(all_times, difference)
        ax.axhline(0, color='gray', linestyle='--')
        
        ax.set_title(title)
        ax.set_xlabel('Contest Time')
        ax.set_ylabel(yaxis_title)
        
        plt.tight_layout()

        filename = f"diff_{metric}_all_{call1}_vs_{call2}.png"
        filepath = self._save_figure(fig, output_path, filename)
        
        return f"Cumulative difference plots for {metric} saved to:\n  - {filepath}"