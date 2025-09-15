# Contest Log Analyzer/contest_tools/reports/chart_point_contribution_single.py
#
# Purpose: Generates a single-log report with per-band pie charts and tables
#          showing the breakdown of QSO points.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-09-14
# Version: 0.86.3-Beta
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
## [0.86.3-Beta] - 2025-09-14
### Fixed
# - Removed an erroneous, top-level call to save_debug_data that was
#   incorrectly saving the entire raw QSO list.
## [0.86.2-Beta] - 2025-09-14
### Changed
# - Refactored to use the new centralized `DonutChartComponent.aggregate_data`
#   static method. The debug file now contains aggregated data instead of
#   the raw QSO list.
## [0.80.5-Beta] - 2025-09-12
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
# - Implemented area scaling for per-band charts, with a 15% minimum
#   size and a "Not to scale" annotation for readability.
## [0.31.16-Beta] - 2025-08-08
### Fixed
# - Implemented `constrained_layout=True` to automatically and robustly
#   handle title and subplot spacing, fixing the systemic layout bug.
## [0.31.4-Beta] - 2025-08-07
### Changed
# - Updated script to use the new DonutChartComponent helper class.
## [0.31.0-Beta] - 2025-08-07
# - Initial release of Version 0.31.0-Beta.
from .report_interface import ContestReport
from ._report_utils import get_valid_dataframe, create_output_directory, DonutChartComponent, save_debug_data
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
        debug_data_flag = kwargs.get("debug_data", False)

        if df.empty or 'QSOPoints' not in df.columns or df['QSOPoints'].sum() == 0:
            return f"Skipping '{self.report_name}': No QSO points found for {callsign}."

        canonical_band_order = [band[1] for band in ContestLog._HAM_BANDS]
        bands = sorted(df['Band'].unique(), key=lambda b: canonical_band_order.index(b) if b in canonical_band_order else -1)
        num_bands = len(bands)
        
        # --- Dynamic Layout ---
        ncols = num_bands if num_bands <= 3 else 3
        nrows = (num_bands + ncols - 1) // ncols
        figsize = (ncols * 6, nrows * 7)

        fig = plt.figure(figsize=figsize, constrained_layout=True)
        gs = GridSpec(nrows, ncols, figure=fig)

        # --- Title Generation ---
        metadata = log.get_metadata()
        year = df['Date'].dropna().iloc[0].split('-')[0]
        contest_name = metadata.get('ContestName', '')
        event_id = metadata.get('EventID', '')

        title_line1 = f"{event_id} {year} {contest_name}".strip()
        title_line2 = f"Point Contribution by Band for {callsign}"
        fig.suptitle(f"{title_line1}\n{title_line2}", fontsize=16, fontweight='bold')

        band_points = {band: df[df['Band'] == band]['QSOPoints'].sum() for band in bands}
        max_band_points = max(band_points.values()) if band_points else 1

        for i, band in enumerate(bands):
            band_df = df[df['Band'] == band]
            aggregated_data = DonutChartComponent.aggregate_data(band_df)

            # --- Save Debug Data for this band ---
            safe_band_name = band.lower().replace('m','').replace(' ', '_')
            debug_band_filename = f"{self.report_id}_{callsign}_{safe_band_name}.txt"
            save_debug_data(debug_data_flag, output_path, aggregated_data, custom_filename=debug_band_filename)
            
            point_ratio = (band_points[band] / max_band_points) if max_band_points > 0 else 0
            
            is_not_to_scale = 0 < point_ratio < 0.15
            radius_ratio = 0.15 if is_not_to_scale else point_ratio
            radius = 1.0 * np.sqrt(radius_ratio)

            component = DonutChartComponent(
                aggregated_data=aggregated_data, 
                title=band, 
                radius=radius, 
                is_not_to_scale=is_not_to_scale
            )
            component.draw_on(fig, gs[i])
            
        output_filename = os.path.join(output_path, f"{self.report_id}_{callsign}.png")
        try:
            plt.savefig(output_filename, dpi=150)
            plt.close(fig)
            return f"'{self.report_name}' for {callsign} saved to {output_filename}"
        except Exception as e:
            logging.error(f"Error saving chart for {callsign}: {e}")
            plt.close(fig)
            return f"Error generating report '{self.report_name}' for {callsign}"