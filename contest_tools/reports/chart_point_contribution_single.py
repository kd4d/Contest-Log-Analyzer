# Contest Log Analyzer/contest_tools/reports/chart_point_contribution_single.py
#
# Purpose: Generates a single-log report with per-band pie charts and tables
#          showing the breakdown of QSO points.
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
from ._report_utils import get_valid_dataframe, create_output_directory, _create_pie_chart_subplot
import matplotlib.pyplot as plt
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

        if df['QSOPoints'].sum() == 0:
            return f"Skipping '{self.report_name}': No QSO points found for {callsign}."

        bands = sorted(df['Band'].unique(), key=lambda b: [band[1] for band in ContestLog._HF_BANDS].index(b))
        num_bands = len(bands)
        
        nrows, ncols = (1, num_bands) if num_bands <= 3 else (2, (num_bands + 1) // 2)
        figsize = (ncols * 6, nrows * 6)

        fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
        if num_bands == 1:
            axes = np.array([axes])
        axes = axes.flatten()

        # --- Title Generation ---
        metadata = log.get_metadata()
        year = df['Date'].dropna().iloc[0].split('-')[0]
        contest_name = metadata.get('ContestName', '')
        event_id = metadata.get('EventID', '')

        title_line1 = f"{event_id} {year} {contest_name}".strip()
        title_line2 = f"Point Contribution by Band for {callsign}"
        fig.suptitle(f"{title_line1}\n{title_line2}", fontsize=16, fontweight='bold', y=0.98)

        for i, band in enumerate(bands):
            ax = axes[i]
            band_df = df[df['Band'] == band]
            
            subplot_fig = _create_pie_chart_subplot(band_df, band, radius=1.0)
            
            # --- FIX: Explicitly draw the canvas before accessing the renderer ---
            subplot_fig.canvas.draw()
            ax.imshow(subplot_fig.canvas.renderer.buffer_rgba())
            ax.axis('off')
            plt.close(subplot_fig)

        for j in range(num_bands, len(axes)):
            fig.delaxes(axes[j])
            
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        
        output_filename = os.path.join(output_path, f"{self.report_id}_{callsign}.png")
        try:
            plt.savefig(output_filename, bbox_inches='tight', dpi=150)
            plt.close(fig)
            return f"'{self.report_name}' for {callsign} saved to {output_filename}"
        except Exception as e:
            logging.error(f"Error saving chart for {callsign}: {e}")
            plt.close(fig)
            return f"Error generating report '{self.report_name}' for {callsign}"