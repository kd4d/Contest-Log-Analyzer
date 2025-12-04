# contest_tools/reports/html_qso_comparison.py
#
# Purpose: An HTML table report comparing two logs on unique vs. common QSOs
#          for each band and providing totals.
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

from typing import List, Dict, Union
import pandas as pd
from jinja2 import Environment, PackageLoader, select_autoescape
from contest_tools.reports.report import Report
from contest_tools.data_models.contest_log import ContestLog
from contest_tools.data_aggregators.categorical_stats import CategoricalAggregator # New Import

class HtmlQsoComparison(Report):
    """
    Generates an HTML table comparing two logs' QSO sets (unique/common)
    broken down by band.
    """

    def __init__(self, logs: List[ContestLog]):
        """
        Initializes the report. Requires exactly two logs for comparison.

        Args:
            logs: A list containing exactly two ContestLog objects.
        """
        super().__init__(logs)
        self.report_id = 'html_qso_comparison'
        if len(logs) != 2:
            raise ValueError("HtmlQsoComparison requires exactly two logs for comparison.")
        self.log1 = logs[0]
        self.log2 = logs[1]
        self.aggregator = CategoricalAggregator() # Instantiate the new aggregator
        
        # Jinja2 environment setup
        # Note: PackageLoader needs the base package name and the templates subfolder
        # Assuming 'contest_tools' is the package root and 'templates' holds HTML templates.
        self.env = Environment(
            loader=PackageLoader('contest_tools', 'templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def _aggregate_data(self) -> Dict[str, Union[List[Dict], Dict]]:
        """
        Performs the data aggregation and comparison for all bands and totals.
        
        Returns:
            A dictionary containing 'band_rows' (List of Dicts) and 'total_row' (Dict).
        """
        df1 = self.log1.get_valid_dataframe()
        df2 = self.log2.get_valid_dataframe()

        # Get the union of bands from both logs
        bands = sorted(set(df1['Band'].unique()) | set(df2['Band'].unique()))
        
        band_rows: List[Dict] = []
        
        # 1. Loop bands and call the aggregator
        for band in bands:
            # Call the aggregator method for comparison breakdown, filtered by band
            comp_data = self.aggregator.compute_comparison_breakdown(
                self.log1, 
                self.log2, 
                band_filter=band
            )
            metrics = comp_data['metrics']

            # Format the output row
            band_rows.append({
                'band': band,
                'log1_total': metrics['total_1'],
                'log2_total': metrics['total_2'],
                'log1_unique': metrics['unique_1'],
                'log2_unique': metrics['unique_2'],
                'common_total': metrics['common_total'],
                # Calculations for percentages
                'log1_pct_unique': (metrics['unique_1'] / metrics['total_1']) * 100 if metrics['total_1'] else 0,
                'log2_pct_unique': (metrics['unique_2'] / metrics['total_2']) * 100 if metrics['total_2'] else 0,
                'log1_pct_common': (metrics['common_total'] / metrics['total_1']) * 100 if metrics['total_1'] else 0,
                'log2_pct_common': (metrics['common_total'] / metrics['total_2']) * 100 if metrics['total_2'] else 0,
            })
            
        # 2. Calculate "All Bands" total row
        # Call aggregator with no filters (band_filter=None)
        total_comp_data = self.aggregator.compute_comparison_breakdown(
            self.log1, 
            self.log2, 
            band_filter=None 
        )
        total_metrics = total_comp_data['metrics']
        
        total_row = {
            'band': 'All Bands',
            'log1_total': total_metrics['total_1'],
            'log2_total': total_metrics['total_2'],
            'log1_unique': total_metrics['unique_1'],
            'log2_unique': total_metrics['unique_2'],
            'common_total': total_metrics['common_total'],
            # Calculations for percentages
            'log1_pct_unique': (total_metrics['unique_1'] / total_metrics['total_1']) * 100 if total_metrics['total_1'] else 0,
            'log2_pct_unique': (total_metrics['unique_2'] / total_metrics['total_2']) * 100 if total_metrics['total_2'] else 0,
            'log1_pct_common': (total_metrics['common_total'] / total_metrics['total_1']) * 100 if total_metrics['total_1'] else 0,
            'log2_pct_common': (total_metrics['common_total'] / total_metrics['total_2']) * 100 if total_metrics['total_2'] else 0,
        }

        return {
            'band_rows': band_rows,
            'total_row': total_row
        }

    def generate(self, output_dir: str) -> List[str]:
        """
        Generates the HTML comparison table and saves it to a file.
        
        Args:
            output_dir: The directory to save the report to.
            
        Returns:
            A list of generated file paths.
        """
        if self.log1.get_valid_dataframe().empty and self.log2.get_valid_dataframe().empty:
            return []

        data = self._aggregate_data()
        
        # Load the template (The template is assumed to exist in the configured Jinja2 loader path)
        template = self.env.get_template('html_qso_comparison.html')
        
        html_content = template.render(
            report_title=f"QSO Comparison Table: {self.log1.callsign} vs. {self.log2.callsign}",
            log1_callsign=self.log1.callsign,
            log2_callsign=self.log2.callsign,
            band_rows=data['band_rows'],
            total_row=data['total_row']
        )

        # Save the HTML file
        output_path = self.get_output_path(output_dir, file_ext='html', callsigns=f"{self.log1.callsign}_{self.log2.callsign}")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return [output_path]