# Contest Log Analyzer/contest_tools/reports/chart_point_contribution_single.py
#
# Purpose: Generates a single-log report with per-band pie charts and tables
#          showing the breakdown of QSO points.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-05
# Version: 0.30.30-Beta
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
## [0.30.30-Beta] - 2025-08-05
### Fixed
# - Removed incompatible plt.tight_layout() call to prevent UserWarning.
## [0.30.27-Beta] - 2025-08-05
### Changed
# - Refactored to use the new ChartComponent factory.
# - Added 'All Bands' summary chart for multi-band contests.
## [0.30.26-Beta] - 2025-08-05
### Fixed
# - Corrected an AttributeError by explicitly drawing the subplot's canvas
#   before attempting to access its renderer.
## [0.30.25-Beta] - 2025-08-05
### Fixed
# - Corrected an AttributeError by explicitly drawing the subplot's canvas
#   before attempting to access its renderer.
## [0.30.24-Beta] - 2025-08-05
### Fixed
# - Updated to use the refactored `_create_pie_chart_subplot` helper.
## [0.30.23-Beta] - 2025-08-05
### Fixed
# - Updated title generation to use the standard two-line format.
## [0.30.21-Beta] - 2025-08-05
### Changed
# - Updated title generation and color palette.
## [0.30.13-Beta] - 2025-08-05
### Fixed
# - No changes in this version.
## [0.30.4-Beta] - 2025-08-05
### Fixed
# - Corrected an AttributeError.
## [0.30.3-Beta] - 2025-08-05
### Fixed
# - Corrected the key for sorting bands to prevent a ValueError.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
from .report_interface import ContestReport
from ._report_utils import get_valid_dataframe, create_output_directory, ChartComponent
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import pandas as pd
import numpy as np
import os
import logging
from ..contest_log import ContestLog

class Report(ContestReport):
    report_id = "chart_point_contribution_single"
    report_name = "Point Contribution Breakdown (Single Log)"
    report_type = "chart"
    supports_single = True

    def generate(self, output_path: str, **kwargs) -> str:
        create_output_directory(output_path)
        log = self.logs[0]
        callsign = log.get_metadata().get('MyCall', 'Log')
        df = get_valid_dataframe(log, kwargs.get('include_dupes', False))

        if df.empty or 'QSOPoints' not in df.columns or df['QSOPoints'].sum() == 0:
            return f"Skipping '{self.report_name}': No QSO points found for {callsign}."

        # --- Band Selection Logic ---
        valid_bands_from_def = log.contest_definition.valid_bands
        is_single_band = len(valid_bands_from_def) == 1
        
        bands_in_log = sorted(df['Band'].unique(), key=lambda b: [band[1] for band in ContestLog._HF_BANDS].index(b))

        if is_single_band:
            bands_to_plot = bands_in_log
        else:
            bands_to_plot = ['All Bands'] + bands_in_log

        num_charts = len(bands_to_plot)
        
        # --- Layout Logic ---
        nrows, ncols = (1, num_charts) if num_charts <= 4 else (2, (num_charts + 1) // 2)
        figsize = (ncols * 6, nrows * 7)
        fig = plt.figure(figsize=figsize)
        gs = GridSpec(nrows, ncols, figure=fig, wspace=0.3, hspace=0.3)

        # --- Title Generation ---
        metadata = log.get_metadata()
        year = df['Date'].dropna().iloc[0].split('-')[0]
        contest_name = metadata.get('ContestName', '')
        event_id = metadata.get('EventID', '')

        title_line1 = f"{event_id} {year} {contest_name}".strip()
        title_line2 = f"Point Contribution by Band for {callsign}"
        fig.suptitle(f"{title_line1}\n{title_line2}", fontsize=16, fontweight='bold', y=0.98)

        # --- Plotting Loop ---
        for i, band in enumerate(bands_to_plot):
            band_df = df if band == 'All Bands' else df[df['Band'] == band]
            chart_title = band if band == 'All Bands' else f"{band.replace('M','')} Meters"
            
            component = ChartComponent(df=band_df, title=chart_title, radius=1.0)
            component.draw_on(fig, gs[i])
        
        output_filename = os.path.join(output_path, f"{self.report_id}_{callsign}.png")
        try:
            plt.savefig(output_filename, bbox_inches='tight', dpi=150)
            plt.close(fig)
            return f"'{self.report_name}' for {callsign} saved to {output_filename}"
        except Exception as e:
            logging.error(f"Error saving chart for {callsign}: {e}")
            plt.close(fig)
            return f"Error generating report '{self.report_name}' for {callsign}"