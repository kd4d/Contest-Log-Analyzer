# Contest Log Analyzer/contest_tools/reports/plot_point_rate.py
#
# Purpose: A plot report that generates a point rate graph for all bands
#          and for each individual band by calling a shared utility.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-22
# Version: 0.14.0-Beta
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

## [0.14.0-Beta] - 2025-07-22
### Changed
# - Updated to save per-band plots into their own subdirectories
#   (e.g., plots/160M/, plots/80M/).

from typing import List
import os

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._plot_utils import generate_rate_plot # Import the shared helper

class Report(ContestReport):
    """
    Generates a series of plots comparing cumulative points: one for all bands
    combined, and one for each individual contest band.
    """
    @property
    def report_id(self) -> str:
        return "point_rate_plots"

    @property
    def report_name(self) -> str:
        return "Point Rate Comparison Plots"

    @property
    def report_type(self) -> str:
        return "plot"

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Orchestrates the generation of all point rate plots.

        Args:
            output_path (str): The base directory for plot outputs (e.g., '.../plots/').
            **kwargs:
                - include_dupes (bool): If True, dupes are included. Defaults to False.
        """
        include_dupes = kwargs.get('include_dupes', False)
        bands_to_plot = ['All', '160M', '80M', '40M', '20M', '15M', '10M']
        created_files = []
        
        for band in bands_to_plot:
            try:
                # Determine the correct save path for this plot
                if band == "All":
                    save_path = output_path
                else:
                    save_path = os.path.join(output_path, band)

                filepath = generate_rate_plot(
                    logs=self.logs,
                    output_path=save_path,
                    band_filter=band,
                    value_column='QSOPoints',  # Sum the QSOPoints column
                    main_title_verb="Point Rate",
                    y_axis_label="Total Points",
                    filename_prefix="point_rate",
                    include_dupes=include_dupes
                )
                created_files.append(filepath)
            except Exception as e:
                print(f"  - Failed to generate point rate plot for {band}: {e}")

        if not created_files:
            return "No point rate plots were generated."

        summary_message = "Point rate plots saved to the 'plots' directory and its subdirectories."
        return summary_message
