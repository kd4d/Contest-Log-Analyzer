# Contest Log Analyzer/contest_tools/reports/text_rate_sheet_comparison.py
#
# Purpose: A text report that generates a comparative hourly rate sheet for two or more logs.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-03
# Version: 0.28.20-Beta
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
## [0.28.20-Beta] - 2025-08-03
### Changed
# - The report now uses the dynamic `valid_bands` list from the contest
#   definition instead of a hardcoded list.
## [0.28.19-Beta] - 2025-08-03
### Added
# - Added a "TOTALS" section to the bottom of the report to show the
#   total QSO count for each individual band, per log.
#
## [0.26.1-Beta] - 2025-08-02
### Fixed
# - Converted report_id, report_name, and report_type from @property methods
#   to simple class attributes to fix a bug in the report generation loop.
## [0.26.6-Beta] - 2025-08-02
### Fixed
# - Corrected a timezone mismatch by ensuring the QSO 'Datetime' column is
#   converted to UTC before creating the pivot table for alignment.
## [0.25.0-Beta] - 2025-08-01
### Changed
# - The report now uses the pre-aligned master time index to display the
#   entire contest period, correctly showing gaps in operating time.
## [0.22.1-Beta] - 2025-07-31
### Changed
# - Implemented the boolean support properties, correctly identifying this
#   report as supporting both 'multi' and 'pairwise' modes.
from typing import List
import pandas as pd
import os
from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a comparative hourly rate sheet for two or more logs.
    """
    report_id: str = "rate_sheet_comparison"
    report_name: str = "Comparative Rate Sheet"
    report_type: str = "text"
    supports_multi = True
    supports_pairwise = True
    
    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content, saves it to a file, and returns a summary.
        """
        include_dupes = kwargs.get('include_dupes', False)

        if len(self.logs) < 2:
            return "Error: The Comparative Rate Sheet report requires at least two logs."
            
        log_manager = getattr(self.logs[0], '_log_manager_ref', None)
        if not log_manager or log_manager.master_time_index is None:
            return "Error: Master time index not available for rate sheet report."
            
        master_time_index = log_manager.master_time_index

        all_calls = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in self.logs])
        first_log_meta = self.logs[0].get_metadata()

        report_lines = []
        report_lines.append(f"CALLSIGNS: {', '.join(all_calls)}")
        report_lines.append(f"CONTEST:   {first_log_meta.get('ContestName', '')}")
        report_lines.append("OPERATORS:")
        for log in self.logs:
            call = log.get_metadata().get('MyCall', 'Unknown')
            operators = log.get_metadata().get('Operators', '')
            report_lines.append(f"  {call}: {operators}")
        report_lines.append(f"CATEGORY: {first_log_meta.get('CategoryOperator', '')}")
        report_lines.append("")
        report_lines.append("---------------- Q S O   R a te   S u m m a r y ---------------------")
        
        prefix_width = 11
        band_width = 6
        hourly_width = 8
        cum_width = 12
        
        bands = self.logs[0].contest_definition.valid_bands
        
        header1_parts = [f"{'':<{prefix_width}}"] + [f"{b.replace('M',''):>{band_width}}" for b in bands]
        header1 = "".join(header1_parts) + f"{'Hourly':>{hourly_width}}{'Cumulative':>{cum_width}}"
        header2 = f"{'':<{prefix_width}}" + "".join([f"{'':>{band_width}}" for _ in bands]) + f"{'Total':>{hourly_width}}{'Total':>{cum_width}}"
        report_lines.append(header1)
        report_lines.append(header2)
        separator = " " * prefix_width + "-" * (len(header2) - prefix_width)
        report_lines.append(separator)

        processed_data = {}
        cumulative_totals = {call: 0 for call in all_calls}

        for log in self.logs:
            callsign = log.get_metadata().get('MyCall', 'Unknown')
            df_full = log.get_processed_data()

            if not include_dupes and 'Dupe' in df_full.columns:
                df = df_full[df_full['Dupe'] == False].copy()
            else:
                df = df_full.copy()
            
            if df.empty:
                rate_data = pd.DataFrame(0, index=master_time_index, columns=bands)
            else:
                df['Datetime'] = pd.to_datetime(df['Datetime'], utc=True)
                rate_data = df.pivot_table(index=df['Datetime'].dt.floor('h'), 
                                           columns='Band', 
                                           aggfunc='size', 
                                           fill_value=0)
                rate_data = rate_data.reindex(master_time_index, fill_value=0)

            for band in bands:
                if band not in rate_data.columns:
                    rate_data[band] = 0
            
            rate_data = rate_data[bands].fillna(0).astype(int)
            rate_data['Hourly Total'] = rate_data.sum(axis=1)
            processed_data[callsign] = rate_data

        for timestamp in master_time_index:
            hour_str = timestamp.strftime('%H%M')
            report_lines.append(hour_str)

            for callsign in all_calls:
                log_data = processed_data.get(callsign)
                hourly_total = 0
                if log_data is not None and timestamp in log_data.index:
                    row = log_data.loc[timestamp]
                    hourly_total = row['Hourly Total']
                    cumulative_totals[callsign] += hourly_total
                    
                    line_parts = [f"  {callsign:<7}: "]
                    for band in bands:
                        line_parts.append(f"{row.get(band, 0):>{band_width}}")
                    line = "".join(line_parts)
                    line += f"{hourly_total:>{hourly_width}}{cumulative_totals[callsign]:>{cum_width}}"
                else:
                    line_parts = [f"  {callsign:<7}: "]
                    for band in bands:
                        line_parts.append(f"{0:>{band_width}}")
                    line = "".join(line_parts)
                    line += f"{0:>{hourly_width}}{cumulative_totals[callsign]:>{cum_width}}"
                
                report_lines.append(line)
        
        # --- Totals Section ---
        report_lines.append(separator)
        report_lines.append("TOTALS")
        for callsign in all_calls:
            log_data = processed_data.get(callsign)
            if log_data is not None:
                total_line_parts = [f"  {callsign:<7}: "]
                grand_total = 0
                for band in bands:
                    band_total = log_data[band].sum()
                    total_line_parts.append(f"{band_total:>{band_width}}")
                    grand_total += band_total
                total_line = "".join(total_line_parts)
                total_line += f"{grand_total:>{hourly_width}}"
                report_lines.append(total_line)

        report_content = "\n".join(report_lines)
        os.makedirs(output_path, exist_ok=True)
        
        filename_calls = '_vs_'.join(sorted(all_calls))
        filename = f"{self.report_id}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"