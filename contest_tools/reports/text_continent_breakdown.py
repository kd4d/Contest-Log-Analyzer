# contest_tools/reports/text_continent_breakdown.py
#
# Purpose: A text report that generates a per-band summary of QSOs per
#          continent, with a breakdown by Run/S&P/Unknown status.
#
# Author: Gemini AI
# Date: 2025-10-01
# Version: 0.90.0-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# --- Revision History ---
# [0.90.0-Beta] - 2025-10-01
# Set new baseline version for release.

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
            report_lines = []

            # --- Grid Formatting Logic ---
            formatted_data = {}
            table_width = 0
            
            if not pivot.empty:
                continents_with_data = sorted(pivot.index.get_level_values('ContinentName').unique())
                for cont_name in continents_with_data:
                    continent_lines = []
                    continent_data = pivot.loc[cont_name]
                    for band in bands:
                        if band in continent_data.index:
                            band_data = continent_data.loc[band]
                            continent_lines.append(f"  {band.replace('M','')} Meters:")
                            for run_status in ['Run', 'S&P', 'Unknown']:
                                line = f"    {run_status:<9}: {band_data.get(run_status, 0):>8}"
                                continent_lines.append(line)
                    
                    if not continent_data.empty:
                        continent_totals = continent_data.sum()
                        total_qsos_for_continent = continent_totals.sum()
                        continent_lines.append(f"    {'-'*9}: {'-'*8}")
                        for run_status in ['Run', 'S&P', 'Unknown']:
                            line = f"    {run_status:<9}: {continent_totals.get(run_status, 0):>8}"
                            continent_lines.append(line)
                        continent_lines.append(f"    {'Total':<9}: {total_qsos_for_continent:>8}")

                    formatted_data[cont_name] = continent_lines
                
                # Dynamically build the grid layout
                grid_layout = []
                max_cols = 3
                for i in range(0, len(continents_with_data), max_cols):
                    grid_layout.append(continents_with_data[i:i+max_cols])

                # Recalculate table width based on dynamic grid
                if grid_layout:
                    table_width = col_width * len(grid_layout[0])
                
                # --- THIS BLOCK MOVED TO AFTER WIDTH CALCULATION ---
                title1 = f"--- {self.report_name} ---"
                title2 = f"{year} {contest_name} - {callsign}"
                header_width = max(table_width, len(title1), len(title2))
                
                if len(title1) > table_width or len(title2) > table_width:
                    report_lines.insert(0, f"{title2.center(header_width)}")
                    report_lines.insert(0, f"{title1.ljust(header_width)}")
                else:
                    report_lines.insert(0, f"{title2.center(header_width)}")
                    report_lines.insert(0, title1.center(header_width))
                report_lines.insert(2, "")
                # --- END MOVED BLOCK ---

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

            # --- Add Overall Totals Section ---
            if not pivot.empty:
                report_lines.append("\n" + "=" * table_width)
                report_lines.append("Overall Totals".center(table_width))
                report_lines.append("=" * table_width)
                grand_totals = pivot.sum()
                grand_total_qsos = grand_totals.sum()

                col1_width = 35 // 2
                col2_width = 35 // 2

                run_line = f"{'Run:':<{col1_width}}{grand_totals.get('Run', 0):>{col2_width}}"
                sp_line = f"{'S&P:':<{col1_width}}{grand_totals.get('S&P', 0):>{col2_width}}"
                unk_line = f"{'Unknown:':<{col1_width}}{grand_totals.get('Unknown', 0):>{col2_width}}"
                sep_line = f"{'-------':<{col1_width}}{'-------':>{col2_width}}"
                total_line = f"{'Total:':<{col1_width}}{grand_total_qsos:>{col2_width}}"

                report_lines.append(run_line.center(table_width))
                report_lines.append(sp_line.center(table_width))
                report_lines.append(unk_line.center(table_width))
                report_lines.append(sep_line.center(table_width))
                report_lines.append(total_line.center(table_width))

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
            report_content = "\n".join(report_lines) + "\n"
            os.makedirs(output_path, exist_ok=True)
            filename = f"{self.report_id}_{callsign}.txt"
            filepath = os.path.join(output_path, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            final_report_messages.append(f"Text report saved to: {filepath}")

        if not final_report_messages:
            return "No continent breakdown reports were generated."
        return "\n".join(final_report_messages)
