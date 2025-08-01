# Contest Log Analyzer/contest_tools/reports/text_summary.py
#
# Purpose: An example text report that generates a simple QSO summary.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-31
# Version: 0.22.2-Beta
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

## [0.22.2-Beta] - 2025-07-31
### Changed
# - Converted the report from a 'single' log summary to a 'multi' log
#   comparative summary table.

## [0.22.1-Beta] - 2025-07-31
### Fixed
# - Corrected the filename generation logic to include the callsign, preventing
#   the report from being overwritten when multiple logs are provided.

## [0.22.0-Beta] - 2025-07-31
### Changed
# - Implemented the boolean support properties, correctly identifying this
#   report as 'single'.

## [0.15.0-Beta] - 2025-07-25
# - Standardized version for final review. No functional changes.

## [0.14.0-Beta] - 2025-07-24
### Changed
# - Updated to correctly handle and display the new "Unknown" classification
#   in the QSO summary.

## [0.12.1-Beta] - 2025-07-22
### Fixed
# - Added missing 'import os' statement to resolve a NameError.
### Changed
# - Refactored the generate() method to use **kwargs for flexible argument passing.
# - The method now saves its own output file and returns a summary message.

## [0.11.0-Beta] - 2025-07-21
### Changed
# - Added logic to exclude duplicate QSOs from calculations by default.
# - Added a note to the report header to explicitly state dupe inclusion status.

## [0.10.0-Beta] - 2025-07-21
# - Initial release of the QSO Summary report.

from typing import List
import os
from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a text summary of key statistics for each log.
    """
    supports_multi = True
    
    @property
    def report_id(self) -> str:
        return "summary"

    @property
    def report_name(self) -> str:
        return "QSO Summary"

    @property
    def report_type(self) -> str:
        return "text"

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content, saves it to a file, and returns a summary.

        Args:
            output_path (str): The directory where any output files should be saved.
            **kwargs:
                - include_dupes (bool): If True, dupes are included. Defaults to False.
        """
        include_dupes = kwargs.get('include_dupes', False)
        
        report_data = []
        all_calls = []

        for log in self.logs:
            callsign = log.get_metadata().get('MyCall', 'Unknown')
            all_calls.append(callsign)
            df_full = log.get_processed_data()
            
            if not include_dupes and 'Dupe' in df_full.columns:
                df = df_full[df_full['Dupe'] == False].copy()
            else:
                df = df_full.copy()
            
            log_summary = {
                'Callsign': callsign,
                'Total QSOs': len(df),
                'Dupes': df_full['Dupe'].sum(),
                'Run': (df['Run'] == 'Run').sum() if 'Run' in df.columns else 0,
                'S&P': (df['Run'] == 'S&P').sum() if 'Run' in df.columns else 0,
                'Unknown': (df['Run'] == 'Unknown').sum() if 'Run' in df.columns else 0,
            }
            report_data.append(log_summary)

        # --- Formatting ---
        headers = ["Callsign", "Total QSOs", "Dupes", "Run", "S&P", "Unknown"]
        col_widths = {h: len(h) for h in headers}

        for row in report_data:
            for key, value in row.items():
                col_widths[key] = max(col_widths.get(key, 0), len(str(value)))

        header_str = "  ".join([f"{h:<{col_widths[h]}}" for h in headers])
        separator = "-" * len(header_str)

        report_lines = [
            f"--- {self.report_name} ---",
            "Note: Does Not Include Dupes" if not include_dupes else "Note: Includes Dupes",
            "",
            header_str,
            separator
        ]

        for row in report_data:
            data_parts = [f"{row[h]:<{col_widths[h]}}" for h in headers]
            report_lines.append("  ".join(data_parts))

        report_content = "\n".join(report_lines)
        os.makedirs(output_path, exist_ok=True)
        
        filename_calls = '_vs_'.join(sorted(all_calls))
        filename = f"{self.report_id}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"
