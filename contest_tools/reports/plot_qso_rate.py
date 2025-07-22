# Contest Log Analyzer/contest_tools/reports/plot_qso_rate.py
#
# Purpose: A plot report that generates a QSO rate graph for all bands
#          and for each individual band.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-22
# Version: 0.13.0-Beta
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

## [0.13.0-Beta] - 2025-07-22
### Changed
# - Refactored the generate() method to use **kwargs for flexible argument passing.

from typing import List
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a series of plots comparing QSO rates: one for all bands
    combined, and one for each individual contest band.
    """
    @property
    def report_id(self) -> str:
        return "qso_rate_plots"

    @property
    def report_name(self) -> str:
        return "QSO Rate Comparison Plots"

    @property
    def report_type(self) -> str:
        return "plot"

    def _generate_single_plot(self, output_path: str, include_dupes: bool, band_filter: str):
        """
        Helper function to generate a single QSO rate plot for a specific band.
        """
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(12, 7))

        # Get contest info from the first log for the title
        first_log_meta = self.logs[0].get_metadata()
        contest_name = first_log_meta.get('ContestName', '')
        first_qso_date = self.logs[0].get_processed_data()['Date'].iloc[0]
        year = first_qso_date.split('-')[0] if first_qso_date else ""

        for log in self.logs:
            callsign = log.get_metadata().get('MyCall', 'Unknown')
            df_full = log.get_processed_data()
            
            # Filter for the specific band if not 'All'
            if band_filter != "All":
                df_band = df_full[df_full['Band'] == band_filter].copy()
            else:
                df_band = df_full.copy()

            # Filter out dupes unless specified otherwise
            if not include_dupes and 'Dupe' in df_band.columns:
                df = df_band[df_band['Dupe'] == False].copy()
            else:
                df = df_band.copy()
            
            if df.empty:
                continue

            rate = df.set_index('Datetime').resample('1min').size()
            cumulative_qsos = rate.cumsum()
            hourly_data = cumulative_qsos.resample('1h').last().dropna()
            
            ax.plot(hourly_data.index, hourly_data, marker='o', linestyle='-', markersize=5, label=f'{callsign}')

        # --- Dynamic Title and Filename ---
        main_title = f"{year} {contest_name} QSO Rate Comparison"
        
        if band_filter == "All":
            band_text = "All Bands"
        else:
            band_text = f"{band_filter.replace('M', '')} Meters"

        dupe_text = "(Includes Dupes)" if include_dupes else "(Does Not Include Dupes)"
        
        sub_title = f"{band_text} - {dupe_text}"

        fig.suptitle(main_title, fontsize=16, fontweight='bold')
        ax.set_title(sub_title, fontsize=12)
        
        ax.set_xlabel("Contest Time")
        ax.set_ylabel("Total QSOs")
        ax.legend()
        ax.grid(True)
        
        fig.tight_layout()
        
        os.makedirs(output_path, exist_ok=True)
        
        filename_band = band_filter.lower().replace('m', '')
        filename = f"qso_rate_{filename_band}_plot.png"
        filepath = os.path.join(output_path, filename)
        fig.savefig(filepath)
        plt.close(fig)

        print(f"Plot saved to: {filepath}")

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Orchestrates the generation of all rate plots.

        Args:
            output_path (str): The directory where any output files should be saved.
            **kwargs:
                - include_dupes (bool): If True, dupes are included. Defaults to False.
        """
        include_dupes = kwargs.get('include_dupes', False)

        bands_to_plot = ['All', '160M', '80M', '40M', '20M', '15M', '10M']
        
        for band in bands_to_plot:
            self._generate_single_plot(
                output_path=output_path,
                include_dupes=include_dupes,
                band_filter=band
            )
        
        num_bands = len(bands_to_plot) -1 # Subtract 'All'
        summary_message = f"Generated {num_bands + 1} plots (All Bands + {num_bands} individual bands)."
        
        return summary_message
