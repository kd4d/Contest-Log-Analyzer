# Contest Log Analyzer/contest_tools/reports/text_multipliers_by_hour.py
#
# Purpose: A data-driven text report that generates an hourly summary of new
#          multipliers worked for a specific multiplier type.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-02
# Version: 0.26.5-Beta
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

## [0.26.5-Beta] - 2025-08-02
### Fixed
# - Corrected the logic for calculating new multipliers when the totaling
#   method is 'once_per_log' to use the correct set of previously
#   worked multipliers.
### Removed
# - Removed temporary diagnostic print statements.

## [0.26.4-Beta] - 2025-08-02
### Added
# - Added temporary diagnostic print statements to debug multiplier calculation.

## [0.25.0-Beta] - 2025-08-01
### Changed
# - The report now uses the pre-aligned master time index to display the
#   entire contest period, correctly showing gaps in operating time.

## [0.22.6-Beta] - 2025-07-31
### Changed
# - The report now uses the 'totaling_method' from the contest definition
#   to correctly calculate new multipliers for contests like WPX.

## [0.22.5-Beta] - 2025-07-31
### Changed
# - Implemented the boolean support properties, correctly identifying this
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
    supports_single = True

    @property
    def report_id(self) -> str:
        return "multipliers_by_hour"

    @property
    def report_name(self) -> str:
        return "Multipliers by Hour"

    @property
    def report_type(self) -> str:
        return "text"

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content.
        """
        mult_name = kwargs.get('mult_name')
        if not mult_name:
            return "Error: 'mult_name' argument is required for the Multipliers by Hour report."

        final_report_messages = []
        
        log_manager = getattr(self.logs[0], '_log_manager_ref', None)
        if not log_manager or log_manager.master_time_index is None:
            return "Error: Master time index not available for report."
        master_time_index = log_manager.master_time_index

        for log in self.logs:
            metadata = log.get_metadata()
            df_full = log.get_processed_data()
            callsign = metadata.get('MyCall', 'UnknownCall')
            contest_name = metadata.get('ContestName', 'UnknownContest')
            
            # --- Find the correct multiplier column and totaling method ---
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
            totaling_method = mult_rule.get('totaling_method', 'sum_by_band')

            # --- Data Preparation ---
            df = df_full[df_full['Dupe'] == False].copy()
            if df.empty or mult_column not in df.columns:
                msg = f"Skipping report for {callsign}: No valid '{mult_name}' data to report."
                print(msg)
                final_report_messages.append(msg)
                continue
            
            df = df[df[mult_column] != 'Unknown']
            df.dropna(subset=[mult_column], inplace=True)
            df['HourDT'] = pd.to_datetime(df['Datetime'], utc=True).dt.floor('h')

            # --- Calculation of New Multipliers per Hour ---
            bands = ['160M', '80M', '40M', '20M', '15M', '10M']
            worked_mults_by_band: Dict[str, Set] = {band: set() for band in bands}
            worked_mults_overall: Set = set()
            hourly_data = []

            for timestamp in master_time_index:
                hour_df = df[df['HourDT'] == timestamp]
                
                hourly_results = {'Timestamp': timestamp}
                hourly_total = 0
                
                for band in bands:
                    band_df = hour_df[hour_df['Band'] == band]
                    current_hour_mults = set(band_df[mult_column].unique())
                    
                    if totaling_method == 'once_per_log':
                        new_mults = current_hour_mults - worked_mults_overall
                        worked_mults_overall.update(new_mults)
                    else: # Default to sum_by_band
                        new_mults = current_hour_mults - worked_mults_by_band[band]
                        worked_mults_by_band[band].update(new_mults)
                    
                    hourly_results[band] = len(new_mults)
                    hourly_total += len(new_mults)
                
                hourly_results['Total'] = hourly_total
                hourly_data.append(hourly_results)

            # --- Format the Report ---
            report_lines = []
            report_lines.append(f"{callsign}")
            report_lines.append(f"{contest_name} - {mult_name} by Hour")
            report_lines.append("")

            header1 = f"{'Date':<12}{'Hr':>4}" + "".join([f"{b.replace('M',''):>9}" for b in bands]) + f"{'Total':>9}"
            header2 = f"{'':<12}{'':>4}" + "".join([f"{'':>9}" for b in bands]) + f"{'':>9}"
            separator = "-" * len(header1)
            
            report_lines.append(header1)
            report_lines.append(header2)
            report_lines.append(separator)

            total_row = {band: 0 for band in bands}
            total_row['Total'] = 0

            for row_data in hourly_data:
                line = f"{row_data['Timestamp'].strftime('%Y-%m-%d'):<12}{row_data['Timestamp'].strftime('%H%M'):>4}"
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
