# Contest Log Analyzer/contest_tools/reports/text_missed_multipliers.py
#
# Purpose: A data-driven text report that generates a comparative "missed multipliers"
#          summary for any multiplier type defined in a contest's JSON file.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-11
# Version: 0.31.45-Beta
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
## [0.31.45-Beta] - 2025-08-11
### Fixed
# - Corrected column width calculation to be global instead of per-band,
#   ensuring consistent table alignment throughout the report.
## [0.31.44-Beta] - 2025-08-11
### Fixed
# - Corrected the first column width calculation to account for summary
#   labels, fixing the table alignment.
## [0.31.44-Beta] - 2025-08-10
### Changed
# - Modified main report logic to exclude "Unknown" multipliers from the
#   comparative analysis.
### Added
# - Added a diagnostic section to list all callsigns associated with an
#   "Unknown" multiplier.
## [0.31.22-Beta] - 2025-08-09
### Changed
# - Re-enabled "Unknown" multipliers by removing the exclusion filter to
#   treat them as a valid category for comparison.
## [0.31.21-Beta] - 2025-08-09
### Fixed
# - Added a filter to exclude "Unknown" multipliers from the main report data.
## [0.30.37-Beta] - 2025-08-06
### Fixed
# - Adjusted dynamic column width calculation to set a minimum width based
#   on summary labels (e.g., "Worked:"), fixing alignment for short mult names.
## [0.30.36-Beta] - 2025-08-06
### Changed
# - Reverted the two-line multiplier format.
# - First column is now correctly formatted as "Prefix (Country Name)".
# - First column header is now dynamically set based on the multiplier rule.
# - First column width is now calculated dynamically to fit the content.
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
            return f"Error: 'mult_name' argument is required for the '{self.report_name}' report."

        first_log = self.logs[0]
        first_log_def = first_log.contest_definition
        mult_rule = next((r for r in first_log_def.multiplier_rules if r.get('name', '').lower() == mult_name.lower()), None)
        
        if not mult_rule or 'value_column' not in mult_rule:
            return f"Error: Multiplier type '{mult_name}' not found in definition for {first_log_def.contest_name}."

        mult_column = mult_rule['value_column']
        name_column = mult_rule.get('name_column')
        report_scope = first_log_def.multiplier_report_scope

        all_calls = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in self.logs])
        
        col_width = 14
        
        # --- Dynamic First Column Header ---
        if mult_name.lower() == 'countries':
            source_type = mult_rule.get('source', 'dxcc').upper()
            first_col_header = source_type
        elif mult_name.lower() == 'prefixes':
            first_col_header = 'Prefix'
        else:
            first_col_header = mult_name[:-1] if mult_name.lower().endswith('s') else mult_name
            first_col_header = first_col_header.capitalize()
            
        metadata = first_log.get_metadata()
        contest_name = metadata.get('ContestName', 'UnknownContest')
        first_qso_date = first_log.get_processed_data()['Date'].iloc[0] if not first_log.get_processed_data().empty else "----"
        year = first_qso_date.split('-')[0]
        
        title1 = f"--- {self.report_name}: {mult_name} ---"
        title2 = f"{year} {contest_name} - {', '.join(all_calls)}"
        
        report_lines = []
        bands = first_log.contest_definition.valid_bands
        
        # --- Global Column Width Calculation ---
        max_mult_len = len(first_col_header)
        summary_label_width = len("Missed:")
        
        combined_df = pd.concat([log.get_processed_data() for log in self.logs])
        if not combined_df.empty and mult_column in combined_df.columns:
            all_mults = combined_df[mult_column].dropna().unique()
            if name_column and name_column in combined_df.columns:
                name_map_df = combined_df[[mult_column, name_column]].dropna().drop_duplicates()
                name_map = name_map_df.set_index(mult_column)[name_column].to_dict()
                for mult in all_mults:
                    full_name = name_map.get(mult, '')
                    display_string = f"{mult} ({full_name})" if pd.notna(full_name) and full_name != '' else str(mult)
                    max_mult_len = max(max_mult_len, len(display_string))
            else:
                max_mult_len = max(max_mult_len, max(len(str(m)) for m in all_mults if pd.notna(m)))

        first_col_width = max(max_mult_len, summary_label_width)

        if report_scope == 'per_band':
            for band in bands:
                band_header_text = f"\n{band.replace('M', '')} Meters Missed Multipliers"
                
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
                    
                    df_band = df_band[df_band[mult_column] != 'Unknown']
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
                
                missed_mults_on_band = set()
                for call in all_calls:
                    missed_mults_on_band.update(union_of_all_mults.difference(mult_sets[call]))

                header_cells = [f"{call:^{col_width}}" for call in all_calls]
                table_header = f"{first_col_header:<{first_col_width}} | {' | '.join(header_cells)}"
                table_width = len(table_header)

                if not report_lines:
                    header_width = max(table_width, len(title1), len(title2))
                    if len(title1) > table_width or len(title2) > table_width:
                         report_lines.append(f"{title1.ljust(header_width)}")
                         report_lines.append(f"{title2.center(header_width)}")
                    else:
                         report_lines.append(title1.center(header_width))
                         report_lines.append(title2.center(header_width))

                report_lines.append(band_header_text.center(table_width))

                if not union_of_all_mults:
                    report_lines.append(f"     (No multipliers on this band for any log)".center(table_width))
                    continue

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
                            mult_full_name = prefix_to_name_map.get(mult, name_map.get(mult, ''))
                            if pd.notna(mult_full_name) and mult_full_name != '':
                                clean_name = str(mult_full_name).split(';')[0].strip()
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
                
                missed_cells = [f"{union_count - total_counts[call]:>{col_width}}" for call in all_calls]
                missed_line = f"{'Missed:':<{first_col_width}} | {' | '.join(missed_cells)}"
                
                delta_cells = [f"{str(total_counts[call] - max_mults) if total_counts[call] - max_mults != 0 else '':>{col_width}}" for call in all_calls]
                delta_line = f"{'Delta:':<{first_col_width}} | {' | '.join(delta_cells)}"
                
                report_lines.append(worked_line)
                report_lines.append(missed_line)
                report_lines.append(delta_line)
        
        # --- Add Diagnostic List for Unknown Multipliers ---
        if not combined_df.empty and mult_column in combined_df.columns:
            unknown_mult_df = combined_df[combined_df[mult_column] == 'Unknown']
            unknown_calls = sorted(list(unknown_mult_df['Call'].unique()))
            
            if unknown_calls:
                table_width = len(table_header) if 'table_header' in locals() else 80
                report_lines.append("\n" + "-" * 40)
                report_lines.append(f"Callsigns with Unknown {first_col_header}:")
                report_lines.append("-" * 40)
                
                col_width = 12
                num_cols = max(1, table_width // (col_width + 2))
                
                for i in range(0, len(unknown_calls), num_cols):
                    line_calls = unknown_calls[i:i+num_cols]
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