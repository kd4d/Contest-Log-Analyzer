# Contest Log Analyzer/contest_tools/reports/chart_point_contribution.py
#
# Purpose: Generates a stacked bar chart showing the point contribution
#          of each continent for a multi-log comparison.
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
import seaborn as sns
from .report_interface import ReportInterface

class PointContributionChart(ReportInterface):
    report_name = "Point Contribution Breakdown"
    report_id = "chart_point_contribution"
    report_type = 'chart'

    supports_single = False
    supports_multi = True
    supports_pairwise = False

    def generate(self, output_path: str, **kwargs) -> str:
        if not self.logs or len(self.logs) < 2:
            return "This report requires at least two logs for comparison."

        all_calls = [log.get_metadata().get('MyCall', f'Log {i+1}') for i, log in enumerate(self.logs)]
        
        continent_points = {call: {} for call in all_calls}
        continents = set()

        for i, log in enumerate(self.logs):
            df = log.get_processed_data()
            df_no_dupes = df[df['Dupe'] == False]
            
            points_by_cont = df_no_dupes.groupby('Continent')['QSOPoints'].sum().to_dict()
            call = all_calls[i]
            
            for cont, points in points_by_cont.items():
                continent_points[call][cont] = points
                continents.add(cont)
        
        sorted_continents = sorted(list(continents))

        df_plot = pd.DataFrame(continent_points).fillna(0).T
        df_plot = df_plot[sorted_continents]

        fig, ax = plt.subplots(figsize=(10, 6))
        df_plot.plot(kind='bar', stacked=True, ax=ax)

        ax.set_title('Point Contribution by Continent', fontsize=16)
        ax.set_xlabel('Callsign')
        ax.set_ylabel('Total Points')
        ax.tick_params(axis='x', rotation=0)
        ax.legend(title='Continent')
        
        plt.tight_layout()
        
        combo_id = '_vs_'.join(sorted(all_calls))
        filename = f"{self.report_id}_all bands_{combo_id}.png"
        filepath = self._save_figure(fig, output_path, filename)

        return f"Point Contribution charts saved to:\n  - {filepath}"