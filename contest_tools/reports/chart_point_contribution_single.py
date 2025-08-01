# Contest Log Analyzer/contest_tools/reports/chart_point_contribution_single.py
#
# Purpose: A chart report that generates a per-band breakdown of total points
#          by QSO point value, presented as a series of proportionally-sized
#          pie charts for a single log.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-01
# Version: 0.22.26-Beta
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

## [0.22.26-Beta] - 2025-08-01
### Changed
# - Refactored to use the new '_create_pie_chart_subplot' shared helper
#   function, simplifying the code and ensuring consistency.

## [0.22.25-Beta] - 2025-08-01
### Fixed
# - Corrected the positioning logic for the "*NOT TO SCALE*" note to prevent
#   it from overlapping with the summary table.

## [0.22.24-Beta] - 2025-08-01
### Fixed
# - Corrected the vertical position of the "*NOT TO SCALE*" note, moving it
#   up to sit correctly between the chart and the table.

## [0.22.23-Beta] - 2025-08-01
### Changed
# - Corrected the vertical position of the "*NOT TO SCALE*" note, moving it
#   up to sit correctly between the chart and the table.

## [0.22.22-Beta] - 2025-08-01
### Changed
# - Corrected the vertical position of the "*NOT TO SCALE*" note, moving it
#   up to sit correctly between the chart and the table.

## [0.22.21-Beta] - 2025-08-01
### Changed
# - Corrected the vertical position of the "*NOT TO SCALE*" note, moving it
#   up to sit correctly between the chart and the table.

## [0.22.20-Beta] - 2025-08-01
### Changed
# - Further adjusted the vertical position of the "*NOT TO SCALE*" note to
#   center it correctly between the chart and the table.

## [0.22.19-Beta] - 2025-08-01
### Changed
# - Further adjusted the vertical position of the "*NOT TO SCALE*" note to
#   place it closer to the pie chart it refers to.

## [0.22.18-Beta] - 2025-08-01
### Changed
# - Increased the font size and corrected the vertical position of the
#   "*NOT TO SCALE*" note for better visibility and layout.

## [0.22.17-Beta] - 2025-08-01
### Changed
# - Increased the font size and adjusted the vertical position of the
#   "*NOT TO SCALE*" note for better visibility and layout.

## [0.22.16-Beta] - 2025-08-01
### Added
# - A "*NOT TO SCALE" note is now added below any pie chart that is rendered
#   at the minimum size, clarifying its proportionality.

## [0.22.12-Beta] - 2025-08-01
### Changed
# - Reverted the label placement logic. Percentage labels are now always
#   drawn inside the pie chart.
# - Reduced the font size of the percentage labels to prevent overlap on
#   smaller charts.

## [0.22.11-Beta] - 2025-08-01
### Changed
# - Refined the threshold for moving percentage labels outside the pie chart
#   to affect only the smallest charts.
# - Increased the distance for external labels and their connecting lines.

## [0.22.10-Beta] - 2025-08-01
### Changed
# - For smaller pie charts, the percentage labels are now drawn outside the
#   slices with connecting lines to prevent text overlap and improve readability.

## [0.22.9-Beta] - 2025-07-31
### Changed
# - Slightly reduced the maximum radius of the pie charts to prevent any
#   overlap with the subplot titles.

## [0.22.8-Beta] - 2025-07-31
### Changed
# - Further adjusted the vertical positioning of the pie charts and tables
#   to achieve better centering within the subplot area.

## [0.22.7-Beta] - 2025-07-31
### Changed
# - Adjusted the vertical positioning of the pie charts and summary tables
#   to create a more balanced and centered layout.

## [0.22.6-Beta] - 2025-07-31
### Changed
# - Removed markdown bold characters from titles and increased title font
#   sizes for better readability.

## [0.22.5-Beta] - 2025-07-31
### Changed
# - Adjusted the vertical positioning of the pie charts and summary tables
#   to create a more balanced and centered layout.

## [0.22.4-Beta] - 2025-07-31
### Changed
# - The proportional sizing logic now enforces a minimum chart area of 5%
#   of the largest chart for any band with points.

