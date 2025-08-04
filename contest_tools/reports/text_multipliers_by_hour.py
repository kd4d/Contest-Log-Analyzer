# Contest Log Analyzer/contest_tools/reports/text_multipliers_by_hour.py
#
# Purpose: A data-driven text report that generates an hourly summary of new
#          multipliers worked for a specific multiplier type.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-04
# Version: 0.26.7-Beta
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
## [0.26.7-Beta] - 2025-08-04
### Changed
# - Standardized the report header to use a two-line title.
### Fixed
# - Redundant 'Total' column is now omitted for single-band contests.
## [0.26.6-Beta] - 2025-08-03
### Changed
# - The report now uses the dynamic `valid_bands` list from the contest definition.
from typing import List, Dict, Set
import pandas as pd
import os
from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates an hourly summary of new multipliers worked for each log.
    """
    report_id: str = "multipliers_by_hour"
    report_name: str = "Multipliers by Hour"
    report_type: str = "text"
    supports_single = True

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
            year = df_full['Date'].iloc[0].split('-')[0] if not df_full.empty else "----"
            
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
            bands = log.contest_definition.valid_bands
            is_single_band = len(bands) == 1
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
                    
                    if totaling_method == 'once_per_log' or totaling_method == 'once_per_contest':
                        new_mults = current_hour_mults - worked_mults_overall
                        worked_mults_overall.update(new_mults)
                    else: # Default to sum_by_band
                        new_mults = current_hour_mults - worked_mults_by_band[band]
                        worked_mults_by_band[band].update(new_mults)
                    
                    hourly_results[band] = len(new_mults)
                    hourly_total += len(new_mults)
                
                if not is_single_band:
                    hourly_results['Total'] = hourly_total
                hourly_data.append(hourly_results)

            # --- Format the Report ---
            header1_parts = [f"{b.replace('M',''):>9}" for b in bands]
            if not is_single_band:
                header1_parts.append(f"{'Total':>9}")
            header1 = f"{'Date':<12}{'Hr':>4}" + "".join(header1_parts)
            separator = "-" * len(header1)
            
            subtitle = f"{year} {contest_name} - {callsign} ({mult_name})"
            report_lines = []
            report_lines.append(f"--- {self.report_name} ---".center(len(header1)))
            report_lines.append(subtitle.center(len(header1)))
            report_lines.append("")
            
            report_lines.append(header1)
            report_lines.append(separator)

            total_row = {band: 0 for band in bands}
            if not is_single_band:
                total_row['Total'] = 0

            for row_data in hourly_data:
                line = f"{row_data['Timestamp'].strftime('%Y-%m-%d'):<12}{row_data['Timestamp'].strftime('%H%M'):>4}"
                for band in bands:
                    line += f"{row_data[band]:>9}"
                    total_row[band] += row_data[band]
                if not is_single_band:
                    line += f"{row_data['Total']:>9}"
                    total_row['Total'] += row_data['Total']
                report_lines.append(line)

            report_lines.append(separator)
            total_line = f"{'Total':<12}{'':>4}"
            for band in bands:
                total_line += f"{total_row[band]:>9}"
            if not is_single_band:
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