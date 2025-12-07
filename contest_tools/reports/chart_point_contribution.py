# contest_tools/reports/chart_point_contribution.py
#
# Purpose: A chart report that generates a breakdown of total points by QSO
#          point value, comparing multiple logs side-by-side.
#
# Author: Gemini AI
# Date: 2025-12-04
# Version: 0.93.7-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# --- Revision History ---
# [0.93.7-Beta] - 2025-12-04
# - Fixed runtime crash by ensuring the output directory is created before
#   saving the chart file.

import os
from typing import List, Dict
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from contest_tools.reports.report_interface import ContestReport
from contest_tools.contest_log import ContestLog
from contest_tools.data_aggregators.categorical_stats import CategoricalAggregator
from contest_tools.styles.mpl_style_manager import MPLStyleManager
from contest_tools.reports._report_utils import create_output_directory

class Report(ContestReport):
    """
    Generates a comparative series of pie charts showing the breakdown of QSO points
    (1-point, 3-point, etc.) for each log (Totals).
    """
    report_id = 'chart_point_contribution'
    report_name = 'Point Contribution Breakdown'
    report_type = 'chart'
    supports_multi = True
    supports_pairwise = True

    def __init__(self, logs: List[ContestLog]):
        super().__init__(logs)
        self.aggregator = CategoricalAggregator()

    def _create_plot_for_log(self, callsign: str, log_data: Dict, ax: plt.Axes) -> None:
        """Creates a single pie chart for a specific log's total data."""
        point_breakdown = log_data['breakdown']
        
        if not point_breakdown:
            ax.text(0.5, 0.5, "No Data", 
                    ha='center', va='center', transform=ax.transAxes, color='gray')
            ax.set_title(callsign)
            return

        total_points = log_data['total_points']
        sorted_items = sorted(point_breakdown.items(), key=lambda item: item[1], reverse=True)
        sizes = [item[1] for item in sorted_items]
        labels = [f"{item[0]} Point ({item[1]})" for item in sorted_items]
        
        sorted_keys = [item[0] for item in sorted_items]
        color_map = MPLStyleManager.get_point_color_map(sorted_keys)
        colors = [color_map[k] for k in sorted_keys]
        
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=labels, 
            autopct='%1.1f%%', 
            startangle=90, 
            wedgeprops={'edgecolor': 'black', 'linewidth': 0.5},
            colors=colors
        )
        
        ax.axis('equal')
        ax.set_title(f"{callsign} (Total: {total_points:.0f})", fontsize=12, weight='bold')

    def generate(self, output_path: str, **kwargs) -> List[str]:
        # Get data for ALL logs, no filters (Grand Totals)
        agg_result = self.aggregator.get_points_breakdown(self.logs)
        
        num_logs = len(self.logs)
        cols = num_logs
        rows = 1

        fig_width = 5 * cols
        fig_height = 5
        
        fig = plt.figure(figsize=(fig_width, fig_height))
        gs = GridSpec(rows, cols, figure=fig)

        for i, log in enumerate(self.logs):
            callsign = log.get_metadata().get('MyCall', f'Log{i+1}')
            if callsign in agg_result['logs']:
                ax = fig.add_subplot(gs[0, i])
                self._create_plot_for_log(callsign, agg_result['logs'][callsign], ax)

        # Standard Title Construction
        first_log = self.logs[0]
        year = first_log.get_processed_data()['Date'].iloc[0].split('-')[0]
        contest_name = first_log.get_metadata().get('ContestName', 'Unknown')
        all_calls = sorted([l.get_metadata().get('MyCall') for l in self.logs])
        
        fig.suptitle(f"Comparative Point Contribution: {year} {contest_name} - {', '.join(all_calls)}", 
                     fontsize=16, weight='bold')
        fig.tight_layout(rect=[0, 0, 1, 0.90])

        create_output_directory(output_path)
        filename = f"{self.report_id}_{'_vs_'.join(all_calls)}.png"
        output_file = os.path.join(output_path, filename)
        
        fig.savefig(output_file)
        plt.close(fig)

        return [output_file]