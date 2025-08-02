# Contest Log Analyzer/contest_tools/reports/text_continent_summary.py
#
# Purpose: A text report that generates a summary of QSOs per continent,
#          broken down by band for multiple logs.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-02
# Version: 0.26.1-Beta
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

## [0.26.1-Beta] - 2025-08-02
### Fixed
# - Converted report_id, report_name, and report_type from @property methods
#   to simple class attributes to fix a bug in the report generation loop.

## [0.22.0-Beta] - 2025-07-31
### Changed
# - Implemented the boolean support properties, correctly identifying this
#   report as 'single'.
# - The report now correctly generates a separate output file for each log
#   provided, ensuring consistency with other single-log summary reports.

## [0.21.4-Beta] - 2025-07-28
### Added
# - The report now includes a diagnostic list at the end, showing all unique
#   callsigns that resulted in an "Unknown" continent classification.

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
    Generates a summary of QSOs per continent, broken down by band.
    """
    report_id: str = "continent_summary"
    report_name: str = "Continent QSO Summary"
    report_type: str = "text"
    supports_single = True

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content.
        """
        include_dupes = kwargs.get('include_dupes', False)
        final_report_messages = []

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
                msg = f"Skipping report for {callsign}: No valid QSOs to report."
                print(msg)
                final_report_messages.append(msg)
                continue

            # --- Report Generation ---
            continent_map = {
                'NA': 'North America', 'SA': 'South America', 'EU': 'Europe',
                'AS': 'Asia', 'AF': 'Africa', 'OC': 'Oceania', 'Unknown': 'Unknown'
            }
            bands = ['160M', '80M', '40M', '20M', '15M', '10M']

            # --- Collect Unknown Calls for Diagnostics ---
            unknown_continent_df = df[df['Continent'].isin(['Unknown', None, ''])]
            unique_unknown_calls = sorted(unknown_continent_df['Call'].unique())

            # Map the continent codes to full names for the report
            df['ContinentName'] = df['Continent'].map(continent_map).fillna('Unknown')

            pivot = df.pivot_table(
                index='ContinentName',
                columns='Band',
                aggfunc='size',
                fill_value=0
            )

            for band in bands:
                if band not in pivot.columns:
                    pivot[band] = 0
            pivot = pivot[bands]
            pivot['Total'] = pivot.sum(axis=1)

            # --- Formatting ---
            header = f"{'Continent':<17}" + "".join([f"{b.replace('M',''):>7}" for b in bands]) + f"{'Total':>7}"
            separator = "-" * len(header)
            
            report_lines = [f"--- {self.report_name} for {callsign} ---".center(len(header))]
            report_lines.append(header)
            report_lines.append(separator)

            for cont_name in continent_map.values():
                if cont_name in pivot.index:
                    row = pivot.loc[cont_name]
                    line = f"{cont_name:<17}"
                    for band in bands:
                        line += f"{row.get(band, 0):>7}"
                    line += f"{row.get('Total', 0):>7}"
                    report_lines.append(line)

            report_lines.append(separator)
            
            total_line = f"{'Total':<17}"
            for band in bands:
                total_line += f"{pivot[band].sum():>7}"
            total_line += f"{pivot['Total'].sum():>7}"
            report_lines.append(total_line)
            
            # --- Add Diagnostic List for Unknown Calls ---
            if unique_unknown_calls:
                report_lines.append("\n" + "-" * 30)
                report_lines.append("Callsigns with 'Unknown' Continent:")
                report_lines.append("-" * 30)
                
                col_width = 12
                num_cols = max(1, len(header) // (col_width + 2))
                
                for i in range(0, len(unique_unknown_calls), num_cols):
                    line_calls = unique_unknown_calls[i:i+num_cols]
                    report_lines.append("  ".join([f"{call:<{col_width}}" for call in line_calls]))


            # --- Save the Report File ---
            report_content = "\n".join(report_lines)
            os.makedirs(output_path, exist_ok=True)
            
            filename = f"{self.report_id}_{callsign}.txt"
            filepath = os.path.join(output_path, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            final_report_messages.append(f"Text report saved to: {filepath}")

        return "\n".join(final_report_messages)