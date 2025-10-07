# contest_tools/reports/text_summary.py
#
# Purpose: An example text report that generates a simple QSO summary.
#
# Author: Gemini AI
# Date: 2025-10-01
# Version: 0.90.0-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# --- Revision History ---
# [0.90.0-Beta] - 2025-10-01
# Set new baseline version for release.

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
        
        table_header = "  ".join([f"{h:<{col_widths[h]}}" for h in headers])
        table_width = len(table_header)
        separator = "-" * table_width
        
        first_log = self.logs[0]
        contest_name = first_log.get_metadata().get('ContestName', 'UnknownContest')
        year = first_log.get_processed_data()['Date'].iloc[0].split('-')[0] if not first_log.get_processed_data().empty else "----"
        
        title1 = f"--- {self.report_name} ---"
        title2 = f"{year} {contest_name} - {', '.join(all_calls)}"
        
        report_lines = []
        if len(title1) > table_width or len(title2) > table_width:
            header_width = max(len(title1), len(title2))
            report_lines.append(f"{title1.ljust(header_width)}")
            report_lines.append(f"{title2.center(header_width)}")
        else:
            header_width = table_width
            report_lines.append(title1.center(header_width))
            report_lines.append(title2.center(header_width))
        
        report_lines.extend([
            "",
            "Note: Does Not Include Dupes" if not include_dupes else "Note: Includes Dupes",
            "",
            table_header,
            separator
        ])

        for row in report_data:
            data_parts = [f"{str(row.get(h, 'N/A')):<{col_widths[h]}}" for h in headers]
            report_lines.append("  ".join(data_parts))

        report_content = "\n".join(report_lines) + "\n"
        os.makedirs(output_path, exist_ok=True)
        
        filename_calls = '_vs_'.join(sorted(all_calls))
        filename = f"{self.report_id}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"
