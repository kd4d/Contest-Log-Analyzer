# Contest Log Analyzer/contest_tools/reports/text_summary.py
#
# Purpose: An example text report that generates a simple QSO summary.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-24
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

## [0.14.0-Beta] - 2025-07-24
### Changed
# - Updated to correctly handle and display the new "Unknown" classification
#   in the QSO summary.

from typing import List
import os
from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a text summary of key statistics for each log.
    """
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

        report_lines = [f"--- {self.report_name} ---"]
        if include_dupes:
            report_lines.append("Note: Includes Dupes")
        else:
            report_lines.append("Note: Does Not Include Dupes")
        report_lines.append("")

        for log in self.logs:
            callsign = log.get_metadata().get('MyCall', 'Unknown')
            df_full = log.get_processed_data()
            
            if not include_dupes and 'Dupe' in df_full.columns:
                df = df_full[df_full['Dupe'] == False].copy()
                qso_label = "Total QSOs (without dupes)"
            else:
                df = df_full.copy()
                qso_label = "Total QSOs (with dupes)"
            
            total_qsos = len(df)
            total_dupes = df_full['Dupe'].sum()
            
            report_lines.append(f"Log: {callsign}")
            report_lines.append(f"  - {qso_label}: {total_qsos}")
            report_lines.append(f"  - Total Dupes (in original log): {total_dupes}")
            
            if 'Run' in df.columns:
                run_qsos = (df['Run'] == 'Run').sum()
                sp_qsos = (df['Run'] == 'S&P').sum()
                unknown_qsos = (df['Run'] == 'Unknown').sum()
                report_lines.append(f"  - Run QSOs: {run_qsos}")
                report_lines.append(f"  - S&P QSOs: {sp_qsos}")
                report_lines.append(f"  - Unknown QSOs: {unknown_qsos}")
            
            report_lines.append("")

        report_content = "\n".join(report_lines)
        os.makedirs(output_path, exist_ok=True)
        filename = f"{self.report_id}_report.txt"
        filepath = os.path.join(output_path, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"
