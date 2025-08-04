# Contest Log Analyzer/contest_tools/reports/text_continent_breakdown.py
#
# Purpose: A text report that generates a per-band summary of QSOs per
#          continent, with a breakdown by Run/S&P/Unknown status.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-04
# Version: 0.28.27-Beta
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
## [0.28.27-Beta] - 2025-08-04
### Changed
# - Standardized the report header to use a two-line title.
## [0.28.26-Beta] - 2025-08-03
### Changed
# - The report now uses the dynamic `valid_bands` list from the contest
#   definition instead of a hardcoded list.
from typing import List
import pandas as pd
import os
from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a per-band summary of QSOs per continent with a Run/S&P/Unknown breakdown.
    """
    report_id: str = "continent_breakdown"
    report_name: str = "Continent QSO Breakdown"
    report_type: str = "text"
    supports_single = True
    
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
            contest_name = metadata.get('ContestName', 'UnknownContest')
            year = df_full['Date'].iloc[0].split('-')[0] if not df_full.empty else "----"


            if not include_dupes and 'Dupe' in df_full.columns:
                df = df_full[df_full['Dupe'] == False].copy()
            else:
                df = df_full.copy()
            
            if df.empty:
                msg = f"Skipping report for {callsign}: No valid QSOs to report."
                print(msg)
                final_report_messages.append(msg)
                continue

            continent_map = {
                'NA': 'North America', 'SA': 'South America', 'EU': 'Europe',
                'AS': 'Asia', 'AF': 'Africa', 'OC': 'Oceania', 'Unknown': 'Unknown'
            }
            bands = log.contest_definition.valid_bands
            df['ContinentName'] = df['Continent'].map(continent_map).fillna('Unknown')

            pivot = df.pivot_table(
                index=['ContinentName', 'Band'],
                columns='Run',
                aggfunc='size',
                fill_value=0
            )

            col_width = 35
            table_width = col_width * 3
            subtitle = f"{year} {contest_name} - {callsign}"
            report_lines = []
            report_lines.append(f"--- {self.report_name} ---".center(table_width))
            report_lines.append(subtitle.center(table_width))
            report_lines.append("")

            # --- Grid Formatting Logic ---
            formatted_data = {}
            for cont_name in sorted(continent_map.values()):
                if cont_name in pivot.index.get_level_values('ContinentName'):
                    continent_lines = []
                    continent_data = pivot.loc[cont_name]
                    for band in bands:
                        if band in continent_data.index:
                            band_data = continent_data.loc[band]
                            continent_lines.append(f"  {band.replace('M','')} Meters:")
                            for run_status in ['Run', 'S&P', 'Unknown']:
                                line = f"    {run_status:<9}: {band_data.get(run_status, 0):>8}"
                                continent_lines.append(line)
                    formatted_data[cont_name] = continent_lines

            grid_layout = [
                ["North America", "South America", "Europe"],
                ["Asia", "Africa", "Oceania"]
            ]
            
            for grid_row in grid_layout:
                row_continent_data = [formatted_data.get(c, []) for c in grid_row]
                
                if not any(row_continent_data):
                    continue

                header_line = "".join([f"{name:^{col_width}}" for name in grid_row])
                separator = "".join([f"{'-' * (len(name)):^{col_width}}" for name in grid_row])
                report_lines.append("\n" + header_line)
                report_lines.append(separator)

                max_lines = max(len(d) for d in row_continent_data) if row_continent_data else 0
                for i in range(max_lines):
                    line_parts = []
                    for continent_data_block in row_continent_data:
                        line = continent_data_block[i] if i < len(continent_data_block) else ""
                        line_parts.append(f"{line:<{col_width}}")
                    report_lines.append("".join(line_parts))

            # --- Add Diagnostic List for Unknown Calls ---
            unknown_continent_df = df[df['ContinentName'] == 'Unknown']
            unique_unknown_calls = sorted(unknown_continent_df['Call'].unique())

            if unique_unknown_calls:
                report_lines.append("\n" + "-" * 40)
                report_lines.append("Callsigns with 'Unknown' Continent:")
                report_lines.append("-" * 40)
                
                num_cols = max(1, (col_width * 3) // 14)
            
                for i in range(0, len(unique_unknown_calls), num_cols):
                    line_calls = unique_unknown_calls[i:i+num_cols]
                    report_lines.append("  ".join([f"{call:<12}" for call in line_calls]))

            # --- Save the SINGLE Report File ---
            report_content = "\n".join(report_lines)
            os.makedirs(output_path, exist_ok=True)
            filename = f"{self.report_id}_{callsign}.txt"
            filepath = os.path.join(output_path, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            final_report_messages.append(f"Text report saved to: {filepath}")

        if not final_report_messages:
            return "No continent breakdown reports were generated."
        return "\n".join(final_report_messages)