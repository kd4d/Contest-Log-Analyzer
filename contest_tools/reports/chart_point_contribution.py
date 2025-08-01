# Contest Log Analyzer/contest_tools/reports/chart_point_contribution.py
#
# Purpose: A chart report that generates a breakdown of total points by QSO
#          point value, presented as a series of pie charts.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-01
# Version: 0.22.16-Beta
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

## [0.22.16-Beta] - 2025-08-01
### Changed
# - Implemented proportional, area-based sizing for the pie charts.
# - Added a "*NOT TO SCALE*" note for charts at the minimum size.

## [0.22.14-Beta] - 2025-08-01
### Fixed
# - Corrected the proportional sizing logic. The area of each log's pie chart
#   is now correctly scaled based on the points scored on the specific band
#   being plotted, not the overall contest total.

## [0.22.13-Beta] - 2025-08-01
### Changed
# - The area of each log's pie chart is now proportional to that log's
#   total points for the entire contest.
# - Percentage labels are now smaller to prevent overlap.
# - The subplot layout now dynamically adjusts for 2, 3, or 4 logs.

## [0.22.3-Beta] - 2025-07-31
### Changed
# - Renamed the report_id to 'chart_point_contribution' to match the new
#   filename and its report type.

## [0.22.2-Beta] - 2025-07-31
### Changed
# - Changed the 'report_type' from 'plot' to 'chart' to ensure the output
#   is saved to the correct subdirectory.

## [0.22.1-Beta] - 2025-07-31
### Changed
# - Reworked the report to generate comparative, multi-chart images. Each
#   output file now contains a side-by-side comparison of all provided logs
#   for a specific band.
# - Implemented the boolean support properties, correctly identifying this
#   report as 'multi'.

## [0.22.0-Beta] - 2025-07-31
# - Initial release of the Point Contribution Breakdown report.

