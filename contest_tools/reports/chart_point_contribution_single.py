# Contest Log Analyzer/contest_tools/reports/chart_point_contribution_single.py
#
# Purpose: Generates a single-log report with per-band pie charts and tables
#          showing the breakdown of QSO points.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-07
# Version: 0.30.37-Beta
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
## [0.30.37-Beta] - 2025-08-07
### Fixed
# - Corrected a NameError by adding the missing import for 'Optional'
#   from the typing library.
## [0.30.30-Beta] - 2025-08-05
### Fixed
# - Corrected an unterminated f-string literal syntax error.
# - Removed incompatible fig.tight_layout() call to prevent UserWarning.
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
from typing import Optional
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

        fig = plt.figure(figsize=figsize)
        gs = GridSpec(nrows, ncols, figure=fig)

        # --- Title Generation ---
        metadata = log.get_metadata()
        year = df['Date'].dropna().iloc[0].split('-')[0]
        contest_name = metadata.get('ContestName', '')
        event_id = metadata.get('EventID', '')

        title_line1 = f"{event_id} {year} {contest_name}".strip()
        title_line2 = f"Point Contribution by Band for {callsign}"
        fig.suptitle(f"{title_line1}\n{title_line2}", fontsize=16, fontweight='bold', y=0.98)

        for i, band in enumerate(bands):
            band_df = df[df['Band'] == band]
            
            component = ChartComponent(
                df=band_df, 
                title=band, 
                radius=1.0, 
                is_not_to_scale=False
            )
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