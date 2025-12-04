# contest_tools/reports/chart_point_contribution_single.py
#
# Purpose: A single-chart report that generates a breakdown of total points by QSO
#          point value for the entire log (all bands/modes combined).
#
# Author: Gemini AI
# Date: 2025-11-25
# Version: 0.91.13-Beta
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
# [0.91.13-Beta] - 2025-10-10
# - Changed: Corrected title generation to conform to the CLA Reports Style Guide.
# [0.90.0-Beta] - 2025-10-01
# Set new baseline version for release.
# [0.93.0-Beta] - 2025-11-25 (Refactor)
# - Refactored to use CategoricalAggregator.get_points_breakdown.

from typing import List
import matplotlib.pyplot as plt
from contest_tools.reports.report import Report
from contest_tools.data_models.contest_log import ContestLog
from contest_tools.data_aggregators.categorical_stats import CategoricalAggregator # New Import
from contest_tools.styles.mpl_style_manager import MPLStyleManager

class ChartPointContributionSingle(Report):
    """
    Generates a single pie chart showing the breakdown of QSO points
    for the entire log.
    """

    def __init__(self, logs: List[ContestLog]):
        """
        Initializes the report.

        Args:
            logs: A list of ContestLog objects.
        """
        super().__init__(logs)
        self.report_id = 'chart_point_contribution_single'
        self.aggregator = CategoricalAggregator() # Instantiate the new aggregator

    def generate(self, output_dir: str) -> List[str]:
        """
        Generates the single point contribution report and saves it to a file.
        
        Args:
            output_dir: The directory to save the report to.
            
        Returns:
            A list of generated file paths.
        """
        if not self.logs or self.logs[0].get_valid_dataframe().empty:
            return []

        # 1. Call the aggregator to get the total log breakdown dictionary
        # No band or mode filters are passed for the overall report.
        agg_result = self.aggregator.get_points_breakdown(self.logs)
        
        # 2. Extract the data for the breakdown
        # Assumes self.logs is always a single-element list for this report type.
        log_data = list(agg_result['logs'].values())[0] 
        point_breakdown = log_data['breakdown']
        total_points = log_data['total_points']

        if not point_breakdown:
            return []

        # Prepare data for the plot
        # Sort items by size (count) descending
        sorted_items = sorted(point_breakdown.items(), key=lambda item: item[1], reverse=True)
        
        sizes = [item[1] for item in sorted_items]
        # Label format: "PointValue Point (Count)"
        labels = [f"{item[0]} Point ({item[1]})" for item in sorted_items] 
        
        # Determine colors based on the point values (keys)
        sorted_keys = [item[0] for item in sorted_items]
        color_map = MPLStyleManager.get_point_color_map(sorted_keys)
        colors = [color_map[k] for k in sorted_keys]

        # Create the figure
        fig, ax = plt.subplots(figsize=(8, 8))

        # Draw the pie chart
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=labels, 
            autopct='%1.1f%%', 
            startangle=90, 
            wedgeprops={'edgecolor': 'black', 'linewidth': 0.5},
            colors=colors
        )
        
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        
        fig.suptitle(f"Total Point Contribution Breakdown: {self.logs[0].callsign}", 
                     fontsize=16, weight='bold')
        ax.set_title(f"Total QSOs: {log_data['total_qsos']:.0f} | Total Points: {total_points:.0f}", 
                     fontsize=12, pad=20)

        # Save the figure
        output_path = self.get_output_path(output_dir, file_ext='png')
        fig.savefig(output_path)
        plt.close(fig)

        return [output_path]