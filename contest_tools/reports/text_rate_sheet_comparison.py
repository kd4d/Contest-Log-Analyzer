# Contest Log Analyzer/contest_tools/reports/text_rate_sheet_comparison.py
#
# Purpose: A text report that generates a comparative hourly rate sheet for two or more logs.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-31
# Version: 0.22.1-Beta
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

## [0.22.1-Beta] - 2025-07-31
### Changed
# - Implemented the boolean support properties, correctly identifying this
#   report as supporting both 'multi' and 'pairwise' modes.
# - Corrected the filename in the header comment to match the actual module name.

## [0.15.1-Beta] - 2025-07-25
### Fixed
# - Corrected the column alignment in the report table by properly indenting
#   the headers to match the data rows.

## [0.15.0-Beta] - 2025-07-25
# - Standardized version for final review. No functional changes.

from typing import List
import pandas as pd
import os
from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a comparative hourly rate sheet for two or more logs.
    """
    supports_multi = True
    supports_pairwise = True
    
    @property
    def report_id(self) -> str:
        return "rate_sheet_comparison"

    @property
    def report_name(self) -> str:
        return "Comparative Rate Sheet"

    @property
    def report_type(self) -> str:
        return "text"

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content, saves it to a file, and returns a summary.
        """
        include_dupes = kwargs.get('include_dupes', False)

        if len(self.logs) < 2:
            return "Error: The Comparative Rate Sheet report requires at least two logs."

        # --- Header Generation ---
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
        report_lines.append("---------------- Q S O   R a t e   S u m m a r y ---------------------")
        
        # Define column widths and prefix for alignment
        prefix_width = 11 # 2 spaces for indent + 7 for callsign + 2 for ': '
        band_width = 6
        hourly_width = 8
        cum_width = 12
        
        header1 = f"{'':<{prefix_width}}{'':>{band_width}}{'':>{band_width}}{'':>{band_width}}{'':>{band_width}}{'':>{band_width}}{'':>{band_width}}{'Hourly':>{hourly_width}}{'Cumulative':>{cum_width}}"
        header2 = f"{'':<{prefix_width}}{'160':>{band_width}}{'80':>{band_width}}{'40':>{band_width}}{'20':>{band_width}}{'15':>{band_width}}{'10':>{band_width}}{'Total':>{hourly_width}}{'Total':>{cum_width}}"
        report_lines.append(header1)
        report_lines.append(header2)
        separator = " " * prefix_width + "-" * (len(header2) - prefix_width)
        report_lines.append(separator)

        # --- Data Aggregation for All Logs ---
        processed_data = {}
        all_dates = set()
        bands = ['160M', '80M', '40M', '20M', '15M', '10M']
        cumulative_totals = {call: 0 for call in all_calls}

        for log in self.logs:
            callsign = log.get_metadata().get('MyCall', 'Unknown')
            df_full = log.get_processed_data()

            if not include_dupes and 'Dupe' in df_full.columns:
                df = df_full[df_full['Dupe'] == False].copy()
            else:
                df = df_full.copy()
            
            if df.empty:
                continue

            all_dates.update(df['Date'].unique())
            df['Hour'] = pd.to_numeric(df['Hour'])
            rate_data = df.pivot_table(index=['Date', 'Hour'], columns='Band', aggfunc='size', fill_value=0)
            
            for band in bands:
                if band not in rate_data.columns:
                    rate_data[band] = 0
            
            rate_data = rate_data[bands].fillna(0).astype(int)
            rate_data['Hourly Total'] = rate_data.sum(axis=1)
            processed_data[callsign] = rate_data

        # --- Format Combined Rate Table ---
        sorted_dates = sorted(list(all_dates))
        hours = range(24)
        full_index = pd.MultiIndex.from_product([sorted_dates, hours], names=['Date', 'Hour'])

        for date, hour in full_index:
            hour_str = f"{hour:02d}00"
            report_lines.append(hour_str)

            for callsign in all_calls:
                log_data = processed_data.get(callsign)
                hourly_total = 0
                if log_data is not None and (date, hour) in log_data.index:
                    row = log_data.loc[(date, hour)]
                    hourly_total = row['Hourly Total']
                    cumulative_totals[callsign] += hourly_total
                    line = (
                        f"  {callsign:<7}: "
                        f"{row.get('160M', 0):>{band_width}}"
                        f"{row.get('80M', 0):>{band_width}}"
                        f"{row.get('40M', 0):>{band_width}}"
                        f"{row.get('20M', 0):>{band_width}}"
                        f"{row.get('15M', 0):>{band_width}}"
                        f"{row.get('10M', 0):>{band_width}}"
                        f"{hourly_total:>{hourly_width}}"
                        f"{cumulative_totals[callsign]:>{cum_width}}"
                    )
                else:
                    # If log has no data for this hour, print a placeholder
                    line = (
                        f"  {callsign:<7}: "
                        f"{0:>{band_width}}"
                        f"{0:>{band_width}}"
                        f"{0:>{band_width}}"
                        f"{0:>{band_width}}"
                        f"{0:>{band_width}}"
                        f"{0:>{band_width}}"
                        f"{0:>{hourly_width}}"
                        f"{cumulative_totals[callsign]:>{cum_width}}"
                    )
                
                report_lines.append(line)
        
        # --- Save the Report to a File ---
        report_content = "\n".join(report_lines)
        os.makedirs(output_path, exist_ok=True)
        
        filename_calls = '_vs_'.join(sorted(all_calls))
        filename = f"{self.report_id}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"
