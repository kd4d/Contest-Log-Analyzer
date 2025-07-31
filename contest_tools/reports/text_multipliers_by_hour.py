# Contest Log Analyzer/contest_tools/reports/text_multipliers_by_hour.py
#
# Purpose: A data-driven text report that generates an hourly summary of new
#          multipliers worked for a specific multiplier type.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-31
# Version: 0.22.5-Beta
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

## [0.22.5-Beta] - 2025-07-31
### Changed
# - Implemented the 'comparison_mode' property, correctly identifying this
#   report as 'single' mode.

## [0.21.2-Beta] - 2025-07-28
### Fixed
# - The report now correctly filters out and ignores "Unknown" multipliers,
#   ensuring its totals are consistent with other reports.

## [0.21.0-Beta] - 2025-07-28
# - Initial release of the Multipliers by Hour report.

from typing import List, Dict, Set
import pandas as pd
import os
from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates an hourly summary of new multipliers worked for each log.
    """
    @property
    def report_id(self) -> str:
        return "multipliers_by_hour"

    @property
    def report_name(self) -> str:
        return "Multipliers by Hour"

    @property
    def report_type(self) -> str:
        return "text"

    @property
    def comparison_mode(self) -> str:
        return "single"

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content.
        """
        mult_name = kwargs.get('mult_name')
        if not mult_name:
            return "Error: 'mult_name' argument is required for the Multipliers by Hour report."

        final_report_messages = []

        for log in self.logs:
            metadata = log.get_metadata()
            df_full = log.get_processed_data()
            callsign = metadata.get('MyCall', 'UnknownCall')
            contest_name = metadata.get('ContestName', 'UnknownContest')
            
            # --- Find the correct multiplier column ---
            mult_rule = None
            for rule in log.contest_definition.multiplier_rules:
                if rule.get('name', '').lower() == mult_name.lower():
                    mult_rule = rule
                    break
            
            if not mult_rule or 'value_column' not in mult_rule:
                msg = f"Skipping report for {callsign}: Multiplier '{mult_name}' not found in contest definition."
                print(msg)
                final_report_messages.append(msg)
                continue

            mult_column = mult_rule['value_column']

            # --- Data Preparation ---
            df = df_full[df_full['Dupe'] == False].copy()
            if df.empty or mult_column not in df.columns:
                msg = f"Skipping report for {callsign}: No valid '{mult_name}' data to report."
                print(msg)
                final_report_messages.append(msg)
                continue
            
            # --- Filter out "Unknown" multipliers ---
            df = df[df[mult_column] != 'Unknown']

            df.dropna(subset=[mult_column], inplace=True)
            df['Hour'] = pd.to_numeric(df['Hour'])

            # --- Calculation of New Multipliers per Hour ---
            bands = ['160M', '80M', '40M', '20M', '15M', '10M']
            worked_mults_by_band: Dict[str, Set] = {band: set() for band in bands}
            hourly_data = []

            dates = sorted(df['Date'].unique())
            hours = range(24)
            full_index = pd.MultiIndex.from_product([dates, hours], names=['Date', 'Hour'])

            for date, hour in full_index:
                hour_df = df[(df['Date'] == date) & (df['Hour'] == hour)]
                
                hourly_results = {'Date': date, 'Hour': f"{hour:02d}"}
                hourly_total = 0
                
                for band in bands:
                    band_df = hour_df[hour_df['Band'] == band]
                    new_mults_on_band = set(band_df[mult_column].unique()) - worked_mults_by_band[band]
                    
                    hourly_results[band] = len(new_mults_on_band)
                    hourly_total += len(new_mults_on_band)
                    worked_mults_by_band[band].update(new_mults_on_band)
                
                hourly_results['Total'] = hourly_total
                hourly_data.append(hourly_results)

            # --- Format the Report ---
            report_lines = []
            report_lines.append(f"{callsign}")
            report_lines.append(f"{contest_name} - {mult_name} by Hour")
            report_lines.append("")

            header1 = f"{'Date':<12}{'Hr':>4}" + "".join([f"{b.replace('M',''):>9}" for b in bands]) + f"{'Total':>9}"
            header2 = f"{'':<12}{'':>4}" + "".join([f"{'CW':>9}" for b in bands]) + f"{'':>9}"
            separator = "-" * len(header1)
            
            report_lines.append(header1)
            report_lines.append(header2)
            report_lines.append(separator)

            total_row = {band: 0 for band in bands}
            total_row['Total'] = 0

            for row_data in hourly_data:
                line = f"{row_data['Date']:<12}{row_data['Hour']:>4}"
                for band in bands:
                    line += f"{row_data[band]:>9}"
                    total_row[band] += row_data[band]
                line += f"{row_data['Total']:>9}"
                total_row['Total'] += row_data['Total']
                report_lines.append(line)

            report_lines.append(separator)
            total_line = f"{'Total':<12}{'':>4}"
            for band in bands:
                total_line += f"{total_row[band]:>9}"
            total_line += f"{total_row['Total']:>9}"
            report_lines.append(total_line)

            # --- Save the Report File ---
            report_content = "\n".join(report_lines)
            os.makedirs(output_path, exist_ok=True)
            filename = f"{self.report_id}_{mult_name.lower()}_{callsign}.txt"
            filepath = os.path.join(output_path, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            final_report_messages.append(f"Text report saved to: {filepath}")

        return "\n".join(final_report_messages)
