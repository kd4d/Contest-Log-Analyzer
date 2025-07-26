# Contest Log Analyzer/contest_tools/reports/text_continent_summary.py
#
# Purpose: A text report that generates a summary of QSOs per continent,
#          broken down by band for multiple logs.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-26
# Version: 0.16.0-Beta
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
    Generates a summary of QSOs per continent, broken down by band.
    """
    @property
    def report_id(self) -> str:
        return "continent_summary"

    @property
    def report_name(self) -> str:
        return "Continent QSO Summary"

    @property
    def report_type(self) -> str:
        return "text"

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

        # Map the continent codes to full names for the report
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
        
        report_lines = ["------------------- C o n t i n e n t   S u m m a r y -----------------"]
        report_lines.append(header)
        report_lines.append(separator)

        for cont_name in continent_map.values():
            if cont_name in pivot.index.get_level_values('ContinentName'):
                report_lines.append(cont_name)
                continent_data = pivot.loc[cont_name]
                for call in all_calls:
                    if call in continent_data.index:
                        row = continent_data.loc[call]
                        line = f"        {call:<8}:"
                        for band in bands:
                            line += f"{row.get(band, 0):>7}"
                        line += f"{row.get('Total', 0):>7}"
                        report_lines.append(line)

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
        filename = f"{self.report_id}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"
