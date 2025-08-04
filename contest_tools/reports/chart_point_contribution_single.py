# Contest Log Analyzer/contest_tools/reports/chart_point_contribution_single.py
#
# Purpose: A chart report that generates a per-band breakdown of total points
#          by QSO point value, presented as a series of proportionally-sized
#          pie charts for a single log.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-03
# Version: 0.26.2-Beta
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
## [0.26.2-Beta] - 2025-08-03
### Changed
# - The report now uses the dynamic `valid_bands` list from the contest
#   definition instead of deriving the band list from the log content.
## [0.26.1-Beta] - 2025-08-02
### Fixed
# - Converted report_id, report_name, and report_type from @property methods
#   to simple class attributes to fix a bug in the report generation loop.
## [0.22.26-Beta] - 2025-08-01
### Changed
# - Refactored to use the new '_create_pie_chart_subplot' shared helper
#   function, simplifying the code and ensuring consistency.
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
    report_id: str = "chart_point_contribution_single"
    report_name: str = "Single Log Point Contribution"
    report_type: str = "chart"
    supports_single = True

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

        # --- Use dynamic band list from contest definition ---
        bands = sorted(
            log.contest_definition.valid_bands,
            key=lambda b: int(re.search(r'\d+', b).group()),
            reverse=True
        )
        if not bands:
            return f"No chart generated for {callsign}: No valid bands defined for contest."

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