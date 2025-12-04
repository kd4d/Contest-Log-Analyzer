# contest_tools/reports/chart_qso_breakdown.py
#
# Purpose: A chart report that generates a stacked bar chart comparing two logs
#          on common/unique QSOs broken down by Run vs. Search & Pounce (S&P) mode.
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
# - Refactored to use CategoricalAggregator.compute_comparison_breakdown.

from typing import List, Dict, Tuple
import pandas as pd
import matplotlib.pyplot as plt
from contest_tools.reports.report import Report
from contest_tools.data_models.contest_log import ContestLog
from contest_tools.data_aggregators.categorical_stats import CategoricalAggregator # New Import
from contest_tools.styles.mpl_style_manager import MPLStyleManager

class ChartQSOBreakdown(Report):
    """
    Generates a stacked bar chart comparing two logs on common/unique QSOs
    broken down by Run vs. Search & Pounce (S&P) mode for each band.
    """

    def __init__(self, logs: List[ContestLog]):
        """
        Initializes the report. Requires exactly two logs for comparison.

        Args:
            logs: A list containing exactly two ContestLog objects.
        """
        super().__init__(logs)
        self.report_id = 'chart_qso_breakdown'
        if len(logs) != 2:
            raise ValueError("ChartQSOBreakdown requires exactly two logs for comparison.")
        self.log1 = logs[0]
        self.log2 = logs[1]
        self.aggregator = CategoricalAggregator() # Instantiate the new aggregator

    def _prepare_data(self, band: str) -> Dict:
        """
        Aggregates data for a specific band using CategoricalAggregator.

        Args:
            band: The band name (e.g., '20M').

        Returns:
            A dictionary of aggregated data ready for plotting.
        """
        # Call the new aggregator method for set comparison breakdown
        comparison_data = self.aggregator.compute_comparison_breakdown(
            self.log1, 
            self.log2, 
            band_filter=band
        )
        
        # Structure the data for the stacked bar chart
        # Categories: Unique 1, Common, Unique 2
        categories = [
            f"Unique {self.log1.callsign}",
            "Common (Both Logs)",
            f"Unique {self.log2.callsign}"
        ]
        
        # Modes/Components: Run, S&P, Mixed/Unk
        modes = ['Run', 'S&P', 'Mixed/Unk']
        
        # Data mapping from aggregator output to chart components
        # Index 0: Log 1 Unique
        # Index 1: Common
        # Index 2: Log 2 Unique
        data = {
            'Run': [
                comparison_data['log1_unique']['run'],
                comparison_data['common']['run_both'],
                comparison_data['log2_unique']['run']
            ],
            'S&P': [
                comparison_data['log1_unique']['sp'],
                comparison_data['common']['sp_both'],
                comparison_data['log2_unique']['sp']
            ],
            'Mixed/Unk': [
                comparison_data['log1_unique']['unk'],
                comparison_data['common']['mixed'],
                comparison_data['log2_unique']['unk']
            ]
        }
        
        return {
            'categories': categories,
            'modes': modes,
            'data': data
        }


    def generate(self, output_dir: str) -> List[str]:
        """
        Generates the stacked bar chart report and saves it to a file.
        
        Args:
            output_dir: The directory to save the report to.
            
        Returns:
            A list of generated file paths.
        """
        df1 = self.log1.get_valid_dataframe()
        df2 = self.log2.get_valid_dataframe()

        # Get the union of bands from both logs
        bands = sorted(set(df1['Band'].unique()) | set(df2['Band'].unique()))

        if not bands:
            return []

        # Calculate the grid size
        num_bands = len(bands)
        cols = min(3, num_bands)
        rows = (num_bands + cols - 1) // cols

        # Setup plot dimensions (adjusted for more horizontal space)
        fig_width = 6 * cols
        fig_height = 4.5 * rows
        
        fig, axes = plt.subplots(rows, cols, figsize=(fig_width, fig_height), sharey=True)
        
        # Flatten axes array if it's 2D
        if num_bands > 1:
            axes = axes.flatten()
        elif num_bands == 1:
            axes = [axes] # Ensure it's iterable if only one subplot

        # Get the colors from the style manager
        colors = MPLStyleManager.get_qso_mode_colors()
        
        # Plot each band
        for i, band in enumerate(bands):
            ax = axes[i]
            
            # Use the refactored data preparation function
            data_dict = self._prepare_data(band)
            categories = data_dict['categories']
            modes = data_dict['modes']
            data = data_dict['data']
            
            # Prepare for stacking
            x_pos = range(len(categories))
            bottom_data = [0] * len(categories)
            
            # Plot each mode in the stack
            for j, mode in enumerate(modes):
                current_data = data[mode]
                ax.bar(
                    x_pos, 
                    current_data, 
                    bottom=bottom_data, 
                    label=mode, 
                    color=colors[mode]
                )
                # Update bottom for the next stack
                bottom_data = [bottom_data[k] + current_data[k] for k in range(len(categories))]

            # Configure the axes
            ax.set_xticks(x_pos)
            ax.set_xticklabels(categories, rotation=45, ha="right", fontsize=8)
            ax.set_title(f"{band} Band Breakdown", fontsize=11, weight='bold')
            ax.yaxis.grid(True, linestyle='--', alpha=0.7)
            
            # Add a legend only to the first plot
            if i == 0:
                ax.legend(title="QSO Mode", loc='upper left', bbox_to_anchor=(1.05, 1), fontsize=8)

        # Remove unused subplots
        for i in range(num_bands, rows * cols):
            fig.delaxes(axes[i])
            
        # Final layout adjustments
        fig.suptitle(f"QSO Set Comparison: {self.log1.callsign} vs. {self.log2.callsign}", 
                     fontsize=16, weight='bold')
        fig.tight_layout(rect=[0, 0, 1, 0.96]) # Adjust for suptitle

        # Save the figure
        output_path = self.get_output_path(output_dir, file_ext='png', callsigns=f"{self.log1.callsign}_{self.log2.callsign}")
        fig.savefig(output_path)
        plt.close(fig)

        return [output_path]