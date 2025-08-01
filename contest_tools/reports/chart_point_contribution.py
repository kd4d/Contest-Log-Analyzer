# Contest Log Analyzer/contest_tools/reports/chart_point_contribution.py
#
# Purpose: A chart report that generates a breakdown of total points by QSO
#          point value, presented as a series of pie charts.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-01
# Version: 0.22.15-Beta
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

## [0.22.15-Beta] - 2025-08-01
### Changed
# - Refactored to use the new '_create_pie_chart_subplot' shared helper
#   function, simplifying the code and ensuring consistency.

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
from ._report_utils import _create_pie_chart_subplot

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
            figsize = (num_logs * 7, 8) # Increased width per subplot
        else:
            nrows, ncols = 2, 2
            figsize = (14, 16)

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

            band_df = df if band == 'All Bands' else df[df['Band'] == band]

            current_log_band_points = band_log_points[i]
            point_ratio = (current_log_band_points / max_band_points) if max_band_points > 0 else 0
            
            is_not_to_scale = False
            if 0 < point_ratio < 0.05:
                point_ratio = 0.05
                is_not_to_scale = True

            max_radius = 1.25
            radius = max_radius * np.sqrt(point_ratio)

            _create_pie_chart_subplot(ax, band_df, callsign, radius, is_not_to_scale)

        # --- Clean up unused subplots ---
        for i in range(num_logs, len(axes)):
            fig.delaxes(axes[i])

        # --- Final Formatting and Save ---
        band_title = band.replace('M', ' Meters') if band != "All Bands" else "All Bands"
        fig.suptitle(f"Point Contribution Breakdown - {band_title}", fontsize=22, fontweight='bold')
        fig.tight_layout(rect=[0, 0.03, 1, 0.95], pad=3.0) # Add padding

        os.makedirs(output_path, exist_ok=True)
        filename_band = band.lower().replace('m','')
        all_calls = '_vs_'.join(sorted([log.get_metadata().get('MyCall', f'Log{i+1}') for i, log in enumerate(self.logs)]))
        filename = f"{self.report_id}_{filename_band}_{all_calls}.png"
        filepath = os.path.join(output_path, filename)
        fig.savefig(filepath, bbox_inches='tight')
        plt.close(fig)

        return filepath
