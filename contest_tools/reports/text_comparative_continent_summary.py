# Contest Log Analyzer/contest_tools/reports/text_comparative_continent_summary.py
#
# Purpose: A text report that generates a comparative summary of QSOs per
#          continent, broken down by band for multiple logs.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-04
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
## [0.28.20-Beta] - 2025-08-04
### Changed
# - Reworked the header formatting logic to correctly handle titles that
#   are wider than the data table, per user specifications.
## [0.28.19-Beta] - 2025-08-04
### Fixed
# - Corrected the formatting to ensure the second title line is centered.
from typing import List
import pandas as pd
import os
from ..contest_log import ContestLog
from ..contest_definitions import ContestDefinition
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a comparative summary of QSOs per continent, broken down by band.
    """
    report_id: str = "comparative_continent_summary"
    report_name: str = "Comparative Continent QSO Summary"
    report_type: str = "text"
    supports_multi = True
    
    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content.
        """
        include_dupes = kwargs.get('include_dupes', False)
        
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
        
        if combined_df.empty:
            return "No valid QSOs to report."
        
        # --- Report Generation ---
        first_log = self.logs[0]
        contest_def = first_log.contest_definition
        
        continent_map = {
            'NA': 'North America', 'SA': 'South America', 'EU': 'Europe',
            'AS': 'Asia', 'AF': 'Africa', 'OC': 'Oceania', 'Unknown': 'Unknown'
        }
        bands = contest_def.valid_bands
        is_single_band = len(bands) == 1
        all_calls = sorted(combined_df['MyCall'].unique())

        combined_df['ContinentName'] = combined_df['Continent'].map(continent_map).fillna('Unknown')

        pivot = combined_df.pivot_table(
            index=['ContinentName', 'MyCall'],
            columns='Band',
            aggfunc='size',
            fill_value=0
        )

        for band in bands:
            if band not in pivot.columns:
                pivot[band] = 0
        pivot = pivot[bands]
        
        if not is_single_band:
            pivot['Total'] = pivot.sum(axis=1)

        # --- Formatting ---
        header_parts = [f"{b.replace('M',''):>7}" for b in bands]
        if not is_single_band:
            header_parts.append(f"{'Total':>7}")
        table_header = f"{'':<17}" + "".join(header_parts)
        table_width = len(table_header)
        separator = "-" * table_width
        
        contest_name = first_log.get_metadata().get('ContestName', 'UnknownContest')
        year = first_log.get_processed_data()['Date'].iloc[0].split('-')[0] if not first_log.get_processed_data().empty else "----"
        
        title1 = f"--- {self.report_name} ---"
        title2 = f"{year} {contest_name} - {', '.join(all_calls)}"
        
        title1_width = len(title1)
        title2_width = len(title2)

        if title1_width > table_width or title2_width > table_width:
            header_width = max(title1_width, title2_width)
            report_lines = [
                f"{title1.ljust(header_width)}",
                f"{title2.center(header_width)}",
                ""
            ]
        else:
            header_width = table_width
            report_lines = [
                title1.center(header_width),
                title2.center(header_width),
                ""
            ]

        report_lines.append(table_header)
        report_lines.append(separator)

        for cont_name in sorted(continent_map.values()):
            if cont_name in pivot.index.get_level_values('ContinentName'):
                report_lines.append(cont_name)
                continent_data = pivot.loc[cont_name]
                for call in all_calls:
                    if call in continent_data.index:
                        row = continent_data.loc[call]
                        line = f"  {call:<15}"
                        for band in bands:
                            line += f"{row.get(band, 0):>7}"
                        if not is_single_band:
                            line += f"{row.get('Total', 0):>7}"
                        report_lines.append(line)
                report_lines.append("")

        report_lines.append(separator)
        report_lines.append("Total")
        
        total_pivot = combined_df.pivot_table(index='MyCall', columns='Band', aggfunc='size', fill_value=0)
        for band in bands:
            if band not in total_pivot.columns:
                total_pivot[band] = 0
        total_pivot = total_pivot[bands]
        
        if not is_single_band:
            total_pivot['Total'] = total_pivot.sum(axis=1)

        for call in all_calls:
                if call in total_pivot.index:
                    row = total_pivot.loc[call]
                    line = f"  {call:<15}"
                    for band in bands:
                        line += f"{row.get(band, 0):>7}"
                    if not is_single_band:
                        line += f"{row.get('Total', 0):>7}"
                    report_lines.append(line)
        
        self._add_diagnostic_sections(report_lines, contest_def)

        # --- Save the Report File ---
        report_content = "\n".join(report_lines)
        os.makedirs(output_path, exist_ok=True)
        
        filename_calls = '_vs_'.join(sorted(all_calls))
        filename = f"{self.report_id}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"

    def _add_diagnostic_sections(self, report_lines: List[str], contest_def: ContestDefinition):
        """Appends sections for various unknown data points to the report."""
        
        combined_df = pd.concat([log.get_processed_data() for log in self.logs])
        if combined_df.empty:
            return

        # --- Check for Unknown DXCC Prefix ---
        unknown_dxcc_df = combined_df[combined_df['DXCCPfx'] == 'Unknown']
        unknown_dxcc_calls = sorted(list(unknown_dxcc_df['Call'].unique()))
        if unknown_dxcc_calls:
            report_lines.append("\n" + "-" * 40)
            report_lines.append("Callsigns with Unknown DXCC Prefix:")
            report_lines.append("-" * 40)
            col_width = 12
            for i in range(0, len(unknown_dxcc_calls), 5):
                line_calls = unknown_dxcc_calls[i:i+5]
                report_lines.append("  ".join([f"{call:<{col_width}}" for call in line_calls]))

        # --- Check for Unknown Continent ---
        unknown_continent_df = combined_df[combined_df['Continent'] == 'Unknown']
        unknown_continent_calls = sorted(list(unknown_continent_df['Call'].unique()))
        if unknown_continent_calls:
            report_lines.append("\n" + "-" * 40)
            report_lines.append("Callsigns with Unknown Continent:")
            report_lines.append("-" * 40)
            col_width = 12
            for i in range(0, len(unknown_continent_calls), 5):
                line_calls = unknown_continent_calls[i:i+5]
                report_lines.append("  ".join([f"{call:<{col_width}}" for call in line_calls]))

        # --- Context-Aware Check for Unknown Multipliers (WPX Only) ---
        if 'CQ-WPX' in contest_def.contest_name:
            rule = next((r for r in contest_def.multiplier_rules if r.get('name') == 'Prefixes'), None)
            if rule:
                col = rule.get('value_column')
                if col and col in combined_df.columns:
                    unknown_mult_df = combined_df[combined_df[col] == 'Unknown']
                    unknown_calls = sorted(list(unknown_mult_df['Call'].unique()))
                    
                    if unknown_calls:
                        report_lines.append("\n" + "-" * 40)
                        report_lines.append(f"Callsigns with Unknown {rule['name']} ({col}):")
                        report_lines.append("-" * 40)
                        col_width = 12
                        for i in range(0, len(unknown_calls), 5):
                            line_calls = unknown_calls[i:i+5]
                            report_lines.append("  ".join([f"{call:<{col_width}}" for call in line_calls]))