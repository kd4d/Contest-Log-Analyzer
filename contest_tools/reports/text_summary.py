# Contest Log Analyzer/contest_tools/reports/text_summary.py
#
# Purpose: An example text report that generates a simple QSO summary.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-04
# Version: 0.26.4-Beta
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
## [0.26.4-Beta] - 2025-08-04
### Changed
# - Standardized the report header to use a two-line title.
# - The 'On-Time' column is now correctly hidden if the contest has no
#   defined operating time limits.
## [0.26.3-Beta] - 2025-08-04
### Changed
# - Standardized the report header to use a two-line title.
## [0.26.2-Beta] - 2025-08-03
### Added
# - The report now includes a new 'On-Time' column to display the calculated
#   operating time for each log.
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
                'On-Time': log.get_metadata().get('OperatingTime'),
                'Total QSOs': len(df),
                'Dupes': df_full['Dupe'].sum(),
                'Run': (df['Run'] == 'Run').sum() if 'Run' in df.columns else 0,
                'S&P': (df['Run'] == 'S&P').sum() if 'Run' in df.columns else 0,
                'Unknown': (df['Run'] == 'Unknown').sum() if 'Run' in df.columns else 0,
            }
            report_data.append(log_summary)

        # --- Formatting ---
        headers = ["Callsign", "On-Time", "Total QSOs", "Dupes", "Run", "S&P", "Unknown"]
        has_on_time = any(row.get('On-Time') for row in report_data)
        if not has_on_time:
            headers.remove('On-Time')
            
        col_widths = {h: len(h) for h in headers}

        for row in report_data:
            for key, value in row.items():
                if key in col_widths:
                    col_widths[key] = max(col_widths.get(key, 0), len(str(value)))
        
        header_str = "  ".join([f"{h:<{col_widths[h]}}" for h in headers])
        separator = "-" * len(header_str)
        
        first_log = self.logs[0]
        contest_name = first_log.get_metadata().get('ContestName', 'UnknownContest')
        year = first_log.get_processed_data()['Date'].iloc[0].split('-')[0] if not first_log.get_processed_data().empty else "----"
        subtitle = f"{year} {contest_name} - {', '.join(all_calls)}"

        report_lines = [
            f"--- {self.report_name} ---".center(len(header_str)),
            subtitle.center(len(header_str)),
            "",
            "Note: Does Not Include Dupes" if not include_dupes else "Note: Includes Dupes",
            "",
            header_str,
            separator
        ]

        for row in report_data:
            data_parts = [f"{str(row.get(h, 'N/A')):<{col_widths[h]}}" for h in headers]
            report_lines.append("  ".join(data_parts))

        report_content = "\n".join(report_lines)
        os.makedirs(output_path, exist_ok=True)
        
        filename_calls = '_vs_'.join(sorted(all_calls))
        filename = f"{self.report_id}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"