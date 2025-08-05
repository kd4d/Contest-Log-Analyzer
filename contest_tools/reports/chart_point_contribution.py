# Contest Log Analyzer/contest_tools/reports/chart_point_contribution.py
#
# Purpose: A chart report that generates a breakdown of total points by QSO
#          point value, presented as a series of pie charts.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-05
# Version: 0.30.26-Beta
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
## [0.30.26-Beta] - 2025-08-05
### Fixed
# - Corrected an AttributeError by explicitly drawing the subplot's canvas
#   before attempting to access its renderer.
## [0.30.24-Beta] - 2025-08-05
### Changed
# - Updated to use the refactored `_create_pie_chart_subplot` helper.
## [0.30.22-Beta] - 2025-08-05
### Fixed
# - Corrected filename and title generation for single-band contests.
## [0.30.21-Beta] - 2025-08-05
### Changed
# - Updated title generation and color palette.
## [0.30.18-Beta] - 2025-08-05
### Changed
# - Restored original multi-file (per-band) report generation behavior.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
from typing import List
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import os
import numpy as np
import re
from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import _create_pie_chart_subplot, create_output_directory, get_valid_dataframe

class Report(ContestReport):
    report_id: str = "chart_point_contribution"
    report_name: str = "Point Contribution Breakdown"
    report_type: str = "chart"
    supports_multi = True
    MAX_LOGS_TO_COMPARE = 3

    def generate(self, output_path: str, **kwargs) -> str:
        if len(self.logs) > self.MAX_LOGS_TO_COMPARE:
            return f"Error: This report supports a maximum of {self.MAX_LOGS_TO_COMPARE} logs."
        
        valid_bands = self.logs[0].contest_definition.valid_bands
        is_single_band = len(valid_bands) == 1
        
        bands_to_plot = valid_bands if is_single_band else ['All Bands'] + sorted(
            valid_bands,
            key=lambda b: [band[1] for band in ContestLog._HF_BANDS].index(b)
        )
        
        created_files = []

        for band in bands_to_plot:
            try:
                save_path = output_path
                if not is_single_band and band != 'All Bands':
                    save_path = os.path.join(output_path, band)

                filepath = self._create_plot_for_band(band, save_path)
                if filepath:
                    created_files.append(filepath)
            except Exception as e:
                created_files.append(f"Failed to generate chart for {band}: {e}")
        
        if not created_files:
            return "No Point Contribution charts were generated."
            
        return "Point Contribution charts saved to:\n" + "\n".join([f"  - {fp}" for fp in created_files])

    def _create_plot_for_band(self, band: str, output_path: str) -> str:
        num_logs = len(self.logs)
        fig, axes = plt.subplots(1, num_logs, figsize=(num_logs * 7, 8))
        if num_logs == 1:
            axes = [axes]
        axes = np.array(axes).flatten()

        band_log_points = [
            (get_valid_dataframe(log)['QSOPoints'].sum() if band == 'All Bands' 
             else get_valid_dataframe(log)[get_valid_dataframe(log)['Band'] == band]['QSOPoints'].sum())
            for log in self.logs
        ]
        max_band_points = max(band_log_points) if band_log_points else 1

        for i, log in enumerate(self.logs):
            ax = axes[i]
            df = get_valid_dataframe(log)
            band_df = df if band == 'All Bands' else df[df['Band'] == band]

            point_ratio = (band_log_points[i] / max_band_points) if max_band_points > 0 else 0
            
            is_not_to_scale = 0 < point_ratio < 0.05
            radius = 1.25 * np.sqrt(0.05 if is_not_to_scale else point_ratio)

            subplot_fig = _create_pie_chart_subplot(band_df, log.get_metadata().get('MyCall', f'Log {i+1}'), radius, is_not_to_scale)
            
            # --- FIX: Explicitly draw the canvas before accessing the renderer ---
            subplot_fig.canvas.draw()
            ax.imshow(subplot_fig.canvas.renderer.buffer_rgba())
            ax.axis('off')
            plt.close(subplot_fig)

        # --- Title and Filename ---
        metadata = self.logs[0].get_metadata()
        year = get_valid_dataframe(self.logs[0])['Date'].dropna().iloc[0].split('-')[0]
        contest_name = metadata.get('ContestName', '')
        event_id = metadata.get('EventID', '')
        all_calls = sorted([log.get_metadata().get('MyCall', f'Log{i+1}') for i, log in enumerate(self.logs)])
        callsign_str = '_vs_'.join(all_calls)
        is_single_band = len(self.logs[0].contest_definition.valid_bands) == 1
        band_title = self.logs[0].contest_definition.valid_bands[0].replace('M', ' Meters') if is_single_band else band.replace('M', ' Meters')
        
        title_line1 = f"{event_id} {year} {contest_name}".strip()
        title_line2 = f"{self.report_name} - {band_title} ({callsign_str})"
        fig.suptitle(f"{title_line1}\n{title_line2}", fontsize=22, fontweight='bold')
        
        fig.tight_layout(rect=[0, 0, 1, 0.95])
        
        create_output_directory(output_path)
        filename_band = self.logs[0].contest_definition.valid_bands[0].lower() if is_single_band else band.lower().replace('m','').replace(' ', '_')
        filename = f"{self.report_id}_{filename_band}_{callsign_str}.png"
        filepath = os.path.join(output_path, filename)
        fig.savefig(filepath, bbox_inches='tight')
        plt.close(fig)

        return filepath