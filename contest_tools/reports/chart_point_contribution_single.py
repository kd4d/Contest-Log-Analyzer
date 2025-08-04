# Contest Log Analyzer/contest_tools/reports/chart_point_contribution_single.py
#
# Purpose: Generates a pie chart showing the point contribution of each
#          continent for a single log file.
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
# - Reverted chart generation from Plotly back to Matplotlib/Seaborn.
import pandas as pd
import matplotlib.pyplot as plt
from .report_interface import ReportInterface

class PointContributionChartSingle(ReportInterface):
    report_name = "Single Log Point Contribution"
    report_id = "chart_point_contribution_single"
    report_type = 'chart'
    
    supports_single = True
    supports_multi = False
    supports_pairwise = False

    def generate(self, output_path: str, **kwargs) -> str:
        if not self.logs:
            return "No log available for this report."

        log = self.logs[0]
        my_call = log.get_metadata().get('MyCall', 'UnknownCall')
        df = log.get_processed_data()
        
        df_no_dupes = df[df['Dupe'] == False]
        points_by_continent = df_no_dupes.groupby('Continent')['QSOPoints'].sum()
        
        fig, ax = plt.subplots()
        ax.pie(points_by_continent, labels=points_by_continent.index, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        
        plt.title(f"Point Contribution by Continent for {my_call}")
        
        filename = f"{self.report_id}_{my_call}.png"
        filepath = self._save_figure(fig, output_path, filename)
        
        return f"Chart saved to: {filepath}"