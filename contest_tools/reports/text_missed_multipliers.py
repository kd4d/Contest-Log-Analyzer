# Contest Log Analyzer/contest_tools/reports/text_missed_multipliers.py
#
# Purpose: A data-driven text report that generates a comparative "missed multipliers"
#          summary for any multiplier type defined in a contest's JSON file.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-04
# Version: 0.26.4-Beta
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
## [0.26.4-Beta] - 2025-08-04
### Changed
# - Reworked the header formatting logic to correctly handle titles that
#   are wider than the data table.
### Fixed
# - The redundant 'All Bands Summary' is now omitted for single-band contests.
## [0.26.3-Beta] - 2025-08-04
### Changed
# - Standardized the report header to use a two-line title.
from typing import List, Dict, Any, Set
import pandas as pd
import numpy as np
import os
from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a comparative report showing a specific multiplier worked by each
    station on each band, highlighting missed opportunities.
    """
    report_id: str = "missed_multipliers"
    report_name: str = "Missed Multipliers Report"
    report_type: str = "text"
    supports_single = False
    supports_multi = True
    supports_pairwise = True
    
    def _get_run_sp_status(self, series: pd.Series) -> str:
        """Determines if a multiplier was worked via Run, S&P, Unknown, or a combination."""
        modes = set(series.unique())
        
        has_run = "Run" in modes
        has_sp = "S&P" in modes

        if has_run and has_sp:
            return "Both"
        elif has_run:
            return "Run"
        elif has_sp:
            return "S&P"
        elif "Unknown" in modes:
            return "Unk"
        return ""

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content.
        """
        mult_name = kwargs.get('mult_name')

        if not mult_name:
            return "Error: 'mult_name' argument is required for the Missed Multipliers report."

        first_log = self.logs[0]
        first_log_def = first_log.contest_definition
        mult_rule = None
        for rule in first_log_def.multiplier_rules:
            if rule.get('name', '').lower() == mult_name.lower():
                mult_rule = rule
                break
        
        if not mult_rule or 'value_column' not in mult_rule:
            return f"Error: Multiplier type '{mult_name}' not found in definition for {first_log_def.contest_name}."

        mult_column = mult_rule['value_column']
        name_column = mult_rule.get('name_column')
        report_scope = first_log_def.multiplier_report_scope

        all_calls = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in self.logs])
        
        col_width = 14
        if mult_name.lower() == 'zones':
            col_width = 11
        elif mult_name.lower() == 'countries':
            col_width = 12
        
        if mult_name.lower() == 'countries':
            first_col_header = 'Country'
        elif mult_name.lower() == 'prefixes':
            first_col_header = 'Prefix'
        else:
            first_col_header = mult_name[:-1] if mult_name.lower().endswith('s') else mult_name
            first_col_header = first_col_header.capitalize()
            
        first_col_width = 27 if name_column else 9

        metadata = first_log.get_metadata()
        contest_name = metadata.get('ContestName', 'UnknownContest')
        first_qso_date = first_log.get_processed_data()['Date'].iloc[0] if not first_log.get_processed_data().empty else "----"
        year = first_qso_date.split('-')[0]
        
        header_cells = [f"{call:^{col_width}}" for call in all_calls]
        table_header = f"{first_col_header:<{first_col_width}} | {' | '.join(header_cells)}"
        table_width = len(table_header)
        
        title1 = f"--- {self.report_name}: {mult_name} ---"
        title2 = f"{year} {contest_name} - {', '.join(all_calls)}"
        
        report_lines = []
        if len(title1) > table_width or len(title2) > table_width:
             header_width = max(len(title1), len(title2))
             report_lines.append(f"{title1.ljust(header_width)}")
             report_lines.append(f"{title2.center(header_width)}")
        else:
             header_width = table_width
             report_lines.append(title1.center(header_width))
             report_lines.append(title2.center(header_width))
        report_lines.append("")

        bands = first_log.contest_definition.valid_bands
        is_single_band = len(bands) == 1
        
        all_bands_worked_sum = {call: 0 for call in all_calls}
        all_bands_missed_sum = {call: 0 for call in all_calls}
        overall_prefix_to_name_map = {}
        all_unknown_calls = set()

        for log in self.logs:
            df_full = log.get_processed_data()
            df = df_full[df_full['Dupe'] == False].copy()
            if df.empty or mult_column not in df.columns:
                continue
            
            unknown_df = df[df[mult_column] == 'Unknown']
            w_ve_unknown_df = unknown_df[unknown_df['DXCCName'].isin(['United States', 'Canada'])]
            all_unknown_calls.update(w_ve_unknown_df['Call'].unique())
            
            if name_column and name_column in df.columns:
                name_map_df = df[[mult_column, name_column]].dropna().drop_duplicates()
                for _, row in name_map_df.iterrows():
                    overall_prefix_to_name_map[row[mult_column]] = row[name_column]

        if report_scope == 'per_band':
            for band in bands:
                band_header_text = f"{band.replace('M', '')} Meters Missed Multipliers"
                report_lines.append(band_header_text.center(table_width))
                
                band_data: Dict[str, pd.DataFrame] = {}
                mult_sets: Dict[str, Set[str]] = {call: set() for call in all_calls}
                prefix_to_name_map = {}

                for log in self.logs:
                    callsign = log.get_metadata().get('MyCall', 'Unknown')
                    df_full = log.get_processed_data()
                    
                    df = df_full[df_full['Dupe'] == False].copy()
                    
                    if df.empty or mult_column not in df.columns:
                        continue
                    
                    df_band = df[df['Band'] == band].copy()
                    df_band = df_band[df_band[mult_column].notna()]
                    
                    if df_band.empty:
                        continue
                    
                    if name_column and name_column in df_band.columns:
                        name_map_df = df_band[[mult_column, name_column]].dropna().drop_duplicates()
                        for _, row in name_map_df.iterrows():
                            prefix_to_name_map[row[mult_column]] = row[name_column]

                    agg_data = df_band.groupby(mult_column).agg(
                        QSO_Count=('Call', 'size'),
                        Run_SP_Status=('Run', self._get_run_sp_status)
                    )
                    
                    band_data[callsign] = agg_data
                    mult_sets[callsign].update(agg_data.index)

                union_of_all_mults = set.union(*mult_sets.values())
                
                if not union_of_all_mults:
                    report_lines.append("     (No multipliers on this band for any log)".center(table_width))
                    report_lines.append("")
                    continue

                missed_mults_on_band = set()
                for call in all_calls:
                    missed_mults_on_band.update(union_of_all_mults.difference(mult_sets[call]))

                report_lines.append(table_header)

                if not missed_mults_on_band:
                    report_lines.append(f"     (No missed {mult_name} on this band)".center(table_width))
                else:
                    for mult in sorted(list(missed_mults_on_band)):
                        cell_parts = []
                        for call in all_calls:
                            if call in band_data and mult in band_data[call].index:
                                qso_count = band_data[call].loc[mult, 'QSO_Count']
                                run_sp = band_data[call].loc[mult, 'Run_SP_Status']
                                text_part = f"({run_sp})"
                                num_part = str(qso_count)
                                padding = " " * (col_width - len(text_part) - len(num_part))
                                cell_content = f"{text_part}{padding}{num_part}"
                            else:
                                cell_content = f"{'0':>{col_width}}"
                            
                            cell_parts.append(cell_content)
                        
                        display_mult = str(mult)
                        if name_column:
                            mult_full_name = prefix_to_name_map.get(mult, overall_prefix_to_name_map.get(mult, ''))

                            if pd.isna(mult_full_name):
                                clean_name = ''
                            else:
                                clean_name = str(mult_full_name).split(';')[0]
                                clean_name = clean_name.replace('\n', ' ').replace('\r', ' ').strip()
                            
                            display_mult = f"{mult} ({clean_name})"

                        row_str = f"{display_mult:<{first_col_width}} | {' | '.join(cell_parts)}"
                        report_lines.append(row_str)

                separator_cells = [f"{'---':^{col_width}}" for _ in all_calls]
                separator = f"{'':<{first_col_width}} | {' | '.join(separator_cells)}"
                report_lines.append(separator)
                
                total_counts = {call: len(mult_sets[call]) for call in all_calls}
                union_count = len(union_of_all_mults)
                max_mults = max(total_counts.values()) if total_counts else 0

                worked_cells = [f"{total_counts[call]:>{col_width}}" for call in all_calls]
                worked_line = f"{'Worked:':<{first_col_width}} | {' | '.join(worked_cells)}"
                
                missed_cells = []
                for call in all_calls:
                    missed_count = union_count - total_counts[call]
                    missed_cells.append(f"{missed_count:>{col_width}}")
                missed_line = f"{'Missed:':<{first_col_width}} | {' | '.join(missed_cells)}"
                
                delta_cells = []
                for call in all_calls:
                    delta = total_counts[call] - max_mults
                    delta_str = str(delta) if delta != 0 else ""
                    delta_cells.append(f"{delta_str:>{col_width}}")
                delta_line = f"{'Delta:':<{first_col_width}} | {' | '.join(delta_cells)}"
                
                report_lines.append(worked_line)
                report_lines.append(missed_line)
                report_lines.append(delta_line)
                report_lines.append("")

                for call in all_calls:
                    all_bands_worked_sum[call] += total_counts[call]
                    all_bands_missed_sum[call] += union_count - total_counts[call]

        if not is_single_band:
            report_lines.append(f"     All Bands Summary".center(table_width))
            
            all_header_cells = [f"{call:^{col_width}}" for call in all_calls]
            all_header = f"{first_col_header:<{first_col_width}} | {' | '.join(all_header_cells)}"
            report_lines.append(all_header)

            all_separator_cells = [f"{'---':^{col_width}}" for _ in all_calls]
            all_separator = f"{'':<{first_col_width}} | {' | '.join(all_separator_cells)}"
            report_lines.append(all_separator)

            max_mults_all = max(all_bands_worked_sum.values()) if all_bands_worked_sum else 0

            all_worked_cells = [f"{all_bands_worked_sum[call]:>{col_width}}" for call in all_calls]
            all_worked_line = f"{'Worked:':<{first_col_width}} | {' | '.join(all_worked_cells)}"
            
            all_missed_cells = [f"{all_bands_missed_sum[call]:>{col_width}}" for call in all_calls]
            all_missed_line = f"{'Missed:':<{first_col_width}} | {' | '.join(all_missed_cells)}"

            all_delta_cells = []
            for call in all_calls:
                delta = all_bands_worked_sum[call] - max_mults_all
                delta_str = str(delta) if delta != 0 else ""
                all_delta_cells.append(f"{delta_str:>{col_width}}")
            all_delta_line = f"{'Delta:':<{first_col_width}} | {' | '.join(all_delta_cells)}"

            report_lines.append(all_worked_line)
            report_lines.append(all_missed_line)
            report_lines.append(all_delta_line)
            report_lines.append("")

        if all_unknown_calls:
            report_lines.append("\n" + "-" * 30)
            report_lines.append(f"Callsigns with 'Unknown' {mult_name}:")
            report_lines.append("-" * 30)
            
            sorted_unknowns = sorted(list(all_unknown_calls))
            col_width = 12
            num_cols = max(1, table_width // (col_width + 2))
            
            for i in range(0, len(sorted_unknowns), num_cols):
                line_calls = sorted_unknowns[i:i+num_cols]
                report_lines.append("  ".join([f"{call:<{col_width}}" for call in line_calls]))

        report_content = "\n".join(report_lines)
        os.makedirs(output_path, exist_ok=True)
        
        filename_calls = '_vs_'.join(sorted(all_calls))
        safe_mult_name = mult_name.lower().replace('/', '_')
        filename = f"{self.report_id}_{safe_mult_name}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"