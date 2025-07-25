# Contest Log Analyzer/contest_tools/reports/text_rate_sheet_by_run.py
#
# Purpose: A text report that generates a detailed hourly rate sheet with a
#          breakdown by Run, S&P, and Unknown QSOs for each band.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-25
# Version: 0.15.1-Beta
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

## [0.15.1-Beta] - 2025-07-25
### Changed
# - Renamed file, report_id, and titles from "...by_mode" to "...by_run"
#   to use correct terminology.

## [0.15.0-Beta] - 2025-07-25
# - Initial release of the Rate Sheet by Mode report.

from typing import List
import pandas as pd
import os
from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a detailed hourly rate sheet with a Run/S&P/Unknown breakdown.
    """
    @property
    def report_id(self) -> str:
        return "rate_sheet_by_run"

    @property
    def report_name(self) -> str:
        return "Rate Sheet (by Run/S&P)"

    @property
    def report_type(self) -> str:
        return "text"

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content.
        """
        include_dupes = kwargs.get('include_dupes', False)
        final_report_messages = []

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
            report_lines.append(f"CALLSIGN: {callsign}")
            report_lines.append("")
            report_lines.append("---------------------------------- Q S O   R a t e   S u m m a r y   (by Run/S&P) ----------------------------------")
            
            bands = ['160M', '80M', '40M', '20M', '15M', '10M']
            header1 = f"{'Hour':<5}" + "".join([f"{band.replace('M', ''):>12}" for band in bands]) + f"{'Total':>12}"
            header2 = f"{'':<5}" + "".join([f"{' R  S  U':>12}" for _ in bands]) + f"{' R    S    U':>12}"
            report_lines.append(header1)
            report_lines.append(header2)
            separator = "-" * len(header1)
            report_lines.append(separator)

            # --- Rate Calculation ---
            df['Hour'] = pd.to_numeric(df['Hour'])
            
            dates = sorted(df['Date'].unique())
            hours = range(24)
            full_index = pd.MultiIndex.from_product([dates, hours], names=['Date', 'Hour'])

            # Pivot to get counts for each Run/S&P/Unknown status per band and hour
            rate_data = df.pivot_table(index=['Date', 'Hour'], columns=['Band', 'Run'], aggfunc='size', fill_value=0)
            
            # Ensure all combinations exist for a clean table
            for band in bands:
                for run_status in ['Run', 'S&P', 'Unknown']:
                    if (band, run_status) not in rate_data.columns:
                        rate_data[(band, run_status)] = 0
            
            rate_data = rate_data.reindex(full_index, fill_value=0)

            # --- Format Rate Table ---
            for (date, hour), row in rate_data.iterrows():
                hour_str = f"{hour:02d}00"
                line = f"{hour_str:<5}"
                
                total_run = 0
                total_sp = 0
                total_unk = 0

                for band in bands:
                    run_count = row.get((band, 'Run'), 0)
                    sp_count = row.get((band, 'S&P'), 0)
                    unk_count = row.get((band, 'Unknown'), 0)
                    
                    total_run += run_count
                    total_sp += sp_count
                    total_unk += unk_count
                    
                    line += f" {run_count:>3}{sp_count:>3}{unk_count:>3} "
                
                line += f" {total_run:>4}{total_sp:>5}{total_unk:>4}"
                report_lines.append(line)

            # --- Footer Generation ---
            report_lines.append(separator)
            
            total_line = f"{'Total':<5}"
            grand_total_run = 0
            grand_total_sp = 0
            grand_total_unk = 0

            for band in bands:
                run_total = rate_data.get((band, 'Run'), pd.Series(0)).sum()
                sp_total = rate_data.get((band, 'S&P'), pd.Series(0)).sum()
                unk_total = rate_data.get((band, 'Unknown'), pd.Series(0)).sum()
                
                grand_total_run += run_total
                grand_total_sp += sp_total
                grand_total_unk += unk_total

                total_line += f" {run_total:>3}{sp_total:>3}{unk_total:>3} "
            
            total_line += f" {grand_total_run:>4}{grand_total_sp:>5}{grand_total_unk:>4}"
            report_lines.append(total_line)
            report_lines.append("")

            # --- Save Individual Report File ---
            report_content = "\n".join(report_lines)
            os.makedirs(output_path, exist_ok=True)
            filename = f"{self.report_id}_{callsign}.txt"
            filepath = os.path.join(output_path, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            final_report_messages.append(f"Text report saved to: {filepath}")

        return "\n".join(final_report_messages)
