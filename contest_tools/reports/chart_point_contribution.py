# Contest Log Analyzer/contest_tools/reports/chart_point_contribution.py
#
# Purpose: A chart report that generates a breakdown of total points by QSO
#          point value, presented as a series of pie charts.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-09-12
# Version: 0.80.4-Beta
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
## [0.80.4-Beta] - 2025-09-12
### Fixed
# - Corrected the band sorting logic to use a robust, two-step pattern
#   to prevent a ValueError during report generation.
## [0.55.9-Beta] - 2025-08-31
### Changed
# - Updated band sorting logic to use the new, comprehensive `_HAM_BANDS`
#   list from the ContestLog class.
## [0.38.0-Beta] - 2025-08-18
### Added
# - Added call to the save_debug_data helper function to dump the source
#   dataframe when the --debug-data flag is enabled.
## [0.31.17-Beta] - 2025-08-08
### Changed
# - Implemented area scaling for comparative charts, with a 15% minimum
#   size and a "Not to scale" annotation for readability.
## [0.31.16-Beta] - 2025-08-08
### Fixed
# - Implemented `constrained_layout=True` to automatically and robustly
#   handle title and subplot spacing, fixing the systemic layout bug.
## [0.31.15-Beta] - 2025-08-08
### Fixed
# - Implemented `constrained_layout=True` to automatically and robustly
#   handle title and subplot spacing, resolving all overlap issues.
## [0.31.14-Beta] - 2025-08-08
### Fixed
# - Removed conflicting hspace and wspace arguments from GridSpec to allow
#   subplots_adjust to correctly manage title spacing.
## [0.31.13-Beta] - 2025-08-08
### Fixed
# - Removed `bbox_inches='tight'` from savefig command to allow
#   `subplots_adjust` to correctly manage title spacing.
## [0.31.12-Beta] - 2025-08-08
### Fixed
# - Corrected layout logic for a horizontal arrangement that also fixes
#   the title overlap issue.
## [0.31.11-Beta] - 2025-08-08
### Fixed
# - Corrected layout logic to arrange comparative charts vertically,
#   resolving title overlap issues.
## [0.31.9-Beta] - 2025-08-08
### Fixed
# - Adjusted subplot layout to prevent the main title from overlapping
#   with the individual chart components.
## [0.31.8-Beta] - 2025-08-07
### Changed
# - Reinstated and corrected the adaptive grid logic to produce a properly
#   spaced, horizontal (landscape) layout for comparative charts.
## [0.31.7-Beta] - 2025-08-07
### Changed
# - Modified layout logic to produce a horizontal (landscape) arrangement
#   for comparative charts.
## [0.31.6-Beta] - 2025-08-07
### Fixed
# - Corrected the grid layout logic to ensure a balanced, vertical
#   layout for comparative charts with 2 or 3 logs.
## [0.31.5-Beta] - 2025-08-07
### Fixed
# - Corrected the dynamic layout logic to ensure proper spacing and
#   proportions for comparative charts.
## [0.31.4-Beta] - 2025-08-07
### Changed
# - Updated script to use the new DonutChartComponent helper class and
#   implemented an adaptive grid layout.
## [0.31.0-Beta] - 2025-08-07
# - Initial release of Version 0.31.0-Beta.
from typing import List
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os
import numpy as np
import re
from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import DonutChartComponent, create_output_directory, get_valid_dataframe, save_debug_data

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
        
        canonical_band_order = [band[1] for band in ContestLog._HAM_BANDS]
        bands_to_plot = valid_bands if is_single_band else ['All Bands'] + sorted(
            valid_bands,
            key=lambda b: canonical_band_order.index(b) if b in canonical_band_order else -1
        )
        
        created_files = []

        for band in bands_to_plot:
            try:
                save_path = output_path
                if not is_single_band and band != 'All Bands':
                    save_path = os.path.join(output_path, band)

                filepath = self._create_plot_for_band(band, save_path, **kwargs)
                if filepath:
                    created_files.append(filepath)
            except Exception as e:
                created_files.append(f"Failed to generate chart for {band}: {e}")
        
        if not created_files:
            return "No Point Contribution charts were generated."
        return "Point Contribution charts saved to:\n" + "\n".join([f"  - {fp}" for fp in created_files])

    def _create_plot_for_band(self, band: str, output_path: str, **kwargs) -> str:
        num_logs = len(self.logs)
        debug_data_flag = kwargs.get("debug_data", False)
        
        # --- Dynamic Layout ---
        nrows = 1
        ncols = num_logs
        figsize = (ncols * 7, nrows * 8) # Landscape format

        fig = plt.figure(figsize=figsize, constrained_layout=True)
        gs = GridSpec(nrows, ncols, figure=fig)

        band_log_points = [
            (get_valid_dataframe(log)['QSOPoints'].sum() if band == 'All Bands' 
             else get_valid_dataframe(log)[get_valid_dataframe(log)['Band'] == band]['QSOPoints'].sum())
            for log in self.logs
        ]
        max_band_points = max(band_log_points) if band_log_points else 1

        all_calls = sorted([log.get_metadata().get('MyCall', f'Log{i+1}') for i, log in enumerate(self.logs)])
        callsign_str = '_vs_'.join(all_calls)
        is_single_band = len(self.logs[0].contest_definition.valid_bands) == 1
        filename_band = self.logs[0].contest_definition.valid_bands[0].lower() if is_single_band else band.lower().replace('m','').replace(' ', '_')

        for i, log in enumerate(self.logs):
            df = get_valid_dataframe(log)
            band_df = df if band == 'All Bands' else df[df['Band'] == band]

            # --- Save Debug Data ---
            debug_filename = f"{self.report_id}_{filename_band}_{all_calls[i]}.txt"
            save_debug_data(debug_data_flag, output_path, band_df, custom_filename=debug_filename)
            
            point_ratio = (band_log_points[i] / max_band_points) if max_band_points > 0 else 0
            
            is_not_to_scale = 0 < point_ratio < 0.15
            radius_ratio = 0.15 if is_not_to_scale else point_ratio
            radius = 1.0 * np.sqrt(radius_ratio)

            component = DonutChartComponent(
                df=band_df, 
                title=log.get_metadata().get('MyCall', f'Log {i+1}'), 
                radius=radius, 
                is_not_to_scale=is_not_to_scale
            )
            component.draw_on(fig, gs[i])

        # --- Title and Filename ---
        metadata = self.logs[0].get_metadata()
        year = get_valid_dataframe(self.logs[0])['Date'].dropna().iloc[0].split('-')[0]
        contest_name = metadata.get('ContestName', '')
        event_id = metadata.get('EventID', '')
        band_title = self.logs[0].contest_definition.valid_bands[0].replace('M', ' Meters') if is_single_band else band.replace('M', ' Meters')
        
        title_line1 = f"{event_id} {year} {contest_name}".strip()
        title_line2 = f"{self.report_name} - {band_title} ({callsign_str})"
        fig.suptitle(f"{title_line1}\n{title_line2}", fontsize=22, fontweight='bold')
        
        create_output_directory(output_path)
        filename = f"{self.report_id}_{filename_band}_{callsign_str}.png"
        filepath = os.path.join(output_path, filename)
        fig.savefig(filepath)
        plt.close(fig)

        return filepath