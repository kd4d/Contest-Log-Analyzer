# Contest Log Analyzer/contest_tools/reports/text_summary.py
#
# Purpose: An example text report that generates a simple QSO summary.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-21
# Version: 0.11.0-Beta
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

## [0.11.0-Beta] - 2025-07-21
### Changed
# - Removed the top-level note about duplicate inclusion.
# - Changed the 'Total QSOs' label to be more explicit about dupe inclusion
#   (e.g., 'Total QSOs (without dupes)').

from typing import List
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

    def generate(self, output_path: str, include_dupes: bool = False) -> str:
        report_lines = [f"--- {self.report_name} ---", ""]

        for log in self.logs:
            callsign = log.get_metadata().get('MyCall', 'Unknown')
            df_full = log.get_processed_data()
            
            # Filter out dupes unless specified otherwise
            if not include_dupes and 'Dupe' in df_full.columns:
                df = df_full[df_full['Dupe'] == False].copy()
                qso_label = "Total QSOs (without dupes)"
            else:
                df = df_full.copy()
                qso_label = "Total QSOs (with dupes)"
            
            total_qsos = len(df)
            total_dupes = df_full['Dupe'].sum() # Always show total dupes from original log
            
            report_lines.append(f"Log: {callsign}")
            report_lines.append(f"  - {qso_label}: {total_qsos}")
            report_lines.append(f"  - Total Dupes (in original log): {total_dupes}")
            
            if 'Run' in df.columns:
                run_qsos = (df['Run'] == 'Run').sum()
                sp_qsos = (df['Run'] == 'S&P').sum()
                report_lines.append(f"  - Run QSOs: {run_qsos}")
                report_lines.append(f"  - S&P QSOs: {sp_qsos}")
            
            report_lines.append("")

        return "\n".join(report_lines)
