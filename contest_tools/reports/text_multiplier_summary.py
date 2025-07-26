# Contest Log Analyzer/contest_tools/reports/text_multiplier_summary.py
#
# Purpose: A data-driven text report that generates a summary of QSOs for a
#          specific multiplier type (e.g., Countries, Zones).
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-26
# Version: 0.16.1-Beta
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

## [0.16.1-Beta] - 2025-07-26
### Fixed
# - Added a specific check to correctly handle the singular form of "Countries",
#   preventing it from being incorrectly changed to "Countrie".

## [0.16.0-Beta] - 2025-07-26
### Fixed
# - Corrected the logic to handle two-letter continent abbreviations (e.g., 'NA')
#   from the CTY.DAT file, allowing the report to generate correctly.

from typing import List
import pandas as pd
import os
from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a summary of QSOs per multiplier, broken down by band.
    """
    @property
    def report_id(self) -> str:
        return "multiplier_summary"

    @property
    def report_name(self) -> str:
        return "Multiplier Summary"

    @property
    def report_type(self) -> str:
        return "text"

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content.
        """
        include_dupes = kwargs.get('include_dupes', False)
        mult_name = kwargs.get('mult_name')

        if not mult_name:
            return "Error: 'mult_name' argument is required for the Multiplier Summary report."

        first_log = self.logs[0]
        first_log_def = first_log.contest_definition
        mult_rule = None
        for rule in first_log_def.multiplier_rules:
            if rule.get('name', '').lower() == mult_name.lower():
                mult_rule = rule
                break
        
        if not mult_rule or 'value_column' not in mult_rule:
            return f"Error: Multiplier type '{mult_name}' not found in definition for {first_log_def.contest_name}."

        mult_column = mult_rule['value_column']
        name_column = mult_rule.get('name_column')

        # --- Data Preparation ---
        all_dfs = []
        for log in self.logs:
            df_full = log.get_processed_data()
            if not include_dupes and 'Dupe' in df_full.columns:
                df = df_full[df_full['Dupe'] == False].copy()
            else:
                df = df_full.copy()
            
            df['MyCall'] = log.get_metadata().get('MyCall', 'Unknown')
            all_dfs.append(df)

        if not all_dfs:
            return "No data available to generate report."

        combined_df = pd.concat(all_dfs, ignore_index=True)
        
        if combined_df.empty or mult_column not in combined_df.columns:
            return f"No '{mult_name}' multiplier data to report."
            
        combined_df.dropna(subset=[mult_column], inplace=True)

        # --- Report Generation ---
        bands = ['160M', '80M', '40M', '20M', '15M', '10M']
        all_calls = sorted(combined_df['MyCall'].unique())
        
        # Create the main pivot table
        pivot = combined_df.pivot_table(
            index=[mult_column, 'MyCall'],
            columns='Band',
            aggfunc='size',
            fill_value=0
        )

        # Create a name mapping if applicable
        name_map = {}
        if name_column and name_column in combined_df.columns:
            name_map = combined_df.dropna(subset=[name_column]).set_index(mult_column)[name_column].to_dict()

        # Ensure all bands are present
        for band in bands:
            if band not in pivot.columns:
                pivot[band] = 0
        pivot = pivot[bands] # Enforce order
        pivot['Total'] = pivot.sum(axis=1)

        # --- Formatting ---
        if mult_name.lower() == 'countries':
            first_col_header = 'Country'
        else:
            first_col_header = mult_name[:-1] if mult_name.lower().endswith('s') else mult_name
            
        header = f"{first_col_header:<17}" + "".join([f"{b.replace('M',''):>7}" for b in bands]) + f"{'Total':>7}"
        separator = "-" * len(header)
        
        report_lines = [f"-------------------- {mult_name} S u m m a r y -------------------".center(len(header))]
        report_lines.append(header)
        report_lines.append(separator)

        sorted_mults = sorted(pivot.index.get_level_values(0).unique())

        for mult in sorted_mults:
            mult_display = str(mult)
            if name_column:
                mult_display = f"{mult} ({name_map.get(mult, '')})"
            report_lines.append(mult_display)
            
            mult_data = pivot.loc[mult]
            for call in all_calls:
                if call in mult_data.index:
                    row = mult_data.loc[call]
                    line = f"        {call:<8}:"
                    for band in bands:
                        line += f"{row.get(band, 0):>7}"
                    line += f"{row.get('Total', 0):>7}"
                    report_lines.append(line)

        # --- Total Footer ---
        report_lines.append(separator)
        report_lines.append("Total")
        
        total_pivot = combined_df.pivot_table(index='MyCall', columns='Band', aggfunc='size', fill_value=0)
        for band in bands:
            if band not in total_pivot.columns:
                total_pivot[band] = 0
        total_pivot = total_pivot[bands]
        total_pivot['Total'] = total_pivot.sum(axis=1)

        for call in all_calls:
             if call in total_pivot.index:
                row = total_pivot.loc[call]
                line = f"        {call:<8}:"
                for band in bands:
                    line += f"{row.get(band, 0):>7}"
                line += f"{row.get('Total', 0):>7}"
                report_lines.append(line)

        # --- Save the Report File ---
        report_content = "\n".join(report_lines)
        os.makedirs(output_path, exist_ok=True)
        
        filename_calls = '_vs_'.join(sorted(all_calls))
        filename = f"{self.report_id}_{mult_name.lower()}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"
