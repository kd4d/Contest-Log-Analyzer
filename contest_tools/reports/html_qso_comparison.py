# contest_tools/reports/html_qso_comparison.py
#
# Purpose: An HTML table report comparing two logs on unique vs. common QSOs
#          for each band and providing totals.
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
#   saving the HTML file.

import os
from typing import List, Dict, Union
import pandas as pd
from jinja2 import Environment, PackageLoader, select_autoescape
from contest_tools.reports.report_interface import ContestReport
from contest_tools.contest_log import ContestLog
from contest_tools.data_aggregators.categorical_stats import CategoricalAggregator
from contest_tools.reports._report_utils import get_valid_dataframe, create_output_directory

class Report(ContestReport):
    """
    Generates an HTML table comparing two logs' QSO sets (unique/common)
    broken down by band.
    """
    report_id = 'html_qso_comparison'
    report_name = 'HTML QSO Comparison'
    report_type = 'html'
    supports_pairwise = True

    def __init__(self, logs: List[ContestLog]):
        super().__init__(logs)
        if len(logs) != 2:
            raise ValueError("HtmlQsoComparison requires exactly two logs for comparison.")
        self.log1 = logs[0]
        self.log2 = logs[1]
        self.aggregator = CategoricalAggregator()
        
        # Jinja2 environment setup
        self.env = Environment(
            loader=PackageLoader('contest_tools', 'templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def _aggregate_data(self) -> Dict[str, Union[List[Dict], Dict]]:
        """Performs data aggregation."""
        df1 = get_valid_dataframe(self.log1)
        df2 = get_valid_dataframe(self.log2)

        bands = sorted(set(df1['Band'].unique()) | set(df2['Band'].unique()))
        band_rows: List[Dict] = []
        
        for band in bands:
            comp_data = self.aggregator.compute_comparison_breakdown(
                self.log1, 
                self.log2, 
                band_filter=band
            )
            metrics = comp_data['metrics']

            band_rows.append({
                'band': band,
                'log1_total': metrics['total_1'],
                'log2_total': metrics['total_2'],
                'log1_unique': metrics['unique_1'],
                'log2_unique': metrics['unique_2'],
                'common_total': metrics['common_total'],
                'log1_pct_unique': (metrics['unique_1'] / metrics['total_1']) * 100 if metrics['total_1'] else 0,
                'log2_pct_unique': (metrics['unique_2'] / metrics['total_2']) * 100 if metrics['total_2'] else 0,
                'log1_pct_common': (metrics['common_total'] / metrics['total_1']) * 100 if metrics['total_1'] else 0,
                'log2_pct_common': (metrics['common_total'] / metrics['total_2']) * 100 if metrics['total_2'] else 0,
            })
            
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
            'log1_pct_unique': (total_metrics['unique_1'] / total_metrics['total_1']) * 100 if total_metrics['total_1'] else 0,
            'log2_pct_unique': (total_metrics['unique_2'] / total_metrics['total_2']) * 100 if total_metrics['total_2'] else 0,
            'log1_pct_common': (total_metrics['common_total'] / total_metrics['total_1']) * 100 if total_metrics['total_1'] else 0,
            'log2_pct_common': (total_metrics['common_total'] / total_metrics['total_2']) * 100 if total_metrics['total_2'] else 0,
        }

        return {
            'band_rows': band_rows,
            'total_row': total_row
        }

    def generate(self, output_path: str, **kwargs) -> List[str]:
        if get_valid_dataframe(self.log1).empty and get_valid_dataframe(self.log2).empty:
            return []

        data = self._aggregate_data()
        template = self.env.get_template('html_qso_comparison.html')
        
        html_content = template.render(
            report_title=f"QSO Comparison Table: {self.log1.get_metadata().get('MyCall')} vs. {self.log2.get_metadata().get('MyCall')}",
            log1_callsign=self.log1.get_metadata().get('MyCall'),
            log2_callsign=self.log2.get_metadata().get('MyCall'),
            band_rows=data['band_rows'],
            total_row=data['total_row']
        )

        create_output_directory(output_path)
        call1 = self.log1.get_metadata().get('MyCall')
        call2 = self.log2.get_metadata().get('MyCall')
        filename = f"{self.report_id}_{call1}_{call2}.html"
        output_file = os.path.join(output_path, filename)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return [output_file]