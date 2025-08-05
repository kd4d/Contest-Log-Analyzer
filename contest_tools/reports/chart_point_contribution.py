# Contest Log Analyzer/contest_tools/reports/chart_point_contribution.py
#
# Purpose: Generates a comparative report with side-by-side pie charts and tables
#          showing the breakdown of QSO points for two logs.
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
import pandas as pd
import os
import logging

class Report(ContestReport):
    """
    Generates a comparative report with side-by-side pie charts showing QSO point contributions.
    """
    report_id = "chart_point_contribution"
    report_name = "Point Contribution Breakdown (Comparative)"
    report_type = "chart"
    supports_single = False
    supports_pairwise = True
    supports_multi = False

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the pie charts and tables.
        """
        create_output_directory(output_path)
        include_dupes = kwargs.get('include_dupes', False)
        
        if len(self.logs) != 2:
            return f"Report '{self.report_name}' requires exactly two logs for comparison. Skipping."

        log1, log2 = self.logs[0], self.logs[1]
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')
        
        df1 = get_valid_dataframe(log1, include_dupes)
        df2 = get_valid_dataframe(log2, include_dupes)

        if df1['QSOPoints'].sum() == 0 and df2['QSOPoints'].sum() == 0:
            return f"Skipping '{self.report_name}': No QSO points found in either log."

        fig, axes = plt.subplots(1, 2, figsize=(16, 7))
        fig.suptitle(f'QSO Point Contribution: {call1} vs {call2}', fontsize=16)

        # --- Process and Plot for Log 1 ---
        point_counts1 = df1['QSOPoints'].value_counts().sort_index()
        total_qsos1 = point_counts1.sum()
        point_labels1 = [f'{idx}-pt\n({val:,.0f} QSOs)' for idx, val in point_counts1.items()]
        
        wedges1, texts1, autotexts1 = axes[0].pie(
            point_counts1, labels=point_labels1, autopct=lambda p: f'{p:.1f}%',
            startangle=90, textprops={'fontsize': 10}, wedgeprops={'edgecolor': 'white'}
        )
        axes[0].set_title(f'{call1}\nTotal Points: {df1["QSOPoints"].sum():,.0f}', fontsize=12)
        plt.setp(autotexts1, size=10, weight="bold", color="white")

        # --- Process and Plot for Log 2 ---
        point_counts2 = df2['QSOPoints'].value_counts().sort_index()
        total_qsos2 = point_counts2.sum()
        point_labels2 = [f'{idx}-pt\n({val:,.0f} QSOs)' for idx, val in point_counts2.items()]
        
        wedges2, texts2, autotexts2 = axes[1].pie(
            point_counts2, labels=point_labels2, autopct=lambda p: f'{p:.1f}%',
            startangle=90, textprops={'fontsize': 10}, wedgeprops={'edgecolor': 'white'}
        )
        axes[1].set_title(f'{call2}\nTotal Points: {df2["QSOPoints"].sum():,.0f}', fontsize=12)
        plt.setp(autotexts2, size=10, weight="bold", color="white")
        
        # --- Create Summary Table ---
        summary_data1 = self._prepare_summary_data(point_counts1, df1["QSOPoints"].sum())
        summary_data2 = self._prepare_summary_data(point_counts2, df2["QSOPoints"].sum())
        
        table_data = []
        all_point_levels = sorted(list(set(summary_data1.keys()) | set(summary_data2.keys()) - {'TOTAL', 'AVG'}))

        for level in all_point_levels:
            row = [f'{level}-PT QSOs', f'{summary_data1.get(level, 0):,.0f}', f'{summary_data2.get(level, 0):,.0f}']
            table_data.append(row)
        
        table_data.append(['-'*15, '-'*15, '-'*15])
        table_data.append(['TOTAL QSOs', f'{summary_data1.get("TOTAL", 0):,.0f}', f'{summary_data2.get("TOTAL", 0):,.0f}'])
        table_data.append(['AVG PTS/QSO', f'{summary_data1.get("AVG", 0.0):.2f}', f'{summary_data2.get("AVG", 0.0):.2f}'])
        
        table = fig.table(
            cellText=table_data,
            colLabels=['Metric', call1, call2],
            loc='bottom',
            cellLoc='center',
            bbox=[0.1, -0.2, 0.8, 0.25]
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)

        # --- Final Adjustments and Save ---
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.subplots_adjust(bottom=0.2)
        
        output_filename = os.path.join(output_path, f"{self.report_id}_{call1}_{call2}.png")
        try:
            plt.savefig(output_filename, bbox_inches='tight', dpi=150)
            plt.close(fig)
            logging.info(f"Successfully generated '{self.report_name}' and saved to {output_filename}")
            return f"'{self.report_name}' saved to {output_filename}"
        except Exception as e:
            logging.error(f"Error saving chart: {e}")
            plt.close(fig)
            return f"Error generating report '{self.report_name}'"

    def _prepare_summary_data(self, point_counts, total_points):
        data = {level: count for level, count in point_counts.items()}
        total_qsos = point_counts.sum()
        data['TOTAL'] = total_qsos
        data['AVG'] = total_points / total_qsos if total_qsos > 0 else 0
        return data