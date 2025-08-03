# Contest Log Analyzer/contest_tools/reports/text_comparative_continent_summary.py
#
# Purpose: A text report that generates a comparative summary of QSOs per
#          continent, broken down by band for multiple logs.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-03
# Version: 0.28.15-Beta
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
## [0.28.15-Beta] - 2025-08-03
### Added
# - Added new diagnostic sections to the end of the report for callsigns
#   with Unknown DXCC and WPX prefixes.
#
## [0.26.1-Beta] - 2025-08-02
### Fixed
# - Converted report_id, report_name, and report_type from @property methods
#   to simple class attributes to fix a bug in the report generation loop.
## [0.22.2-Beta] - 2025-07-31
### Changed
# - Implemented the boolean support properties, correctly identifying this
#   report as 'multi' mode.
## [0.22.1-Beta] - 2025-07-30
### Changed
# - Added a blank line between each continent's data block to improve
#   readability.
## [0.22.0-Beta] - 2025-07-30
# - Initial release of the Comparative Continent Summary report.
from typing import List
import pandas as pd
import os
from ..contest_log import ContestLog
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
        continent_map = {
            'NA': 'North America', 'SA': 'South America', 'EU': 'Europe',
            'AS': 'Asia', 'AF': 'Africa', 'OC': 'Oceania', 'Unknown': 'Unknown'
        }
        bands = ['160M', '80M', '40M', '20M', '15M', '10M']
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
        pivot['Total'] = pivot.sum(axis=1)

        # --- Formatting ---
        header = f"{'':<17}" + "".join([f"{b.replace('M',''):>7}" for b in bands]) + f"{'Total':>7}"
        separator = "-" * len(header)
        
        report_lines = [f"--- {self.report_name} ---".center(len(header))]
        report_lines.append(header)
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
        total_pivot['Total'] = total_pivot.sum(axis=1)

        for call in all_calls:
                if call in total_pivot.index:
                    row = total_pivot.loc[call]
                    line = f"  {call:<15}"
                    for band in bands:
                        line += f"{row.get(band, 0):>7}"
                    line += f"{row.get('Total', 0):>7}"
                    report_lines.append(line)
        
        # --- Diagnostic Sections ---
        self._add_diagnostic_sections(report_lines)

        # --- Save the Report File ---
        report_content = "\n".join(report_lines)
        os.makedirs(output_path, exist_ok=True)
        
        filename_calls = '_vs_'.join(sorted(all_calls))
        filename = f"{self.report_id}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"

    def _add_diagnostic_sections(self, report_lines: List[str]):
        """Appends sections for Unknown DXCC and WPX prefixes to the report."""
        unknown_dxcc_calls = set()
        unknown_wpx_calls = set()

        # Consolidate data from all logs for this specific report instance
        for log in self.logs:
            df = log.get_processed_data()
            unknown_dxcc_df = df[df['DXCCPfx'] == 'Unknown']
            unknown_dxcc_calls.update(unknown_dxcc_df['Call'].unique())

            if 'Mult1' in df.columns:
                unknown_wpx_df = df[df['Mult1'] == 'Unknown']
                unknown_wpx_calls.update(unknown_wpx_df['Call'].unique())

        if unknown_dxcc_calls:
            report_lines.append("\n" + "-" * 40)
            report_lines.append("Callsigns with Unknown DXCC Prefix:")
            report_lines.append("-" * 40)
            col_width = 12
            sorted_calls = sorted(list(unknown_dxcc_calls))
            # Format into neat columns
            for i in range(0, len(sorted_calls), 5):
                line_calls = sorted_calls[i:i+5]
                report_lines.append("  ".join([f"{call:<{col_width}}" for call in line_calls]))

        if unknown_wpx_calls:
            report_lines.append("\n" + "-" * 40)
            report_lines.append("Callsigns with Unknown WPX Prefix (Mult1):")
            report_lines.append("-" * 40)
            col_width = 12
            sorted_calls = sorted(list(unknown_wpx_calls))
            for i in range(0, len(sorted_calls), 5):
                line_calls = sorted_calls[i:i+5]
                report_lines.append("  ".join([f"{call:<{col_width}}" for call in line_calls]))