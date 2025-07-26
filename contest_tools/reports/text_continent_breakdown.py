# Contest Log Analyzer/contest_tools/reports/text_continent_breakdown.py
#
# Purpose: A text report that generates a per-band summary of QSOs per
#          continent, with a breakdown by Run/S&P/Unknown status.
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
# - Initial release of the Continent QSO Breakdown report.

from typing import List
import pandas as pd
import os
from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a per-band summary of QSOs per continent with a Run/S&P/Unknown breakdown.
    """
    @property
    def report_id(self) -> str:
        return "continent_breakdown"

    @property
    def report_name(self) -> str:
        return "Continent QSO Breakdown"

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
        continents = ['North America', 'South America', 'Europe', 'Asia', 'Africa', 'Oceania', 'Unknown']
        bands = ['160M', '80M', '40M', '20M', '15M', '10M']
        all_calls = sorted(combined_df['MyCall'].unique())
        created_files = []

        for band in bands:
            band_df = combined_df[combined_df['Band'] == band]
            if band_df.empty:
                continue

            report_lines = []
            
            # --- Header ---
            header = f"{'Continent':<14}" + "".join([f"{call:>12}" for call in all_calls])
            separator = "-" * len(header)
            report_lines.append(f"--- {band.replace('M','')} Meters Continent Breakdown ---")
            report_lines.append(header)
            report_lines.append(separator)

            # --- Pivot and Format ---
            pivot = band_df.pivot_table(
                index=['Continent', 'MyCall'],
                columns='Run',
                aggfunc='size',
                fill_value=0
            )

            for continent in continents:
                if continent in pivot.index.get_level_values('Continent'):
                    report_lines.append(continent)
                    continent_data = pivot.loc[continent]
                    
                    for run_status in ['Run', 'S&P', 'Unknown']:
                        line = f"  {run_status:<11}:"
                        for call in all_calls:
                            if call in continent_data.index:
                                line += f"{continent_data.loc[call].get(run_status, 0):>12}"
                            else:
                                line += f"{0:>12}"
                        report_lines.append(line)
            
            # --- Save Individual Report File ---
            report_content = "\n".join(report_lines)
            
            band_output_path = os.path.join(output_path, band)
            os.makedirs(band_output_path, exist_ok=True)
            
            filename_calls = '_vs_'.join(sorted(all_calls))
            filename = f"{self.report_id}_{band.lower()}_{filename_calls}.txt"
            filepath = os.path.join(band_output_path, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            created_files.append(filepath)

        if not created_files:
            return "No per-band continent breakdown reports were generated."

        return f"Continent breakdown reports saved to:\n" + "\n".join([f"  - {fp}" for fp in created_files])
