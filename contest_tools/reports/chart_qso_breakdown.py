# contest_tools/reports/chart_qso_breakdown.py
#
# Purpose: A chart report that generates a stacked bar chart comparing two logs
#          on common/unique QSOs broken down by Run vs. Search & Pounce (S&P) mode.
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
from typing import List, Dict, Tuple
import pandas as pd
import matplotlib.pyplot as plt
from contest_tools.reports.report_interface import ContestReport
from contest_tools.contest_log import ContestLog
from contest_tools.data_aggregators.categorical_stats import CategoricalAggregator
from contest_tools.styles.mpl_style_manager import MPLStyleManager
from contest_tools.reports._report_utils import get_valid_dataframe, create_output_directory

class Report(ContestReport):
    """
    Generates a stacked bar chart comparing two logs on common/unique QSOs
    broken down by Run vs. Search & Pounce (S&P) mode for each band.
    """
    report_id = 'qso_breakdown_chart' # Aligned with Interpretation Guide
    report_name = 'QSO Breakdown Chart'
    report_type = 'chart'
    supports_pairwise = True

    def __init__(self, logs: List[ContestLog]):
        super().__init__(logs)
        if len(logs) != 2:
            raise ValueError("ChartQSOBreakdown requires exactly two logs for comparison.")
        self.log1 = logs[0]
        self.log2 = logs[1]
        self.aggregator = CategoricalAggregator()

    def _prepare_data(self, band: str) -> Dict:
        """
        Aggregates data for a specific band using CategoricalAggregator.
        """
        comparison_data = self.aggregator.compute_comparison_breakdown(
            self.log1, 
            self.log2, 
            band_filter=band
        )
        
        categories = [
            f"Unique {self.log1.get_metadata().get('MyCall')}",
            "Common (Both Logs)",
            f"Unique {self.log2.get_metadata().get('MyCall')}"
        ]
        
        modes = ['Run', 'S&P', 'Mixed/Unk']
        
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


    def generate(self, output_path: str, **kwargs) -> List[str]:
        """
        Generates the stacked bar chart report and saves it to a file.
        """
        df1 = get_valid_dataframe(self.log1)
        df2 = get_valid_dataframe(self.log2)

        bands = sorted(set(df1['Band'].unique()) | set(df2['Band'].unique()))

        if not bands:
            return []

        num_bands = len(bands)
        cols = min(3, num_bands)
        rows = (num_bands + cols - 1) // cols

        fig_width = 6 * cols
        fig_height = 4.5 * rows
        
        fig, axes = plt.subplots(rows, cols, figsize=(fig_width, fig_height), sharey=True)
        
        if num_bands > 1:
            axes = axes.flatten()
        elif num_bands == 1:
            axes = [axes] 

        colors = MPLStyleManager.get_qso_mode_colors()

        for i, band in enumerate(bands):
            ax = axes[i]
            
            data_dict = self._prepare_data(band)
            categories = data_dict['categories']
            modes = data_dict['modes']
            data = data_dict['data']
            
            x_pos = range(len(categories))
            bottom_data = [0] * len(categories)
            
            for j, mode in enumerate(modes):
                current_data = data[mode]
                ax.bar(
                    x_pos, 
                    current_data, 
                    bottom=bottom_data, 
                    label=mode, 
                    color=colors[mode]
                )
                bottom_data = [bottom_data[k] + current_data[k] for k in range(len(categories))]

            ax.set_xticks(x_pos)
            ax.set_xticklabels(categories, rotation=45, ha="right", fontsize=8)
            ax.set_title(f"{band} Band Breakdown", fontsize=11, weight='bold')
            ax.yaxis.grid(True, linestyle='--', alpha=0.7)
            
            if i == 0:
                ax.legend(title="QSO Mode", loc='upper left', bbox_to_anchor=(1.05, 1), fontsize=8)

        for i in range(num_bands, rows * cols):
            fig.delaxes(axes[i])
            
        fig.suptitle(f"QSO Set Comparison: {self.log1.get_metadata().get('MyCall')} vs. {self.log2.get_metadata().get('MyCall')}", 
                     fontsize=16, weight='bold')
        fig.tight_layout(rect=[0, 0, 1, 0.96])

        create_output_directory(output_path)
        call1 = self.log1.get_metadata().get('MyCall')
        call2 = self.log2.get_metadata().get('MyCall')
        filename = f"{self.report_id}_{call1}_{call2}.png"
        output_file = os.path.join(output_path, filename)
        
        fig.savefig(output_file)
        plt.close(fig)

        return [output_file]