# Contest Log Analyzer/contest_tools/reports/plot_point_rate.py
#
# Purpose: A plot report that generates a point rate graph for all bands
#          and for each individual band by calling a shared utility.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-04
# Version: 0.28.3-Beta
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
## [0.28.3-Beta] - 2025-08-04
### Changed
# - Simplified the report to work with pre-aligned dataframes, removing
#   all internal time-alignment logic to fix the "all zeros" bug.
## [0.28.2-Beta] - 2025-08-03
### Changed
# - The report now uses the dynamic `valid_bands` list from the contest
#   definition instead of a hardcoded list.
## [0.28.1-Beta] - 2025-08-02
### Changed
# - Refactored to use the new _create_cumulative_rate_plot shared helper
#   function from _report_utils, reducing code duplication.
# - Added the inset summary table to this report for consistency with the
#   QSO Rate plot. The table is now opaque to cover grid lines.
from typing import List
import os
import pandas as pd
from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import _create_cumulative_rate_plot

class Report(ContestReport):
    """
    Generates a series of plots comparing cumulative points: one for all bands
    combined, and one for each individual contest band.
    """
    report_id: str = "point_rate_plots"
    report_name: str = "Point Rate Comparison Plots"
    report_type: str = "plot"
    supports_multi = True
    
    def generate(self, output_path: str, **kwargs) -> str:
        """
        Orchestrates the generation of all point rate plots by calling the
        shared helper function.
        """
        bands_to_plot = ['All'] + self.logs[0].contest_definition.valid_bands
        created_files = []
        
        for band in bands_to_plot:
            try:
                save_path = os.path.join(output_path, band) if band != "All" else output_path
                filepath = _create_cumulative_rate_plot(
                    logs=self.logs,
                    output_path=save_path,
                    band_filter=band,
                    metric_name="Points",
                    value_column='QSOPoints',
                    agg_func='sum',
                    report_id=self.report_id
                )
                if filepath:
                    created_files.append(filepath)
            except Exception as e:
                print(f"  - Failed to generate point rate plot for {band}: {e}")

        if not created_files:
            return "No point rate plots were generated."
        return "Point rate plots saved to:\n" + "\n".join([f"  - {fp}" for fp in created_files])