## [0.22.3-Beta] - 2025-07-31
### Changed
# - Reduced the maximum radius for the pie charts to prevent the largest
#   chart from overlapping with the subplot title.

## [0.22.2-Beta] - 2025-07-31
### Changed
# - Reworked the pie chart sizing logic. The AREA of each chart is now
#   proportional to the total points for that band, providing a more
#   accurate visual representation.
# - Increased the overall size of the pie charts to better fill the subplot area.

## [0.22.1-Beta] - 2025-07-31
### Changed
# - The radius of each band's pie chart is now proportional to the total
#   points earned on that band, not the total number of QSOs.

## [0.22.0-Beta] - 2025-07-31
# - Initial release of the Single Log Point Contribution chart report.

from typing import List
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import re
from matplotlib.gridspec import GridSpec
from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import _create_pie_chart_subplot

class Report(ContestReport):
    """
    Generates a chart with a grid of pie charts and tables, one for each band,
    showing the breakdown of total points by the point value of each QSO.
    The size of each pie chart is proportional to its point total.
    """
    supports_single = True

    @property
    def report_id(self) -> str:
        return "chart_point_contribution_single"

    @property
    def report_name(self) -> str:
        return "Single Log Point Contribution"

    @property
    def report_type(self) -> str:
        return "chart"

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content.
        """
        final_report_messages = []

        for log in self.logs:
            try:
                filepath = self._create_plot_for_log(log, output_path)
                if filepath:
                    final_report_messages.append(f"Chart saved to: {filepath}")
            except Exception as e:
                final_report_messages.append(f"Failed to generate chart for {log.get_metadata().get('MyCall', 'Unknown')}: {e}")
        
        return "\n".join(final_report_messages)

    def _create_plot_for_log(self, log: ContestLog, output_path: str) -> str:
        """
        Creates a single multi-plot image for a given log.
        """
        metadata = log.get_metadata()
        callsign = metadata.get('MyCall', 'UnknownCall')
        df_full = log.get_processed_data()
        df = df_full[df_full['Dupe'] == False].copy()

        if df.empty or 'QSOPoints' not in df.columns:
            return None

        # --- Data-driven Band Determination ---
        bands = sorted(
            [b for b in df['Band'].unique() if b != 'Invalid'],
            key=lambda b: int(re.search(r'\d+', b).group()),
            reverse=True
        )
        if not bands:
            return f"No chart generated for {callsign}: No QSOs on valid bands."

        # --- Dynamic Plot Layout ---
        num_bands = len(bands)
        if num_bands <= 3:
            nrows, ncols = 1, num_bands
            figsize = (num_bands * 7, 8)
        elif num_bands == 4:
            nrows, ncols = 2, 2
            figsize = (14, 16)
        else: # 5 or 6 bands
            nrows, ncols = 2, 3
            figsize = (20, 14)

        fig = plt.figure(figsize=figsize)
        outer_gs = GridSpec(nrows, ncols, figure=fig, hspace=0.4, wspace=0.3)
        
        band_points = {band: df[df['Band'] == band]['QSOPoints'].sum() for band in bands}
        max_band_points = max(band_points.values()) if band_points else 1

        # --- Generate a subplot for each band ---
        for i, band in enumerate(bands):
            gs = outer_gs[i]
            band_df = df[df['Band'] == band]
            
            current_band_points = band_points.get(band, 0)
            point_ratio = (current_band_points / max_band_points) if max_band_points > 0 else 0
            
            is_not_to_scale = False
            if 0 < point_ratio < 0.05:
                point_ratio = 0.05
                is_not_to_scale = True

            max_radius = 1.25
            radius = max_radius * np.sqrt(point_ratio)
            
            title = f"{band.replace('M','')} Meters"
            _create_pie_chart_subplot(fig, gs, band_df, title, radius, is_not_to_scale)

        # --- Final Formatting and Save ---
        fig.suptitle(f"{callsign} - Point Contribution Breakdown by Band", fontsize=22, fontweight='bold')
        
        os.makedirs(output_path, exist_ok=True)
        filename = f"{self.report_id}_{callsign}.png"
        filepath = os.path.join(output_path, filename)
        fig.savefig(filepath, bbox_inches='tight')
        plt.close(fig)

        return filepath
