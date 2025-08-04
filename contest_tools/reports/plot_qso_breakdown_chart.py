# Contest Log Analyzer/contest_tools/reports/plot_qso_breakdown_chart.py
#
# Purpose: Generates a sunburst chart showing the QSO breakdown by band
#          and Run/S&P/Unknown status.
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

class QsoBreakdownChart(ReportInterface):
    report_name = "QSO Breakdown Chart"
    report_id = "qso_breakdown_chart"
    report_type = 'chart'

    supports_single = True
    supports_multi = True
    supports_pairwise = False

    def generate(self, output_path: str, **kwargs) -> str:
        if not self.logs:
            return "No logs available for this report."

        # This report is complex to do comparatively in matplotlib, so we'll do one per log
        output_files = []
        for log in self.logs:
            my_call = log.get_metadata().get('MyCall', 'UnknownCall')
            df = log.get_processed_data()
            df_no_dupes = df[df['Dupe'] == False]

            breakdown = df_no_dupes.groupby(['Band', 'Run']).size().unstack(fill_value=0)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            breakdown.plot(kind='bar', stacked=True, ax=ax)
            
            ax.set_title(f'QSO Breakdown by Band and Type for {my_call}')
            ax.set_xlabel('Band')
            ax.set_ylabel('QSO Count')
            ax.tick_params(axis='x', rotation=45)
            ax.legend(title='Type')
            
            plt.tight_layout()

            filename = f"{self.report_id}_{my_call}.png"
            filepath = self._save_figure(fig, output_path, filename)
            output_files.append(filepath)
        
        return f"QSO breakdown chart(s) saved to:\n" + "\n".join([f"  - {fp}" for fp in output_files])