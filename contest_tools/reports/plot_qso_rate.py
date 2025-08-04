# Contest Log Analyzer/contest_tools/reports/plot_qso_rate.py
#
# Purpose: A plot report that generates a QSO rate graph for all bands
#          and for each individual band by calling a shared utility.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-03
# Version: 0.28.2-Beta
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
## [0.28.2-Beta] - 2025-08-03
### Changed
# - The report now uses the dynamic `valid_bands` list from the contest
#   definition instead of a hardcoded list.
## [0.28.1-Beta] - 2025-08-02
### Changed
# - Refactored to use the new _create_cumulative_rate_plot shared helper
#   function from _report_utils, reducing code duplication.
# - The inset summary table is now opaque to cover grid lines.
## [0.26.1-Beta] - 2025-08-02
### Fixed
# - Converted report_id, report_name, and report_type from @property methods
#   to simple class attributes to fix a bug in the report generation loop.
from typing import List
import os
import pandas as pd
from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import _create_cumulative_rate_plot

class Report(ContestReport):
    """
    Generates a series of plots comparing QSO rates: one for all bands
    combined, and one for each individual contest band.
    """
    report_id: str = "qso_rate_plots"
    report_name: str = "QSO Rate Comparison Plots"
    report_type: str = "plot"
    supports_multi = True
    
    def generate(self, output_path: str, **kwargs) -> str:
        """
        Orchestrates the generation of all QSO rate plots by calling the
        shared helper function.
        """
        log_manager = getattr(self.logs[0], '_log_manager_ref', None)
        if not log_manager or log_manager.master_time_index is None:
            return "Error: Master time index not available for plot report."
        master_index = log_manager.master_time_index

        bands_to_plot = ['All'] + self.logs[0].contest_definition.valid_bands
        created_files = []
        
        for band in bands_to_plot:
            try:
                save_path = os.path.join(output_path, band) if band != "All" else output_path
                filepath = _create_cumulative_rate_plot(
                    logs=self.logs,
                    output_path=save_path,
                    master_index=master_index,
                    band_filter=band,
                    metric_name="QSOs",
                    value_column='Call',
                    agg_func='count',
                    report_id=self.report_id
                )
                if filepath:
                    created_files.append(filepath)
            except Exception as e:
                print(f"  - Failed to generate QSO rate plot for {band}: {e}")

        if not created_files:
            return "No QSO rate plots were generated."
        return "QSO rate plots saved to:\n" + "\n".join([f"  - {fp}" for fp in created_files])