from typing import List
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a chart with pie charts and tables showing the breakdown of
    total points by the point value of each QSO.
    """
    supports_multi = True
    MAX_LOGS_TO_COMPARE = 4

    @property
    def report_id(self) -> str:
        return "chart_point_contribution"

    @property
    def report_name(self) -> str:
        return "Point Contribution Breakdown"

    @property
    def report_type(self) -> str:
        return "chart"

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content.
        """
        if len(self.logs) > self.MAX_LOGS_TO_COMPARE:
            return f"Error: This report supports a maximum of {self.MAX_LOGS_TO_COMPARE} logs."

        all_dfs = [log.get_processed_data()[log.get_processed_data()['Dupe'] == False] for log in self.logs]
        all_bands = set()
        for df in all_dfs:
            all_bands.update(df['Band'].unique())
        
        bands_to_plot = ['All Bands'] + sorted([b for b in all_bands if b != 'Invalid'])
        created_files = []

        for band in bands_to_plot:
            try:
                # Create band-specific subdirectories for the output
                save_path = os.path.join(output_path, band) if band != "All Bands" else output_path
                filepath = self._create_plot_for_band(band, save_path)
                if filepath:
                    created_files.append(filepath)
            except Exception as e:
                created_files.append(f"Failed to generate chart for {band}: {e}")
        
        if not created_files:
            return "No Point Contribution charts were generated."
            
        return "Point Contribution charts saved to:\n" + "\n".join([f"  - {fp}" for fp in created_files])

    def _create_plot_for_band(self, band: str, output_path: str) -> str:
        """
        Creates a single comparative image with a subplot for each log for a given band.
        """
        num_logs = len(self.logs)
        
        # --- Dynamic Plot Layout ---
        if num_logs <= 3:
            nrows, ncols = 1, num_logs
            figsize = (num_logs * 6, 7)
        else:
            nrows, ncols = 2, 2
            figsize = (12, 14)

        fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)
        if num_logs == 1:
            axes = [axes]
        else:
            axes = axes.flatten()

        # --- Pre-calculate band-specific points for proportional sizing ---
        band_log_points = []
        for log in self.logs:
            df = log.get_processed_data()[log.get_processed_data()['Dupe'] == False]
            if band == 'All Bands':
                band_log_points.append(df['QSOPoints'].sum())
            else:
                band_log_points.append(df[df['Band'] == band]['QSOPoints'].sum())
        max_band_points = max(band_log_points) if band_log_points else 1

        # --- Generate a subplot for each log ---
        for i, log in enumerate(self.logs):
            ax = axes[i]
            metadata = log.get_metadata()
            callsign = metadata.get('MyCall', f'Log {i+1}')
            df = log.get_processed_data()[log.get_processed_data()['Dupe'] == False].copy()

            if band == 'All Bands':
                band_df = df
            else:
                band_df = df[df['Band'] == band]

            if band_df.empty or 'QSOPoints' not in band_df.columns or band_df['QSOPoints'].sum() == 0:
                ax.text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=12)
                ax.set_title(f"{callsign}", fontweight='bold', fontsize=16)
                ax.axis('off')
                continue

            # --- Data Aggregation for the subplot ---
            point_summary = band_df.groupby('QSOPoints').agg(
                QSOs=('Call', 'count')
            ).reset_index()
            point_summary['Points'] = point_summary['QSOPoints'] * point_summary['QSOs']
            point_summary['AVG'] = point_summary['QSOPoints']

            # --- Proportional Pie Chart Sizing ---
            current_log_band_points = band_log_points[i]
            point_ratio = (current_log_band_points / max_band_points) if max_band_points > 0 else 0
            
            is_not_to_scale = False
            if 0 < point_ratio < 0.05:
                point_ratio = 0.05
                is_not_to_scale = True

            max_radius = 1.25
            radius = max_radius * np.sqrt(point_ratio)

            pie_data = point_summary.set_index('QSOPoints')['Points']
            labels = [f"{idx} Pts" for idx in pie_data.index]
            
            wedges, texts, autotexts = ax.pie(pie_data, labels=labels, autopct='%1.1f%%',
                                              startangle=90, counterclock=False, radius=radius,
                                              center=(0, 0.1))
            for autotext in autotexts:
                autotext.set_fontsize(8)

            ax.set_title(f"{callsign}", fontweight='bold', fontsize=16)

            # --- Add "Not to Scale" note if needed ---
            if is_not_to_scale:
                ax.text(0.5, -0.1, "*NOT TO SCALE*", ha='center', va='top',
                        transform=ax.transAxes, fontsize=12, fontweight='bold')

            # --- Summary Table ---
            total_row = pd.DataFrame({
                'QSOPoints': ['Total'],
                'QSOs': [point_summary['QSOs'].sum()],
                'Points': [point_summary['Points'].sum()],
                'AVG': [point_summary['Points'].sum() / point_summary['QSOs'].sum() if point_summary['QSOs'].sum() > 0 else 0]
            })
            
            table_data = pd.concat([point_summary, total_row], ignore_index=True)
            table_data['AVG'] = table_data['AVG'].map('{:.2f}'.format)
            
            cell_text = table_data[['QSOPoints', 'QSOs', 'Points', 'AVG']].values
            col_labels = ['Pts/QSO', 'QSOs', 'Points', 'Avg']
            
            table = ax.table(cellText=cell_text, colLabels=col_labels, cellLoc='center', loc='bottom', bbox=[0.1, -0.5, 0.8, 0.4])
            table.auto_set_font_size(False)
            table.set_fontsize(10)

        # --- Clean up unused subplots ---
        for i in range(num_logs, len(axes)):
            fig.delaxes(axes[i])

        # --- Final Formatting and Save ---
        band_title = band.replace('M', ' Meters') if band != "All Bands" else "All Bands"
        fig.suptitle(f"Point Contribution Breakdown - {band_title}", fontsize=22, fontweight='bold')
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])

        os.makedirs(output_path, exist_ok=True)
        filename_band = band.lower().replace('m','')
        all_calls = '_vs_'.join(sorted([log.get_metadata().get('MyCall', f'Log{i+1}') for i, log in enumerate(self.logs)]))
        filename = f"{self.report_id}_{filename_band}_{all_calls}.png"
        filepath = os.path.join(output_path, filename)
        fig.savefig(filepath, bbox_inches='tight')
        plt.close(fig)

        return filepath
