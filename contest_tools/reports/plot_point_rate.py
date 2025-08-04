# Contest Log Analyzer/contest_tools/reports/plot_point_rate.py
#
# Purpose: Generates a plot showing the point rate (points per hour)
#          for multiple logs.
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
from .report_interface import ReportInterface

class PointRatePlots(ReportInterface):
    report_name = "Point Rate Comparison Plots"
    report_id = "point_rate_plots"
    report_type = 'plot'

    supports_single = False
    supports_multi = True
    supports_pairwise = False

    def generate(self, output_path: str, **kwargs) -> str:
        if not self.logs:
            return "No logs available to generate point rate plots."

        fig, ax = plt.subplots(figsize=(10, 6))
        
        for log in self.logs:
            my_call = log.get_metadata().get('MyCall', 'UnknownCall')
            df = log.get_processed_data()
            df_no_dupes = df[df['Dupe'] == False]
            
            point_rate = df_no_dupes.set_index('Datetime')['QSOPoints'].resample('H').sum()
            
            ax.plot(point_rate.index, point_rate.values, marker='o', linestyle='-', label=my_call)

        ax.set_title('Point Rate Comparison (Points per Hour)')
        ax.set_xlabel('Contest Time')
        ax.set_ylabel('Points per Hour')
        ax.legend()
        ax.grid(True)
        
        plt.tight_layout()
        
        all_calls = sorted([log.get_metadata().get('MyCall', f'Log{i+1}') for i, log in enumerate(self.logs)])
        combo_id = '_vs_'.join(all_calls)

        filename = f"{self.report_id}_all_plot.png"
        filepath = self._save_figure(fig, output_path, filename)

        return f"Point rate plots saved to:\n  - {filepath}"