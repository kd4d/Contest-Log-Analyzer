# contest_tools/reports/chart_point_contribution_single.py
#
# Purpose: A chart report that generates a breakdown of total points by QSO
#          point value, presented as a series of pie charts per band for a SINGLE log.
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
from contest_tools.reports._report_utils import get_valid_dataframe, create_output_directory

class Report(ContestReport):
    """
    Generates a series of pie charts showing the breakdown of QSO points
    (1-point, 3-point, etc.) for each band in a single log.
    """
    report_id = 'chart_point_contribution_single'
    report_name = 'Point Contribution Breakdown (Single Log)'
    report_type = 'chart'
    supports_single = True

    def __init__(self, logs: List[ContestLog]):
        super().__init__(logs)
        self.aggregator = CategoricalAggregator()

    def _create_plot_for_band(self, band: str, ax: plt.Axes) -> None:
        """Creates a single pie chart for the given band data."""
        agg_result = self.aggregator.get_points_breakdown(self.logs, band_filter=band)
        
        log_data = list(agg_result['logs'].values())[0] 
        point_breakdown = log_data['breakdown']
    
        if not point_breakdown:
            ax.text(0.5, 0.5, "No Data for this Band", 
                    ha='center', va='center', transform=ax.transAxes, color='gray')
            ax.set_title(f"{band} Band Points")
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
        ax.set_title(f"{band} Band Points (Total: {total_points:.0f})", fontsize=10, weight='bold')

    def generate(self, output_path: str, **kwargs) -> List[str]:
        if not self.logs or get_valid_dataframe(self.logs[0]).empty:
            return []

        df = get_valid_dataframe(self.logs[0])
        bands = sorted(df['Band'].unique())

        if not bands:
            return []

        num_bands = len(bands)
        cols = min(4, num_bands)
        rows = (num_bands + cols - 1) // cols

        fig_width = 4 * cols
        fig_height = 4 * rows
        
        fig = plt.figure(figsize=(fig_width, fig_height))
        gs = GridSpec(rows, cols, figure=fig)

        for i, band in enumerate(bands):
            ax = fig.add_subplot(gs[i // cols, i % cols])
            self._create_plot_for_band(band, ax) 

        fig.suptitle(f"Point Contribution Breakdown: {self.logs[0].get_metadata().get('MyCall')}", 
                     fontsize=16, weight='bold')
        fig.tight_layout(rect=[0, 0, 1, 0.96])

        create_output_directory(output_path)
        callsign = self.logs[0].get_metadata().get('MyCall', 'Unknown')
        filename = f"{self.report_id}_{callsign}.png"
        output_file = os.path.join(output_path, filename)
        
        fig.savefig(output_file)
        plt.close(fig)

        return [output_file]