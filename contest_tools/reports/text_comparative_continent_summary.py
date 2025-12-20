# contest_tools/reports/text_comparative_continent_summary.py
#
# Purpose: A text report that generates a comparative summary of QSOs per
#          continent, broken down by band for multiple logs.
#
# Author: Gemini AI
# Date: 2025-12-14
# Version: 0.134.1-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0.
# If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# --- Revision History ---
# [0.134.1-Beta] - 2025-12-20
# - Added standard report header generation using `format_text_header`.
# [0.113.0-Beta] - 2025-12-13
# - Standardized filename generation: removed '_vs_' separator to match Web Dashboard conventions.
# [0.90.1-Beta] - 2025-12-14
# - Updated file generation to use `_sanitize_filename_part` for strict lowercase naming.
# [0.90.0-Beta] - 2025-10-01
# - Set new baseline version for release.
from typing import List
import pandas as pd
import os
from ..contest_log import ContestLog
from ..contest_definitions import ContestDefinition
from .report_interface import ContestReport
from ._report_utils import _sanitize_filename_part, format_text_header, get_cty_metadata, get_standard_title_lines

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
        
        # --- Standard Header ---
        modes_present = set()
        for log in self.logs:
            df = log.get_processed_data()
            if 'Mode' in df.columns:
                modes_present.update(df['Mode'].dropna().unique())

        title_lines = get_standard_title_lines(self.report_name, self.logs, "All Bands", None, modes_present)
        meta_lines = ["Contest Log Analytics by KD4D", get_cty_metadata(self.logs)]
        
        header_block = format_text_header(table_width, title_lines, meta_lines)
        report_lines = header_block + [""]

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
        
        filename_calls = '_'.join([_sanitize_filename_part(c) for c in sorted(all_calls)])
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