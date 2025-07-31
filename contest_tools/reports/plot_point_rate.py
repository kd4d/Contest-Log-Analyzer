# Contest Log Analyzer/contest_tools/reports/plot_point_rate.py
#
# Purpose: A plot report that generates a point rate graph for all bands
#          and for each individual band by calling a shared utility.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-31
# Version: 0.22.0-Beta
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

## [0.22.0-Beta] - 2025-07-31
### Changed
# - Implemented the boolean support properties, correctly identifying this
#   report as 'multi'.

## [0.15.0-Beta] - 2025-07-25
### Changed
# - Refactored to use the new 'align_logs_by_time' shared helper function
#   for robust data alignment and consistency.

## [0.14.0-Beta] - 2025-07-22
# - Initial release of the Point Rate plot report.

from typing import List
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import align_logs_by_time # Import the shared helper

class Report(ContestReport):
    """
    Generates a series of plots comparing cumulative points: one for all bands
    combined, and one for each individual contest band.
    """
    supports_multi = True
    
    @property
    def report_id(self) -> str:
        return "point_rate_plots"

    @property
    def report_name(self) -> str:
        return "Point Rate Comparison Plots"

    @property
    def report_type(self) -> str:
        return "plot"

    def _generate_single_plot(self, output_path: str, include_dupes: bool, band_filter: str) -> str:
        """
        Helper function to generate a single point rate plot for a specific band.
        """
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(12, 7))

        # --- Data Preparation using the shared helper ---
        aligned_data = align_logs_by_time(
            logs=self.logs,
            value_column='QSOPoints',
            agg_func='sum',
            band_filter=band_filter, # Pass the band filter here
            time_unit='10min'
        )
        
        if not aligned_data:
              print(f"  - Skipping {band_filter} point rate plot: no logs have QSOs on this band.")
              return None

        # --- Plotting ---
        for callsign, df_aligned in aligned_data.items():
            cumulative_points = df_aligned['Overall'].cumsum()
            ax.plot(cumulative_points.index, cumulative_points, marker='o', linestyle='-', markersize=4, label=callsign)

        # --- Formatting ---
        first_log_meta = self.logs[0].get_metadata()
        contest_name = first_log_meta.get('ContestName', '')
        year = self.logs[0].get_processed_data()['Date'].iloc[0].split('-')[0]
        
        main_title = f"{year} {contest_name} Point Rate Comparison"
        band_text = "All Bands" if band_filter == "All" else f"{band_filter.replace('M', '')} Meters"
        dupe_text = "(Includes Dupes)" if include_dupes else "(Does Not Include Dupes)"
        sub_title = f"{band_text} - {dupe_text}"

        fig.suptitle(main_title, fontsize=16, fontweight='bold')
        ax.set_title(sub_title, fontsize=12)
        
        ax.set_xlabel("Contest Time")
        ax.set_ylabel("Total Points")
        ax.legend()
        ax.grid(True)
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])

        # --- Save File ---
        os.makedirs(output_path, exist_ok=True)
        filename_band = band_filter.lower().replace('m', '')
        filename = f"point_rate_{filename_band}_plot.png"
        filepath = os.path.join(output_path, filename)
        fig.savefig(filepath)
        plt.close(fig)

        return filepath

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Orchestrates the generation of all point rate plots.
        """
        include_dupes = kwargs.get('include_dupes', False)
        bands_to_plot = ['All', '160M', '80M', '40M', '20M', '15M', '10M']
        created_files = []
        
        for band in bands_to_plot:
            try:
                save_path = os.path.join(output_path, band) if band != "All" else output_path
                filepath = self._generate_single_plot(
                    output_path=save_path,
                    include_dupes=include_dupes,
                    band_filter=band
                )
                if filepath:
                    created_files.append(filepath)
            except Exception as e:
                print(f"  - Failed to generate point rate plot for {band}: {e}")

        if not created_files:
            return "No point rate plots were generated."

        return "Point rate plots saved to:\n" + "\n".join([f"  - {fp}" for fp in created_files])
