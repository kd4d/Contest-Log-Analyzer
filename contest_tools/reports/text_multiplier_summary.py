# contest_tools/reports/text_multiplier_summary.py
#
# Purpose: A data-driven text report that generates a summary of QSOs for a
#          specific multiplier type (e.g., Countries, Zones).
#
# Author: Gemini AI
# Date: 2025-11-23
# Version: 0.93.1
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
# [0.93.1] - 2025-11-23
# - Refactored to use MultiplierStatsAggregator for data processing.
# [0.93.0-Beta] - 2025-11-23
# - Added logic to preserve "Prefixes" as a plural header.
# [0.90.0-Beta] - 2025-10-01
# Set new baseline version for release.
from typing import List
import pandas as pd
import os
import json
import logging
import hashlib
from ..contest_log import ContestLog
from ..data_aggregators.multiplier_stats import MultiplierStatsAggregator
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
        
        # --- Use Aggregator for Data Calculation ---
        aggregator = MultiplierStatsAggregator(self.logs)
        result = aggregator.get_summary_data(mult_name, mode_filter)
        
        if 'error' in result:
            return result['error']
            
        pivot = result['pivot']
        all_calls = result['all_calls']
        mult_column = result['mult_column']
        mult_rule = result['mult_rule']
        combined_df = result['combined_df']
        main_df = result['main_df']
        contest_def = self.logs[0].contest_definition
        name_column = mult_rule.get('name_column')

        if pivot.empty and combined_df.empty:
             mode_str = f" on mode '{mode_filter}'" if mode_filter else ""
             return f"Report '{self.report_name}' for '{mult_name}'{mode_str} skipped as no data was found."
        
        if kwargs.get('debug_mults'):
            callsign = all_calls[0] if len(all_calls) == 1 else '_vs_'.join(all_calls)
            debug_csv_filename = f"multiplier_summary_sourcedata_debug_{callsign}.csv"
            debug_csv_filepath = os.path.join(output_path, debug_csv_filename)
            main_df.to_csv(debug_csv_filepath, index=False)
        
        bands = contest_def.valid_bands
        is_single_band = len(bands) == 1
        is_comparative = len(all_calls) > 1
        
        # --- Report Header Setup ---
        first_row_date = combined_df['Date'].iloc[0] if not combined_df.empty else "----"
        year = first_row_date.split('-')[0]
        mode_title_str = f" ({mode_filter})" if mode_filter else ""
        title1 = f"--- {self.report_name}: {mult_name}{mode_title_str} ---"
        title2 = f"{year} {contest_def.contest_name} - {', '.join(all_calls)}"
        report_lines = []

        # --- Gracefully handle cases with no multipliers ---
        if pivot.empty:
            report_lines.append(title1)
            report_lines.append(title2)
            report_lines.append(f"\nNo '{mult_name}' multipliers found to summarize.")
            # --- Save the clean (but empty) report and exit ---
            report_content = "\n".join(report_lines) + "\n"
            os.makedirs(output_path, exist_ok=True)
            filename_calls = '_vs_'.join(sorted(all_calls))
        
            mode_suffix = f"_{mode_filter.lower()}" if mode_filter else ""
            filename = f"{self.report_id}_{mult_name.lower()}{mode_suffix}_{filename_calls}.txt"
            filepath = os.path.join(output_path, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            return f"Text report saved to: {filepath}"
         
        name_map = {}
        if name_column and name_column in main_df.columns:
            name_map_df = main_df[[mult_column, name_column]].dropna().drop_duplicates()
            name_map = name_map_df.set_index(mult_column)[name_column].to_dict()

        for band in bands:
            if band not in pivot.columns: pivot[band] = 0
        pivot = pivot[bands]
         
        if not is_single_band:
            pivot['Total'] = pivot.sum(axis=1)

        if mult_name.lower() == 'countries':
            source_type = mult_rule.get('source', 'dxcc').upper()
            first_col_header = source_type
        elif mult_name.lower() == 'prefixes':
            first_col_header = mult_name
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
                if is_comparative:
                    if call in mult_data.index:
                        row = mult_data.loc[call]
                    else:
                        continue
                else:
                    row = mult_data

                line = f"  {call}:".ljust(first_col_width)
                for band in bands: line += f"{row.get(band, 0):>7}"
                if not is_single_band:
                    line += f"{row.get('Total', 0):>7}"
                report_lines.append(line)

        report_lines.append(separator)
        report_lines.append(f"{'Total':<{first_col_width}}")
        
        if is_comparative:
            total_pivot = pivot.groupby(level='MyCall').sum()
        else:
            total_pivot = pivot.sum().to_frame().T
            total_pivot['MyCall'] = all_calls[0]
            total_pivot = total_pivot.set_index('MyCall')

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

        # --- Diagnostic Section for "Unassigned" Multipliers ---
        df_to_check = combined_df
        if getattr(contest_def, 'is_naqp_ruleset', False):
            df_to_check = combined_df[(combined_df['Continent'] == 'NA') | (combined_df['DXCCPfx'] == 'KH6')]

        unassigned_df = df_to_check[df_to_check[mult_column].isna()]
        
        # Filter out intentional blanks for mutually exclusive mults
        exclusive_groups = contest_def.mutually_exclusive_mults
        for group in exclusive_groups:
            if mult_column in group:
                partner_cols = [p for p in group if p != mult_column and p in combined_df.columns]
                if partner_cols:
                    indices_to_check = unassigned_df.index
                    partner_values_exist = combined_df.loc[indices_to_check, partner_cols].notna().any(axis=1)
                    unassigned_df = unassigned_df.loc[~partner_values_exist]
        
        unique_unassigned_calls = sorted(unassigned_df['Call'].unique())
        
        if unique_unassigned_calls:
            report_lines.append("\n" + "-" * 30)
            report_lines.append(f"Callsigns with unassigned {first_col_header}:")
            report_lines.append("-" * 30)
            
            col_width = 12
            num_cols = max(1, table_width // (col_width + 2))
            
            for i in range(0, len(unique_unassigned_calls), num_cols):
                line_calls = unique_unassigned_calls[i:i+5]
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