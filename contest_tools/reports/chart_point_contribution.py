# contest_tools/reports/chart_point_contribution.py
#
# Purpose: A chart report that generates a breakdown of total points by QSO
#          point value, presented as a series of pie charts.
#
# Author: Gemini AI
# Date: 2025-10-10
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

from typing import List, Dict
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from contest_tools.reports.report import Report
from contest_tools.data_models.contest_log import ContestLog
from contest_tools.data_aggregators.categorical_stats import CategoricalAggregator # New Import
from contest_tools.styles.mpl_style_manager import MPLStyleManager

class ChartPointContribution(Report):
    """
    Generates a series of pie charts showing the breakdown of QSO points
    (1-point, 3-point, etc.) for each band in the log.
    """

    def __init__(self, logs: List[ContestLog]):
        """
        Initializes the report.

        Args:
            logs: A list of ContestLog objects.
        """
        super().__init__(logs)
        self.report_id = 'chart_point_contribution'
        self.aggregator = CategoricalAggregator() # Instantiate the new aggregator

    def _create_plot_for_band(self, band: str, ax: plt.Axes) -> None:
        """
        Creates a single pie chart for the given band data on the provided axes.
        
        Args:
            band: The band name (e.g., '20M').
            ax: The matplotlib Axes object to draw on.
        """
        
        # 1. Call the aggregator to get the breakdown dictionary
        # This report is for a single log, so we pass self.logs (which should contain one log)
        agg_result = self.aggregator.get_points_breakdown(self.logs, band_filter=band)
        
        # 2. Extract the data for the breakdown
        # Assumes self.logs is always a single-element list for this report type.
        log_data = list(agg_result['logs'].values())[0] 
        point_breakdown = log_data['breakdown']
        
        if not point_breakdown:
            ax.text(0.5, 0.5, "No Data for this Band", 
                    ha='center', va='center', transform=ax.transAxes, color='gray')
            ax.set_title(f"{band} Band Points")
            return

        # Prepare labels and values for the pie chart
        total_points = log_data['total_points']
        
        # Sort items by size (count) descending
        sorted_items = sorted(point_breakdown.items(), key=lambda item: item[1], reverse=True)
        sizes = [item[1] for item in sorted_items]
        labels = [f"{item[0]} Point ({item[1]})" for item in sorted_items]
        
        # Get colors based on the sorted point values (keys)
        sorted_keys = [item[0] for item in sorted_items]
        color_map = MPLStyleManager.get_point_color_map(sorted_keys)
        colors = [color_map[k] for k in sorted_keys]
        
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
        ax.set_title(f"{band} Band Points (Total: {total_points:.0f})", fontsize=10, weight='bold')

    def generate(self, output_dir: str) -> List[str]:
        """
        Generates the point contribution report and saves it to a file.
        
        Args:
            output_dir: The directory to save the report to.
            
        Returns:
            A list of generated file paths.
        """
        if not self.logs or self.logs[0].get_valid_dataframe().empty:
            return []

        # Get all bands with QSOs
        df = self.logs[0].get_valid_dataframe()
        bands = sorted(df['Band'].unique())

        if not bands:
            return []

        # Calculate the grid size
        num_bands = len(bands)
        cols = min(4, num_bands)
        rows = (num_bands + cols - 1) // cols

        # Setup plot dimensions
        fig_width = 4 * cols
        fig_height = 4 * rows
        
        fig = plt.figure(figsize=(fig_width, fig_height))
        
        # Use GridSpec for better control over subplot placement
        gs = GridSpec(rows, cols, figure=fig)

        # Plot each band
        for i, band in enumerate(bands):
            ax = fig.add_subplot(gs[i // cols, i % cols])
            
            # Call the updated plot method
            self._create_plot_for_band(band, ax) 

        # Final layout adjustments
        fig.suptitle(f"Point Contribution Breakdown: {self.logs[0].callsign}", 
                     fontsize=16, weight='bold')
        fig.tight_layout(rect=[0, 0, 1, 0.96]) # Adjust for suptitle

        # Save the figure
        output_path = self.get_output_path(output_dir, file_ext='png')
        fig.savefig(output_path)
        plt.close(fig)

        return [output_path]