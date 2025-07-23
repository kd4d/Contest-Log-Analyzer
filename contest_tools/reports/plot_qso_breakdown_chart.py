# Contest Log Analyzer/contest_tools/reports/plot_qso_breakdown_chart.py
#
# Purpose: A plot report that generates a comparative QSO breakdown bar chart.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-23
# Version: 0.14.0-Beta
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
# All notable changes to this project will be documented in this file.
# The format is based on "Keep a Changelog" (https://keepachangelog.com/en/1.0.0/),
# and this project aims to adhere to Semantic Versioning (https://semver.org/).

## [0.14.0-Beta] - 2025-07-23
### Changed
# - The 'report_type' is now 'chart' to save output to the 'charts' directory.
# - Removed the "All Bands" summary bar from the plot to improve the scale
#   and readability of the band-by-band comparison.

from typing import List
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a stacked bar chart comparing the QSO breakdown (Run/S&P/Common)
    between two logs for each band.
    """
    @property
    def report_id(self) -> str:
        return "qso_breakdown_chart"

    @property
    def report_name(self) -> str:
        return "QSO Breakdown Chart"

    @property
    def report_type(self) -> str:
        return "chart"

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the plot. This report always excludes dupes.

        Args:
            output_path (str): The directory where the plot file should be saved.
            **kwargs: Accepts standard arguments but does not use them.
        """
        if len(self.logs) != 2:
            return "Error: The QSO Breakdown Chart report requires exactly two logs."

        log1, log2 = self.logs[0], self.logs[1]
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')

        bands = ['160M', '80M', '40M', '20M', '15M', '10M'] # Exclude 'All Bands'
        
        # --- Data Aggregation ---
        plot_data = {
            'bands': [b.replace('M', '') for b in bands],
            call1: {'run': [], 'sp': []},
            call2: {'run': [], 'sp': []},
            'common': []
        }

        df1_full = log1.get_processed_data()[log1.get_processed_data()['Dupe'] == False]
        df2_full = log2.get_processed_data()[log2.get_processed_data()['Dupe'] == False]

        for band in bands:
            df1_band = df1_full[df1_full['Band'] == band]
            df2_band = df2_full[df2_full['Band'] == band]

            calls1 = set(df1_band['Call'].unique())
            calls2 = set(df2_band['Call'].unique())
            common_calls = calls1.intersection(calls2)

            plot_data[call1]['run'].append((df1_band['Run'] == 'Run').sum())
            plot_data[call1]['sp'].append((df1_band['Run'] == 'S&P').sum())
            plot_data[call2]['run'].append((df2_band['Run'] == 'Run').sum())
            plot_data[call2]['sp'].append((df2_band['Run'] == 'S&P').sum())
            plot_data['common'].append(len(common_calls))

        # --- Plotting ---
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(15, 8)) # Landscape orientation

        index = np.arange(len(plot_data['bands']))
        bar_width = 0.25

        # Bar group for Log 1
        ax.bar(index - bar_width, plot_data[call1]['run'], bar_width, color='red', label=f'{call1} Run')
        ax.bar(index - bar_width, plot_data[call1]['sp'], bar_width, bottom=plot_data[call1]['run'], color='green', label=f'{call1} S&P')

        # Bar group for Common QSOs
        ax.bar(index, plot_data['common'], bar_width, color='grey', label='Common Calls')

        # Bar group for Log 2
        ax.bar(index + bar_width, plot_data[call2]['run'], bar_width, color='red', label=f'{call2} Run')
        ax.bar(index + bar_width, plot_data[call2]['sp'], bar_width, bottom=plot_data[call2]['run'], color='green', label=f'{call2} S&P')

        # --- Formatting ---
        contest_name = log1.get_metadata().get('ContestName', '')
        year = log1.get_processed_data()['Date'].iloc[0].split('-')[0]
        
        ax.set_ylabel('QSO Count')
        ax.set_title(f"{year} {contest_name}\nQSO Breakdown by Band ({call1} vs {call2})", fontsize=16, fontweight='bold')
        ax.set_xticks(index)
        ax.set_xticklabels(plot_data['bands'])
        
        # Create a clean legend
        handles, labels = ax.get_legend_handles_labels()
        # Use a dictionary to remove duplicate labels (e.g., two "Run" labels)
        unique_labels = dict(zip(labels, handles))
        ax.legend(unique_labels.values(), unique_labels.keys(), ncol=3)

        fig.tight_layout()

        # --- Save File ---
        os.makedirs(output_path, exist_ok=True)
        filename = f"{self.report_id}_{call1}_vs_{call2}.png"
        filepath = os.path.join(output_path, filename)
        fig.savefig(filepath)
        plt.close(fig)

        return f"QSO breakdown chart saved to: {filepath}"
