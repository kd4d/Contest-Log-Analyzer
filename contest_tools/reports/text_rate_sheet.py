# Contest Log Analyzer/contest_tools/reports/text_rate_sheet.py
#
# Purpose: A text report that generates a detailed hourly rate sheet.
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
# - The report now generates a separate output file for each log.
# - Added a "YYYY Contest-Name" header to the top of each report file.
# - The generate() method now saves files directly and returns a summary message.

from typing import List
import pandas as pd
import os
from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a detailed hourly rate sheet for each log.
    """
    @property
    def report_id(self) -> str:
        return "rate_sheet"

    @property
    def report_name(self) -> str:
        return "Rate Sheet"

    @property
    def report_type(self) -> str:
        return "text"

    def generate(self, output_path: str, include_dupes: bool = False) -> str:
        
        os.makedirs(output_path, exist_ok=True)
        
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
                print(f"Skipping rate sheet for {callsign}: No valid QSOs to report.")
                continue

            # --- Header Generation ---
            first_qso_date = df['Date'].iloc[0]
            year = first_qso_date.split('-')[0] if first_qso_date else "UnknownYear"
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
            
            header1 = f"{'':<5} {'':>5} {'':>5} {'':>5} {'':>5} {'':>5} {'':>5} {'Hourly':>7} {'Cumulative':>11}"
            header2 = f"{'Hour':<5} {'160':>5} {'80':>5} {'40':>5} {'20':>5} {'15':>5} {'10':>5} {'Total':>7} {'Total':>11}"
            report_lines.append(header1)
            report_lines.append(header2)
            separator = "-" * len(header2)
            report_lines.append(separator)

            # --- Rate Calculation ---
            df['Hour'] = pd.to_numeric(df['Hour'])
            bands = ['160M', '80M', '40M', '20M', '15M', '10M']
            
            dates = sorted(df['Date'].unique())
            hours = range(24)
            full_index = pd.MultiIndex.from_product([dates, hours], names=['Date', 'Hour'])

            rate_data = df.pivot_table(index=['Date', 'Hour'], columns='Band', aggfunc='size', fill_value=0)
            rate_data = rate_data.reindex(full_index, fill_value=0)

            for band in bands:
                if band not in rate_data.columns:
                    rate_data[band] = 0
            
            rate_data = rate_data[bands].fillna(0).astype(int)

            rate_data['Hourly Total'] = rate_data.sum(axis=1)
            rate_data['Cumulative Total'] = rate_data['Hourly Total'].cumsum()

            # --- Format Rate Table ---
            for (date, hour), row in rate_data.iterrows():
                hour_str = f"{hour:02d}"
                line = (
                    f"{hour_str:<5} "
                    f"{row.get('160M', 0):>5} "
                    f"{row.get('80M', 0):>5} "
                    f"{row.get('40M', 0):>5} "
                    f"{row.get('20M', 0):>5} "
                    f"{row.get('15M', 0):>5} "
                    f"{row.get('10M', 0):>5} "
                    f"{row['Hourly Total']:>7} "
                    f"{row['Cumulative Total']:>11}"
                )
                report_lines.append(line)

            # --- Footer Generation ---
            report_lines.append(separator)
            total_line = (
                f"{'Total':<5} "
                f"{rate_data['160M'].sum():>5} "
                f"{rate_data['80M'].sum():>5} "
                f"{rate_data['40M'].sum():>5} "
                f"{rate_data['20M'].sum():>5} "
                f"{rate_data['15M'].sum():>5} "
                f"{rate_data['10M'].sum():>5} "
                f"{rate_data['Hourly Total'].sum():>7}"
            )
            report_lines.append(total_line)
            report_lines.append("")

            gross_qsos = len(df_full)
            dupes = df_full['Dupe'].sum()
            net_qsos = gross_qsos - dupes
            report_lines.append(f"Gross QSOs={gross_qsos}      Dupes={dupes}      Net QSOs={net_qsos if not include_dupes else gross_qsos}")
            
            # --- Save Individual Report File ---
            report_content = "\n".join(report_lines)
            filename = f"{self.report_id}_{callsign}.txt"
            filepath = os.path.join(output_path, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"Text report saved to: {filepath}")

        return f"Generated {len(self.logs)} rate sheet file(s)."
