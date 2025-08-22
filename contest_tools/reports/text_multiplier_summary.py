# Contest Log Analyzer/contest_tools/reports/text_multiplier_summary.py
#
# Purpose: A data-driven text report that generates a summary of QSOs for a
#          specific multiplier type (e.g., Countries, Zones).
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-21
# Version: 0.39.0-Beta
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
## [0.39.0-Beta] - 2025-08-21
### Fixed
# - Added logic to correctly apply the 'mults_from_zero_point_qsos'
#   contest rule, ensuring consistency with other reports.
## [0.38.0-Beta] - 2025-08-21
### Fixed
# - Added a filter to exclude "Unknown" multipliers from the report,
#   ensuring its counting logic is consistent with the score_report.
## [0.37.1-Beta] - 2025-08-16
### Fixed
# - Corrected file writing logic to append a final newline character,
#   ensuring compatibility with diff utilities.
## [0.32.9-Beta] - 2025-08-12
### Fixed
# - Refactored the generate method to work on copies of the data, preventing
#   the permanent modification of the original ContestLog objects and fixing
#   the data corruption bug for per-mode reports.
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
        mode_filter = kwargs.get('mode_filter')

        if not mult_name:
            return f"Error: 'mult_name' argument is required for the '{self.report_name}' report."
        # --- Create a list of filtered dataframes to process ---
        # This approach avoids modifying the original ContestLog objects.
        log_data_to_process = []
        for log in self.logs:
            df = log.get_processed_data()
            if mode_filter:
                filtered_df = df[df['Mode'] == mode_filter].copy()
            else:
                filtered_df = df.copy()
            log_data_to_process.append({'df': filtered_df, 'meta': log.get_metadata()})

        # --- Single-Log Mode ---
        if len(log_data_to_process) == 1:
            log_data = log_data_to_process[0]
            df = log_data['df'][log_data['df']['Dupe'] == False]
            all_calls = [log_data['meta'].get('MyCall', 'Unknown')]
            return self._generate_report_for_logs(
                dfs=[df],
                all_calls=all_calls,
                mult_name=mult_name,
                mode_filter=mode_filter,
                output_path=output_path,
                contest_def=self.logs[0].contest_definition
            )
        
        # --- Multi-Log (Comparative) Mode ---
        else:
            all_dfs = []
            all_calls = []
            for log_data in log_data_to_process:
                df = log_data['df'][log_data['df']['Dupe'] == False].copy()
                if not df.empty:
                    my_call = log_data['meta'].get('MyCall', 'Unknown')
                    df['MyCall'] = my_call
                    all_calls.append(my_call)
                    all_dfs.append(df)

            return self._generate_report_for_logs(
                dfs=all_dfs,
                all_calls=sorted(all_calls),
                mult_name=mult_name,
                mode_filter=mode_filter,
                output_path=output_path,
                contest_def=self.logs[0].contest_definition
            )

    def _generate_report_for_logs(self, dfs, all_calls, mult_name, mode_filter, output_path, contest_def):
        if not dfs:
            mode_str = f" on mode '{mode_filter}'" if mode_filter else ""
            return f"Report '{self.report_name}' for '{mult_name}'{mode_str} skipped as no data was found."
        mult_rule = next((r for r in contest_def.multiplier_rules if r.get('name', '').lower() == mult_name.lower()), None)
        if not mult_rule or 'value_column' not in mult_rule:
            return f"Error: Multiplier type '{mult_name}' not found in definition."
        mult_column = mult_rule['value_column']
        name_column = mult_rule.get('name_column')
        
        combined_df = pd.concat(dfs, ignore_index=True)
        if combined_df.empty or mult_column not in combined_df.columns:
            return f"No '{mult_name}' multiplier data to report for mode '{mode_filter}'."
            
        main_df = combined_df[combined_df[mult_column].notna()]
        main_df = main_df[main_df[mult_column] != 'Unknown']

        # --- Apply contest rule for multipliers from zero-point QSOs ---
        if not contest_def.mults_from_zero_point_qsos:
            main_df = main_df[main_df['QSOPoints'] > 0]
        
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
        
        max_mult_len = len(first_col_header)
        if sorted_mults:
            for mult in sorted_mults:
                if name_column:
                    full_name = name_map.get(mult, '')
                    display_string = f"{mult} ({full_name})" if pd.notna(full_name) and full_name != '' else str(mult)
                    max_mult_len = max(max_mult_len, len(display_string))
                else:
                    max_mult_len = max(max_mult_len, len(str(mult)))
        
        max_call_len = 0
        if len(all_calls) > 1:
            max_call_len = max(len(f"  {call}: ") for call in all_calls)

        first_col_width = max(max_mult_len, max_call_len)
        
        header_parts = [f"{b.replace('M',''):>7}" for b in bands]
        if not is_single_band:
            header_parts.append(f"{'Total':>7}")
        table_header = f"{first_col_header:<{first_col_width}}" + "".join(header_parts)
        table_width = len(table_header)
        separator = "-" * table_width
        
        year = dfs[0]['Date'].iloc[0].split('-')[0] if not dfs[0].empty else "----"
        
        mode_title_str = f" ({mode_filter})" if mode_filter else ""
        title1 = f"--- {self.report_name}: {mult_name}{mode_title_str} ---"
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
                    line = f"  {call}:".ljust(first_col_width)
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
                line = f"  {call}:".ljust(first_col_width)
                for band in bands: line += f"{row.get(band, 0):>7}"
                if not is_single_band:
                    line += f"{row.get('Total', 0):>7}"
                report_lines.append(line)

        # --- Diagnostic Section for "Unknown" Multipliers ---
        unknown_df = combined_df[combined_df[mult_column] == 'Unknown']
        unique_unknown_calls = sorted(unknown_df['Call'].unique())
        
        if unique_unknown_calls:
            report_lines.append("\n" + "-" * 30)
            report_lines.append(f"Callsigns with unknown {first_col_header}:")
            report_lines.append("-" * 30)
            
            col_width = 12
            num_cols = max(1, table_width // (col_width + 2))
            
            for i in range(0, len(unique_unknown_calls), num_cols):
                line_calls = unique_unknown_calls[i:i+5]
                report_lines.append("  ".join([f"{call:<{col_width}}" for call in line_calls]))

        report_content = "\n".join(report_lines) + "\n"
        os.makedirs(output_path, exist_ok=True)
        
        filename_calls = '_vs_'.join(sorted(all_calls))
        mode_suffix = f"_{mode_filter.lower()}" if mode_filter else ""
        filename = f"{self.report_id}_{mult_name.lower()}{mode_suffix}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"