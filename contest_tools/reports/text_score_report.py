# Contest Log Analyzer/contest_tools/reports/text_summary.py
#
# Purpose: An example text report that generates a simple QSO summary.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-03
# Version: 0.28.17-Beta
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
## [0.28.17-Beta] - 2025-08-03
### Added
# - Added new diagnostic sections to the end of the report for callsigns
#   with Unknown DXCC and WPX prefixes.
#
## [0.26.1-Beta] - 2025-08-02
### Fixed
# - Converted report_id, report_name, and report_type from @property methods
#   to simple class attributes to fix a bug in the report generation loop.
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
from typing import List
import os
from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a text summary of key statistics for each log.
    """
    report_id: str = "summary"
    report_name: str = "QSO Summary"
    report_type: str = "text"
    supports_multi = True
    
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

        # --- Diagnostic Sections ---
        self._add_diagnostic_sections(report_lines)

        report_content = "\n".join(report_lines)
        os.makedirs(output_path, exist_ok=True)
        
        filename_calls = '_vs_'.join(sorted(all_calls))
        filename = f"{self.report_id}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"

    def _add_diagnostic_sections(self, report_lines: List[str]):
        """Appends sections for Unknown DXCC and WPX prefixes to the report."""
        unknown_dxcc_calls = set()
        unknown_wpx_calls = set()

        # Consolidate data from all logs for this specific report instance
        for log in self.logs:
            df = log.get_processed_data()
            unknown_dxcc_df = df[df['DXCCPfx'] == 'Unknown']
            unknown_dxcc_calls.update(unknown_dxcc_df['Call'].unique())

            if 'Mult1' in df.columns:
                unknown_wpx_df = df[df['Mult1'] == 'Unknown']
                unknown_wpx_calls.update(unknown_wpx_df['Call'].unique())

        if unknown_dxcc_calls:
            report_lines.append("\n" + "-" * 40)
            report_lines.append("Callsigns with Unknown DXCC Prefix:")
            report_lines.append("-" * 40)
            col_width = 12
            sorted_calls = sorted(list(unknown_dxcc_calls))
            # Format into neat columns
            for i in range(0, len(sorted_calls), 5):
                line_calls = sorted_calls[i:i+5]
                report_lines.append("  ".join([f"{call:<{col_width}}" for call in line_calls]))

        if unknown_wpx_calls:
            report_lines.append("\n" + "-" * 40)
            report_lines.append("Callsigns with Unknown WPX Prefix (Mult1):")
            report_lines.append("-" * 40)
            col_width = 12
            sorted_calls = sorted(list(unknown_wpx_calls))
            for i in range(0, len(sorted_calls), 5):
                line_calls = sorted_calls[i:i+5]
                report_lines.append("  ".join([f"{call:<{col_width}}" for call in line_calls]))