# Contest Log Analyzer/contest_tools/reports/text_missed_multipliers.py
#
# Purpose: A data-driven text report that generates a comparative "missed multipliers"
#          summary for any multiplier type defined in a contest's JSON file.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-16
# Version: 0.37.4-Beta
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
## [0.37.4-Beta] - 2025-08-16
### Changed
# - Refactored logic to inspect the multiplier's `totaling_method`.
#   If `once_per_log`, it now correctly generates a single all-band
#   summary instead of an incorrect per-band breakdown.
## [0.37.1-Beta] - 2025-08-16
### Fixed
# - Corrected file writing logic to append a final newline character,
#   ensuring compatibility with diff utilities.
## [0.32.10-Beta] - 2025-08-12
### Fixed
# - Corrected the report_scope check to include 'per_mode', fixing the
#   blank report bug for the ARRL 10 Meter contest.
## [0.32.9-Beta] - 2025-08-12
### Fixed
# - Refactored the generate method to work on copies of the data, preventing
#   the permanent modification of the original ContestLog objects and fixing
#   the data corruption bug for per-mode reports.
## [0.32.5-Beta] - 2025-08-12
### Changed
# - Modified the generate method to accept a `mode_filter` argument and
#   filter the dataframe by mode, enabling per-mode analysis.
# - Updated the report title and filename to include the mode.
## [0.32.0-Beta] - 2025-08-12
### Fixed
# - Added a protective check to prevent a ValueError when processing a
#   multiplier type that has no QSOs in the logs.
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
# - Added a filter to exclude "Unknown" multipliers from the report data.
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
import logging
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
        mode_filter = kwargs.get('mode_filter')

        if not mult_name:
            return f"Error: 'mult_name' argument is required for the '{self.report_name}' report."

        first_log = self.logs[0]
        first_log_def = first_log.contest_definition
        mult_rule = next((r for r in first_log_def.multiplier_rules if r.get('name', '').lower() == mult_name.lower()), None)
        
        if not mult_rule or 'value_column' not in mult_rule:
            return f"Error: Multiplier type '{mult_name}' not found in definition for {first_log_def.contest_name}."

        all_calls = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in self.logs])
        
        # --- Create a list of dictionaries containing filtered data to process ---
        log_data_to_process = []
        for log in self.logs:
            df = log.get_processed_data()
            if mode_filter:
                filtered_df = df[df['Mode'] == mode_filter].copy()
            else:
                filtered_df = df.copy()
            log_data_to_process.append({'df': filtered_df, 'meta': log.get_metadata()})
        
        metadata = first_log.get_metadata()
        contest_name = metadata.get('ContestName', 'UnknownContest')
        first_qso_date = first_log.get_processed_data()['Date'].iloc[0] if not first_log.get_processed_data().empty else "----"
        year = first_qso_date.split('-')[0]
        
        mode_title_str = f" ({mode_filter})" if mode_filter else ""
        title1 = f"--- {self.report_name}: {mult_name}{mode_title_str} ---"
        title2 = f"{year} {contest_name} - {', '.join(all_calls)}"
        report_lines = []

        totaling_method = mult_rule.get('totaling_method', 'sum_by_band')
        report_scope = first_log_def.multiplier_report_scope
        bands = first_log.contest_definition.valid_bands
        
        # --- LOGIC BRANCH: Determine if report is per-band or contest-wide ---
        if totaling_method == 'once_per_log':
            # This multiplier is scored once for the whole contest.
            # Generate a single, all-band summary table.
            self._generate_missed_mult_table(
                "All Bands", all_calls, log_data_to_process, mult_rule, report_lines
            )
        elif report_scope in ['per_band', 'per_mode']:
            # This multiplier is scored per-band.
            # Generate a separate table for each band.
            for band in bands:
                self._generate_missed_mult_table(
                    band, all_calls, log_data_to_process, mult_rule, report_lines
                )
        else:
             self._generate_missed_mult_table(
                "All Bands", all_calls, log_data_to_process, mult_rule, report_lines
            )

        # --- Add Diagnostic List for Unknown Multipliers ---
        combined_df = pd.concat([log_data['df'] for log_data in log_data_to_process])
        mult_column = mult_rule['value_column']

        if not combined_df.empty and mult_column in combined_df.columns:
            unknown_mult_df = combined_df[combined_df[mult_column] == 'Unknown']
            unknown_calls = sorted(list(unknown_mult_df['Call'].unique()))
            
            if unknown_calls:
                report_lines.append("\n" + "-" * 40)
                report_lines.append(f"Callsigns with Unknown {mult_name}:")
                report_lines.append("-" * 40)
                
                col_width = 12
                num_cols = max(1, 80 // (col_width + 2))
                
                for i in range(0, len(unknown_calls), 5):
                    line_calls = unknown_calls[i:i+5]
                    report_lines.append("  ".join([f"{call:<{col_width}}" for call in line_calls]))

        report_content = "\n".join(report_lines) + "\n"
        os.makedirs(output_path, exist_ok=True)
        
        filename_calls = '_vs_'.join(sorted(all_calls))
        safe_mult_name = mult_name.lower().replace('/', '_')
        mode_suffix = f"_{mode_filter.lower()}" if mode_filter else ""
        filename = f"{self.report_id}_{safe_mult_name}{mode_suffix}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"

    def _generate_missed_mult_table(self, band, all_calls, log_data_to_process, mult_rule, report_lines):
        """Helper to generate a single table for either a specific band or all bands."""
        mult_column = mult_rule['value_column']
        name_column = mult_rule.get('name_column')
        mult_name = mult_rule.get('name', 'Multiplier')
        col_width = 14
        
        # --- Data Aggregation for the specified scope (band or "All Bands") ---
        band_data: Dict[str, pd.DataFrame] = {}
        mult_sets: Dict[str, Set[str]] = {call: set() for call in all_calls}
        prefix_to_name_map = {}

        for log_data in log_data_to_process:
            callsign = log_data['meta'].get('MyCall', 'Unknown')
            df = log_data['df'][log_data['df']['Dupe'] == False].copy()
            
            if df.empty or mult_column not in df.columns:
                continue
            
            df_scope = df if band == "All Bands" else df[df['Band'] == band].copy()
            df_scope = df_scope[df_scope[mult_column] != 'Unknown']
            df_scope = df_scope[df_scope[mult_column].notna()]
            
            if df_scope.empty:
                continue
            
            if name_column and name_column in df_scope.columns:
                name_map_df = df_scope[[mult_column, name_column]].dropna().drop_duplicates()
                for _, row in name_map_df.iterrows():
                    prefix_to_name_map[row[mult_column]] = row[name_column]

            agg_data = df_scope.groupby(mult_column).agg(
                QSO_Count=('Call', 'size'),
                Run_SP_Status=('Run', self._get_run_sp_status)
            )
            
            band_data[callsign] = agg_data
            mult_sets[callsign].update(agg_data.index)

        union_of_all_mults = set.union(*mult_sets.values())
        
        # --- Determine table structure and headers ---
        if mult_name.lower() == 'countries':
            first_col_header = mult_rule.get('source', 'dxcc').upper()
        else:
            first_col_header = mult_name[:-1] if mult_name.lower().endswith('s') else mult_name
            first_col_header = first_col_header.capitalize()

        max_mult_len = len(first_col_header)
        if union_of_all_mults:
            max_mult_len = max([len(str(m)) for m in union_of_all_mults] + [max_mult_len])

        first_col_width = max(max_mult_len, len("Missed:"))
        
        header_cells = [f"{call:^{col_width}}" for call in all_calls]
        table_header = f"{first_col_header:<{first_col_width}} | {' | '.join(header_cells)}"
        table_width = len(table_header)
        
        band_header_text = f"\n{band.replace('M', '')} Meters Missed Multipliers" if band != "All Bands" else f"\nOverall Missed Multipliers"
        report_lines.append(band_header_text.center(table_width))

        if not union_of_all_mults:
            report_lines.append(f"     (No multipliers found for this scope)".center(table_width))
            return

        report_lines.append(table_header)
        
        # --- Populate Table Rows ---
        missed_mults_on_band = set()
        for call in all_calls:
            missed_mults_on_band.update(union_of_all_mults.difference(mult_sets[call]))

        if not missed_mults_on_band:
            report_lines.append(f"     (No missed {mult_name} for this scope)".center(table_width))
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
                if name_column and mult in prefix_to_name_map:
                    mult_full_name = prefix_to_name_map[mult]
                    if pd.notna(mult_full_name) and mult_full_name != '':
                        clean_name = str(mult_full_name).split(';')[0].strip()
                        display_mult = f"{mult} ({clean_name})"

                row_str = f"{display_mult:<{first_col_width}} | {' | '.join(cell_parts)}"
                report_lines.append(row_str)

        # --- Populate Table Footer (Summary) ---
        separator = f"{'':<{first_col_width}} | {' | '.join([f'{'---':^{col_width}}' for _ in all_calls])}"
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