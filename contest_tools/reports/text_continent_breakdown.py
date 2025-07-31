# Contest Log Analyzer/contest_tools/reports/text_continent_breakdown.py
#
# Purpose: A text report that generates a per-band summary of QSOs per
#          continent, with a breakdown by Run/S&P/Unknown status.
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
# - Implemented the 'comparison_mode' property, correctly identifying this
#   report as 'single'.
# - The report now correctly generates a separate set of per-band output files
#   for each log provided, ensuring consistency with other summary reports.

## [0.21.5-Beta] - 2025-07-28
### Added
# - Each per-band report now includes a diagnostic list at the end, showing
#   all unique callsigns from that band that resulted in an "Unknown"
#   continent classification.

## [0.16.0-Beta] - 2025-07-26
### Fixed
# - Corrected the logic to handle two-letter continent abbreviations (e.g., 'NA')
#   from the CTY.DAT file, allowing the report to generate correctly.

from typing import List
import pandas as pd
import os
from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a per-band summary of QSOs per continent with a Run/S&P/Unknown breakdown.
    """
    @property
    def report_id(self) -> str:
        return "continent_breakdown"

    @property
    def report_name(self) -> str:
        return "Continent QSO Breakdown"

    @property
    def report_type(self) -> str:
        return "text"

    @property
    def comparison_mode(self) -> str:
        return "single"

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content.
        """
        include_dupes = kwargs.get('include_dupes', False)
        created_files_for_log = []

        for log in self.logs:
            metadata = log.get_metadata()
            df_full = log.get_processed_data()
            callsign = metadata.get('MyCall', 'UnknownCall')

            # --- Data Preparation ---
            if not include_dupes and 'Dupe' in df_full.columns:
                df = df_full[df_full['Dupe'] == False].copy()
            else:
                df = df_full.copy()
            
            if df.empty:
                print(f"Skipping report for {callsign}: No valid QSOs to report.")
                continue

            # --- Report Generation ---
            continent_map = {
                'NA': 'North America', 'SA': 'South America', 'EU': 'Europe',
                'AS': 'Asia', 'AF': 'Africa', 'OC': 'Oceania', 'Unknown': 'Unknown'
            }
            bands = ['160M', '80M', '40M', '20M', '15M', '10M']
            
            df['ContinentName'] = df['Continent'].map(continent_map).fillna('Unknown')

            for band in bands:
                band_df = df[df['Band'] == band]
                if band_df.empty:
                    continue

                report_lines = []
                
                # --- Header ---
                header = f"{'Continent':<14}{callsign:>12}"
                separator = "-" * len(header)
                report_lines.append(f"--- {band.replace('M','')} Meters Continent Breakdown for {callsign} ---")
                report_lines.append(header)
                report_lines.append(separator)

                # --- Pivot and Format ---
                pivot = band_df.pivot_table(
                    index='ContinentName',
                    columns='Run',
                    aggfunc='size',
                    fill_value=0
                )

                for cont_name in continent_map.values():
                    if cont_name in pivot.index:
                        report_lines.append(cont_name)
                        continent_data = pivot.loc[cont_name]
                        
                        for run_status in ['Run', 'S&P', 'Unknown']:
                            line = f"  {run_status:<11}:"
                            line += f"{continent_data.get(run_status, 0):>12}"
                            report_lines.append(line)
                
                # --- Add Diagnostic List for Unknown Calls ---
                unknown_continent_df = band_df[band_df['ContinentName'] == 'Unknown']
                unique_unknown_calls = sorted(unknown_continent_df['Call'].unique())

                if unique_unknown_calls:
                    report_lines.append("\n" + "-" * 30)
                    report_lines.append("Callsigns with 'Unknown' Continent:")
                    report_lines.append("-" * 30)
                    
                    col_width = 12
                    num_cols = max(1, len(header) // (col_width + 2))
                    
                    for i in range(0, len(unique_unknown_calls), num_cols):
                        line_calls = unique_unknown_calls[i:i+num_cols]
                        report_lines.append("  ".join([f"{call:<{col_width}}" for call in line_calls]))

                # --- Save Individual Report File ---
                report_content = "\n".join(report_lines)
                
                band_output_path = os.path.join(output_path, band)
                os.makedirs(band_output_path, exist_ok=True)
                
                filename = f"{self.report_id}_{band.lower()}_{callsign}.txt"
                filepath = os.path.join(band_output_path, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                
                created_files_for_log.append(filepath)

        if not created_files_for_log:
            return "No continent breakdown reports were generated."

        return f"Continent breakdown reports generated."
