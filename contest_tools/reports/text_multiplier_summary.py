# Contest Log Analyzer/contest_tools/reports/text_multiplier_summary.py
#
# Purpose: A data-driven text report that generates a summary of QSOs for a
#          specific multiplier type (e.g., Countries, Zones).
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-31
# Version: 0.22.4-Beta
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

## [0.22.4-Beta] - 2025-07-31
### Changed
# - Implemented the boolean support properties, correctly identifying this
#   report as supporting both 'multi' and 'pairwise' modes.

## [0.21.9-Beta] - 2025-07-29
### Changed
# - "Unknown" multipliers are no longer included in the main report body or totals.
# - A new "Unknown Total" line has been added to the footer to show these counts separately.
# - The diagnostic header is now dynamic (e.g., "Callsigns with unknown Country").

## [0.21.3-Beta] - 2025-07-28
### Added
# - The report now includes a diagnostic list at the end, showing all unique
#   callsigns that resulted in an "Unknown" multiplier classification.

## [0.17.0-Beta] - 2025-07-27
### Fixed
# - Corrected the pluralization logic for the first column header to specifically
#   handle "Countries" -> "Country", preventing it from becoming "Countrie".
# - Added data cleaning for multiplier names to correctly parse semicolon (;)
#   comments from source files, preventing stray data from appearing.
# - Optimized the footer calculation by summing the existing pivot table,
#   avoiding the need to process the entire dataset a second time.
# - Made the multiplier name mapping logic more robust by handling potential
#   duplicate entries from the combined log data.

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

    @property
    def supports_multi(self) -> bool:
        return True

    @property
    def supports_pairwise(self) -> bool:
        return True

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content.
        """
        include_dupes = kwargs.get('include_dupes', False)
        mult_name = kwargs.get('mult_name')

        if not mult_name:
            return "Error: 'mult_name' argument is required for the Multiplier Summary report."

        # --- Find the correct multiplier column ---
        first_log = self.logs[0]
        mult_rule = None
        for rule in first_log.contest_definition.multiplier_rules:
            if rule.get('name', '').lower() == mult_name.lower():
                mult_rule = rule
                break
        
        if not mult_rule or 'value_column' not in mult_rule:
            return f"Error: Multiplier type '{mult_name}' not found in definition for {first_log.contest_definition.contest_name}."

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

        # --- Separate Unknowns and Prepare Main Data ---
        unknown_df = combined_df[combined_df[mult_column] == 'Unknown']
        main_df = combined_df[combined_df[mult_column] != 'Unknown']
        
        unique_unknown_calls = sorted(unknown_df['Call'].unique())
        
        # --- Report Generation ---
        bands = ['160M', '80M', '40M', '20M', '15M', '10M']
        all_calls = sorted(main_df['MyCall'].unique())
        
        pivot = main_df.pivot_table(
            index=[mult_column, 'MyCall'], columns='Band', aggfunc='size', fill_value=0
        )

        name_map = {}
        if name_column and name_column in main_df.columns:
            name_map_df = main_df[[mult_column, name_column]].dropna().drop_duplicates()
            name_map = name_map_df.set_index(mult_column)[name_column].to_dict()

        for band in bands:
            if band not in pivot.columns: pivot[band] = 0
        pivot = pivot[bands]
        pivot['Total'] = pivot.sum(axis=1)

        # --- Formatting ---
        if mult_name.lower() == 'countries':
            first_col_header = 'Country'
        else:
            first_col_header = mult_name[:-1] if mult_name.lower().endswith('s') else mult_name
            
        header = f"{first_col_header:<25}" + "".join([f"{b.replace('M',''):>7}" for b in bands]) + f"{'Total':>7}"
        separator = "-" * len(header)
        
        report_lines = [f"-------------------- {mult_name} S u m m a r y -------------------".center(len(header))]
        report_lines.append(header)
        report_lines.append(separator)

        sorted_mults = sorted(pivot.index.get_level_values(0).unique())

        for mult in sorted_mults:
            mult_display = str(mult)
            if name_column:
                mult_full_name = name_map.get(mult, '')
                if pd.isna(mult_full_name): clean_name = ''
                else: clean_name = str(mult_full_name).split(';')[0].strip()
                mult_display = f"{mult} ({clean_name})"

            report_lines.append(f"{mult_display:<25}")
            
            mult_data = pivot.loc[mult]
            for call in all_calls:
                if call in mult_data.index:
                    row = mult_data.loc[call]
                    line = f"  {call:<21}"
                    for band in bands: line += f"{row.get(band, 0):>7}"
                    line += f"{row.get('Total', 0):>7}"
                    report_lines.append(line)

        # --- Footer ---
        report_lines.append(separator)
        report_lines.append(f"{'Total':<25}")
        
        total_pivot = pivot.groupby(level='MyCall').sum()
        for call in all_calls:
             if call in total_pivot.index:
                row = total_pivot.loc[call]
                line = f"  {call:<21}"
                for band in bands: line += f"{row.get(band, 0):>7}"
                line += f"{row.get('Total', 0):>7}"
                report_lines.append(line)

        # --- Add Unknown Total Line ---
        if not unknown_df.empty:
            report_lines.append(f"{'Unknown Total':<25}")
            unknown_pivot = unknown_df.pivot_table(index='MyCall', columns='Band', aggfunc='size', fill_value=0)
            for band in bands:
                if band not in unknown_pivot.columns: unknown_pivot[band] = 0
            unknown_pivot = unknown_pivot[bands]
            unknown_pivot['Total'] = unknown_pivot.sum(axis=1)

            for call in all_calls:
                if call in unknown_pivot.index:
                    row = unknown_pivot.loc[call]
                    line = f"  {call:<21}"
                    for band in bands: line += f"{row.get(band, 0):>7}"
                    line += f"{row.get('Total', 0):>7}"
                    report_lines.append(line)
        
        # --- Add Diagnostic List for Unknown Calls ---
        if unique_unknown_calls:
            report_lines.append("\n" + "-" * 30)
            report_lines.append(f"Callsigns with unknown {first_col_header}:")
            report_lines.append("-" * 30)
            
            col_width = 12
            num_cols = max(1, len(header) // (col_width + 2))
            
            for i in range(0, len(unique_unknown_calls), num_cols):
                line_calls = unique_unknown_calls[i:i+num_cols]
                report_lines.append("  ".join([f"{call:<{col_width}}" for call in line_calls]))

        # --- Save the Report File ---
        report_content = "\n".join(report_lines)
        os.makedirs(output_path, exist_ok=True)
        
        filename_calls = '_vs_'.join(sorted(all_calls))
        filename = f"{self.report_id}_{mult_name.lower()}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"
