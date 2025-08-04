# Contest Log Analyzer/contest_tools/reports/text_rate_sheet.py
#
# Purpose: A text report that generates a detailed hourly rate sheet.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-03
# Version: 0.28.19-Beta
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
## [0.28.19-Beta] - 2025-08-03
### Changed
# - The report now uses the dynamic `valid_bands` list from the contest
#   definition instead of a hardcoded list.
## [0.28.18-Beta] - 2025-08-03
### Added
# - Added a "Total" row to the bottom of the rate table to show the
#   total QSO count for each individual band.
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
## [0.22.0-Beta] - 2025-07-31
### Changed
# - Implemented the boolean support properties, correctly identifying this
#   report as 'single'.
from typing import List
import pandas as pd
import os
from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import align_logs_by_time

class Report(ContestReport):
    """
    Generates a detailed hourly rate sheet for each log.
    """
    report_id: str = "rate_sheet"
    report_name: str = "Rate Sheet"
    report_type: str = "text"
    supports_single = True
    
    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content.
        """
        include_dupes = kwargs.get('include_dupes', False)
        final_report_messages = []

        if not self.logs:
            return "No logs to process."
            
        log_manager = getattr(self.logs[0], '_log_manager_ref', None)
        if not log_manager or log_manager.master_time_index is None:
            print("Warning: Master time index not available. Rate sheet may be incomplete.")
            master_time_index = pd.DatetimeIndex([])
        else:
            master_time_index = log_manager.master_time_index

        for log in self.logs:
            metadata = log.get_metadata()
            df_full = log.get_processed_data()
            callsign = metadata.get('MyCall', 'UnknownCall')

            if df_full.empty:
                print(f"Skipping rate sheet for {callsign}: No valid QSOs to report.")
                continue

            if not include_dupes and 'Dupe' in df_full.columns:
                df = df_full[df_full['Dupe'] == False].copy()
            else:
                df = df_full.copy()

            year = df['Date'].iloc[0].split('-')[0] if not df.empty else "UnknownYear"
            contest_name = metadata.get('ContestName', 'UnknownContest')

            report_lines = []
            report_lines.append(f"{year} {contest_name}")
            report_lines.append("")
            report_lines.append(f"CONTEST: {metadata.get('ContestName', '')}")
            report_lines.append(f"CALLSIGN: {callsign}")
            report_lines.append(f"CATEGORY-OPERATOR: {metadata.get('CategoryOperator', '')}")
            report_lines.append(f"CATEGORY-TRANSMITTER: {metadata.get('CategoryTransmitter', '')}")
            report_lines.append(f"OPERATORS: {metadata.get('Operators', '')}") 
            report_lines.append("")
            report_lines.append("---------------- Q S O   R a t e   S u m m a r y -----------------")
            
            bands = log.contest_definition.valid_bands
            
            header1_parts = [f"{'Hour':<5}"] + [f"{b.replace('M',''):>5}" for b in bands]
            header1 = " ".join(header1_parts) + f" {'Hourly':>7} {'Cumulative':>11}"
            header2 = f"{'':<5}" + "".join([f"{'':>6}" for _ in bands]) + f" {'Total':>7} {'Total':>11}"
            
            report_lines.append(header1)
            report_lines.append(header2)
            separator = "-" * len(header1)
            report_lines.append(separator)
            
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
            rate_data['Cumulative Total'] = rate_data['Hourly Total'].cumsum()

            for timestamp, row in rate_data.iterrows():
                hour_str = timestamp.strftime('%H%M')
                line_parts = [f"{hour_str:<5}"]
                for band in bands:
                    line_parts.append(f"{row.get(band, 0):>5}")
                
                line = " ".join(line_parts)
                line += f" {row['Hourly Total']:>7} "
                line += f"{row['Cumulative Total']:>11}"
                report_lines.append(line)

            report_lines.append(separator)
            
            total_line_parts = [f"{'Total':<5}"]
            for band in bands:
                total_line_parts.append(f"{rate_data[band].sum():>5}")
            total_line = " ".join(total_line_parts)
            total_line += f" {rate_data['Hourly Total'].sum():>7}"
            report_lines.append(total_line)
            report_lines.append("")

            gross_qsos = len(df_full)
            dupes = df_full['Dupe'].sum()
            net_qsos = gross_qsos - dupes
            report_lines.append(f"Gross QSOs={gross_qsos}     Dupes={dupes}     Net QSOs={net_qsos if not include_dupes else gross_qsos}")
            
            report_content = "\n".join(report_lines)
            os.makedirs(output_path, exist_ok=True)
            filename = f"{self.report_id}_{callsign}.txt"
            filepath = os.path.join(output_path, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            final_report_messages.append(f"Text report saved to: {filepath}")

        return "\n".join(final_report_messages)