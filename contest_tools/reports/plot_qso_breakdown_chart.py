# Contest Log Analyzer/contest_tools/reports/plot_qso_breakdown_chart.py
#
# Purpose: A plot report that generates a comparative QSO breakdown bar chart.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-02
# Version: 0.26.1-Beta
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

## [0.26.1-Beta] - 2025-08-02
### Fixed
# - Converted report_id, report_name, and report_type from @property methods
#   to simple class attributes to fix a bug in the report generation loop.

## [0.22.0-Beta] - 2025-07-31
### Changed
# - Implemented the boolean support properties, correctly identifying this
#   report as 'pairwise'.

## [0.15.0-Beta] - 2025-07-25
# - Standardized version for final review. No functional changes.

## [0.14.0-Beta] - 2025-07-24
### Changed
# - Updated to handle and display the new "Unknown" classification, adding a
#   third, yellow segment to the stacked bar charts.
# - The 'report_type' is now 'chart' to save output to the 'charts' directory.
# - Removed the "All Bands" summary bar from the plot to improve the scale
#   and readability of the band-by-band comparison.
# - Implemented a two-level x-axis for the bar chart with refined formatting.
### Fixed
# - Corrected data aggregation logic to ensure bars represent "Unique" QSOs only.
# - Corrected various alignment and spacing issues with the x-axis labels.

## [0.12.0-Beta] - 2025-07-23
# - Initial release of the QSO Breakdown Chart report.

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
    Generates a stacked bar chart comparing the QSO breakdown (Run/S&P/Unknown/Common)
    between two logs for each band.
    """
    report_id: str = "qso_breakdown_chart"
    report_name: str = "QSO Breakdown Chart"
    report_type: str = "chart"
    supports_pairwise = True
    
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
            call1: {'run': [], 'sp': [], 'unknown': []},
            call2: {'run': [], 'sp': [], 'unknown': []},
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
            unique_to_1 = calls1.difference(calls2)
            unique_to_2 = calls2.difference(calls1)

            # Filter to only unique QSOs before counting
            df1_unique = df1_band[df1_band['Call'].isin(unique_to_1)]
            df2_unique = df2_band[df2_band['Call'].isin(unique_to_2)]

            plot_data[call1]['run'].append((df1_unique['Run'] == 'Run').sum())
            plot_data[call1]['sp'].append((df1_unique['Run'] == 'S&P').sum())
            plot_data[call1]['unknown'].append((df1_unique['Run'] == 'Unknown').sum())
            
            plot_data[call2]['run'].append((df2_unique['Run'] == 'Run').sum())
            plot_data[call2]['sp'].append((df2_unique['Run'] == 'S&P').sum())
            plot_data[call2]['unknown'].append((df2_unique['Run'] == 'Unknown').sum())
            
            plot_data['common'].append(len(common_calls))

        # --- Plotting ---
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(15, 8)) # Landscape orientation

        group_spacing = 3.0 
        bar_width = 0.8
        index = np.arange(len(plot_data['bands'])) * group_spacing

        # Bar group for Log 1 (Unique QSOs)
        run1_bars = np.array(plot_data[call1]['run'])
        sp1_bars = np.array(plot_data[call1]['sp'])
        ax.bar(index - bar_width, run1_bars, bar_width, color='red', label=f'Unique Run')
        ax.bar(index - bar_width, sp1_bars, bar_width, bottom=run1_bars, color='green', label=f'Unique S&P')
        ax.bar(index - bar_width, plot_data[call1]['unknown'], bar_width, bottom=run1_bars + sp1_bars, color='gold', label=f'Unique Unknown')

        # Bar group for Common QSOs
        ax.bar(index, plot_data['common'], bar_width, color='grey', label='Common Calls')

        # Bar group for Log 2 (Unique QSOs)
        run2_bars = np.array(plot_data[call2]['run'])
        sp2_bars = np.array(plot_data[call2]['sp'])
        ax.bar(index + bar_width, run2_bars, bar_width, color='red')
        ax.bar(index + bar_width, sp2_bars, bar_width, bottom=run2_bars, color='green')
        ax.bar(index + bar_width, plot_data[call2]['unknown'], bar_width, bottom=run2_bars + sp2_bars, color='gold')

        # --- Formatting ---
        contest_name = log1.get_metadata().get('ContestName', '')
        year = log1.get_processed_data()['Date'].iloc[0].split('-')[0]
        
        ax.set_ylabel('QSO Count')
        ax.set_title(f"{year} {contest_name}\nQSO Breakdown ({call1} vs {call2})", fontsize=16, fontweight='bold')
        
        # --- Two-Level X-Axis Labels ---
        ax.set_xticks(index)
        ax.set_xticklabels([''] * len(plot_data['bands']))
        ax.tick_params(axis='x', length=0)

        default_fontsize = plt.rcParams['xtick.labelsize']
        callsign_fontsize = default_fontsize - 2

        # Add the two label lines manually
        for i, group_center in enumerate(index):
            # Top line: Callsigns (closer to the axis)
            y_pos_top = -0.025
            ax.text(group_center - bar_width, y_pos_top, f"{call1}  ", ha='center', va='top', transform=ax.get_xaxis_transform(), fontweight='bold', fontsize=callsign_fontsize)
            ax.text(group_center, y_pos_top, "Common", ha='center', va='top', transform=ax.get_xaxis_transform(), fontweight='bold', fontsize=callsign_fontsize)
            ax.text(group_center + bar_width, y_pos_top, f"  {call2}", ha='center', va='top', transform=ax.get_xaxis_transform(), fontweight='bold', fontsize=callsign_fontsize)
            
            # Bottom line: Bands (further from the axis)
            y_pos_bottom = -0.065
            band_text = f"{plot_data['bands'][i]} Meters"
            ax.text(group_center, y_pos_bottom, band_text, ha='center', va='top', transform=ax.get_xaxis_transform(), fontsize=default_fontsize)
        
        # Create a clean legend
        handles, labels = ax.get_legend_handles_labels()
        unique_labels = dict(zip(labels, handles))
        ax.legend(unique_labels.values(), unique_labels.keys(), ncol=4)

        # Adjust subplot parameters to reduce bottom margin
        plt.subplots_adjust(bottom=0.12)

        # --- Save File ---
        os.makedirs(output_path, exist_ok=True)
        filename = f"{self.report_id}_{call1}_vs_{call2}.png"
        filepath = os.path.join(output_path, filename)
        fig.savefig(filepath)
        plt.close(fig)

        return f"QSO breakdown chart saved to: {filepath}"