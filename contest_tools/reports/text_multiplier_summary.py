# Contest Log Analyzer/contest_tools/reports/text_multiplier_summary.py
#
# Purpose: A data-driven text report that generates a summary of QSOs for a
#          specific multiplier type (e.g., Countries, Zones).
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-06
# Version: 0.30.36-Beta
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
## [0.30.36-Beta] - 2025-08-06
### Changed
# - Aligned formatting with Missed Multipliers report.
# - First column header is now dynamically set based on the multiplier rule.
# - First column width is now calculated dynamically to fit the content.
## [0.26.5-Beta] - 2025-08-04
### Fixed
# - Corrected a bug that caused the report to fail for single logs by
#   enabling single-log support and adding the correct processing logic.
from typing import List
import pandas as pd
import os
from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a summary of QSOs per multiplier, broken down by band.
    """
    report_id: str = "multiplier_summary"
    report_name: str = "Multiplier Summary"
    report_type: str = "text"
    supports_single = True
    supports_multi = True
    supports_pairwise = True
    
    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content.
        """
        mult_name = kwargs.get('mult_name')
        if not mult_name:
            return f"Error: 'mult_name' argument is required for the '{self.report_name}' report."

        # --- Single-Log Mode ---
        if len(self.logs) == 1:
            log = self.logs[0]
            df = log.get_processed_data()[log.get_processed_data()['Dupe'] == False]
            all_calls = [log.get_metadata().get('MyCall', 'Unknown')]
            return self._generate_report_for_logs(
                dfs=[df],
                all_calls=all_calls,
                mult_name=mult_name,
                output_path=output_path,
                contest_def=log.contest_definition
            )
        
        # --- Multi-Log (Comparative) Mode ---
        else:
            all_dfs = []
            all_calls = []
            for log in self.logs:
                df = log.get_processed_data()[log.get_processed_data()['Dupe'] == False].copy()
                df['MyCall'] = log.get_metadata().get('MyCall', 'Unknown')
                all_calls.append(df['MyCall'].iloc[0])
                all_dfs.append(df)

            return self._generate_report_for_logs(
                dfs=all_dfs,
                all_calls=sorted(all_calls),
                mult_name=mult_name,
                output_path=output_path,
                contest_def=self.logs[0].contest_definition
            )

    def _generate_report_for_logs(self, dfs, all_calls, mult_name, output_path, contest_def):
        mult_rule = next((r for r in contest_def.multiplier_rules if r.get('name', '').lower() == mult_name.lower()), None)
        if not mult_rule or 'value_column' not in mult_rule:
            return f"Error: Multiplier type '{mult_name}' not found in definition."

        mult_column = mult_rule['value_column']
        name_column = mult_rule.get('name_column')
        
        combined_df = pd.concat(dfs, ignore_index=True)
        if combined_df.empty or mult_column not in combined_df.columns:
            return f"No '{mult_name}' multiplier data to report."
        
        combined_df.dropna(subset=[mult_column], inplace=True)
        
        unknown_df = combined_df[combined_df[mult_column].isna()]
        w_ve_unknown_df = unknown_df[unknown_df['DXCCName'].isin(['United States', 'Canada'])]
        unique_unknown_calls = sorted(w_ve_unknown_df['Call'].unique())
        
        main_df = combined_df[combined_df[mult_column].notna()]
        
        bands = contest_def.valid_bands
        is_single_band = len(bands) == 1
        
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
        
        if not is_single_band:
            pivot['Total'] = pivot.sum(axis=1)

        # --- Dynamic First Column Header & Width ---
        if mult_name.lower() == 'countries':
            source_type = mult_rule.get('source', 'dxcc').upper()
            first_col_header = source_type
        else:
            first_col_header = mult_name[:-1] if mult_name.lower().endswith('s') else mult_name
        
        sorted_mults = sorted(pivot.index.get_level_values(0).unique())
        max_len = len(first_col_header)
        for mult in sorted_mults:
            if name_column:
                full_name = name_map.get(mult, '')
                display_string = f"{mult} ({full_name})" if pd.notna(full_name) and full_name != '' else str(mult)
                max_len = max(max_len, len(display_string))
            else:
                max_len = max(max_len, len(str(mult)))
        first_col_width = max_len
            
        header_parts = [f"{b.replace('M',''):>7}" for b in bands]
        if not is_single_band:
            header_parts.append(f"{'Total':>7}")
        table_header = f"{first_col_header:<{first_col_width}}" + "".join(header_parts)
        table_width = len(table_header)
        separator = "-" * table_width
        
        year = dfs[0]['Date'].iloc[0].split('-')[0] if not dfs[0].empty else "----"
        
        title1 = f"--- {self.report_name}: {mult_name} ---"
        title2 = f"{year} {contest_def.contest_name} - {', '.join(all_calls)}"
        
        report_lines = []
        header_width = max(table_width, len(title1), len(title2))
        if len(title1) > table_width or len(title2) > table_width:
             report_lines.append(f"{title1.ljust(header_width)}")
             report_lines.append(f"{title2.center(header_width)}")
        else:
             report_lines.append(title1.center(header_width))
             report_lines.append(title2.center(header_width))
        report_lines.append("")
        report_lines.append(table_header)
        report_lines.append(separator)

        for mult in sorted_mults:
            mult_display = str(mult)
            if name_column:
                mult_full_name = name_map.get(mult, '')
                if pd.notna(mult_full_name) and mult_full_name != '': 
                    clean_name = str(mult_full_name).split(';')[0].strip()
                    mult_display = f"{mult} ({clean_name})"

            report_lines.append(f"{mult_display:<{first_col_width}}")
            
            mult_data = pivot.loc[mult]
            for call in all_calls:
                if call in mult_data.index:
                    row = mult_data.loc[call]
                    line = f"  {'':<{first_col_width-2}}"
                    for band in bands: line += f"{row.get(band, 0):>7}"
                    if not is_single_band:
                        line += f"{row.get('Total', 0):>7}"
                    report_lines.append(line)

        report_lines.append(separator)
        report_lines.append(f"{'Total':<{first_col_width}}")
        
        total_pivot = pivot.groupby(level='MyCall').sum()
        for call in all_calls:
                if call in total_pivot.index:
                    row = total_pivot.loc[call]
                    line = f"  {'':<{first_col_width-2}}"
                    for band in bands: line += f"{row.get(band, 0):>7}"
                    if not is_single_band:
                        line += f"{row.get('Total', 0):>7}"
                    report_lines.append(line)

        if not unknown_df.empty:
            report_lines.append(f"{'Unknown Total':<{first_col_width}}")
            unknown_pivot = unknown_df.pivot_table(index='MyCall', columns='Band', aggfunc='size', fill_value=0)
            for band in bands:
                if band not in unknown_pivot.columns: unknown_pivot[band] = 0
            unknown_pivot = unknown_pivot[bands]
            
            if not is_single_band:
                unknown_pivot['Total'] = unknown_pivot.sum(axis=1)

            for call in all_calls:
                if call in unknown_pivot.index:
                    row = unknown_pivot.loc[call]
                    line = f"  {'':<{first_col_width-2}}"
                    for band in bands: line += f"{row.get(band, 0):>7}"
                    if not is_single_band:
                        line += f"{row.get('Total', 0):>7}"
                    report_lines.append(line)
        
        if unique_unknown_calls:
            report_lines.append("\n" + "-" * 30)
            report_lines.append(f"Callsigns with unknown {first_col_header}:")
            report_lines.append("-" * 30)
            
            col_width = 12
            num_cols = max(1, table_width // (col_width + 2))
            
            for i in range(0, len(unique_unknown_calls), num_cols):
                line_calls = unique_unknown_calls[i:i+num_cols]
                report_lines.append("  ".join([f"{call:<{col_width}}" for call in line_calls]))

        report_content = "\n".join(report_lines)
        os.makedirs(output_path, exist_ok=True)
        
        filename_calls = '_vs_'.join(sorted(all_calls))
        filename = f"{self.report_id}_{mult_name.lower()}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"