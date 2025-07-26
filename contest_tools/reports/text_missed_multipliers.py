# Contest Log Analyzer/contest_tools/reports/text_missed_multipliers.py
#
# Purpose: A data-driven text report that generates a comparative "missed multipliers"
#          summary for any multiplier type defined in a contest's JSON file.
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
### Changed
# - The report now includes the full multiplier name (e.g., "Vietnam") next
#   to the prefix (e.g., "3W") when a 'name_column' is available in the
#   contest definition.

## [0.15.0-Beta] - 2025-07-25
# - Standardized version for final review. No functional changes.

## [0.13.0-Beta] - 2025-07-22
### Changed
# - Refactored to be a generic, data-driven report that can handle any
#   multiplier type defined in the contest's JSON file.
# - The report now requires a '--mult-name' argument to specify which
#   multiplier to analyze.
# - Logic was updated to use efficient set operations for comparisons.
# - Report header, footer, and filename are now dynamically generated and formatted.
# - Added a final summary table for "All Bands" to the end of the report.

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
    @property
    def report_id(self) -> str:
        return "missed_multipliers"

    @property
    def report_name(self) -> str:
        return "Missed Multipliers"

    @property
    def report_type(self) -> str:
        return "text"

    def _get_run_sp_status(self, series: pd.Series) -> str:
        """Determines if a multiplier was worked via Run, S&P, or Both."""
        modes = set(series.unique())
        if "Run" in modes and "S&P" in modes:
            return "Both"
        elif "Run" in modes:
            return "Run"
        elif "S&P" in modes:
            return "S&P"
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
        
        if not mult_rule or 'column' not in mult_rule:
            return f"Error: Multiplier type '{mult_name}' not found in definition for {first_log_def.contest_name}."

        mult_column = mult_rule['column']
        name_column = mult_rule.get('name_column') # Will be None if not defined

        all_calls = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in self.logs])
        
        # --- Dynamic Column Width and Headers ---
        col_width = 14
        first_col_header = mult_name.rstrip('s').capitalize()
        first_col_width = 25 if name_column else 7


        # --- Dynamic Header Generation ---
        metadata = first_log.get_metadata()
        contest_name = metadata.get('ContestName', 'UnknownContest')
        first_qso_date = first_log.get_processed_data()['Date'].iloc[0]
        year = first_qso_date.split('-')[0] if first_qso_date else "UnknownYear"
        
        table_width = first_col_width + 3 + (len(all_calls) * (col_width + 3)) - 1
        
        title_text = f"{year} {contest_name} Missed {mult_name}"
        centered_title = f"- {title_text} -".center(table_width)
        separator_line = "-" * len(centered_title)

        report_lines = [separator_line, centered_title, separator_line, ""]

        bands = ['160M', '80M', '40M', '20M', '15M', '10M']
        
        all_bands_worked = {call: 0 for call in all_calls}
        all_bands_missed = {call: 0 for call in all_calls}

        for band in bands:
            band_header_text = f"{band.replace('M', '')} Meters Missed Multipliers"
            report_lines.append(band_header_text.center(table_width))
            
            band_data: Dict[str, pd.DataFrame] = {}
            mult_sets: Dict[str, Set[str]] = {call: set() for call in all_calls}
            # Store a map of prefix to name for this band
            prefix_to_name_map = {}

            for log in self.logs:
                callsign = log.get_metadata().get('MyCall', 'Unknown')
                df_full = log.get_processed_data()
                
                df = df_full[df_full['Dupe'] == False].copy()
                
                if df.empty or mult_column not in df.columns:
                    continue
                
                df_band = df[df['Band'] == band].copy()
                if df_band.empty:
                    continue
                
                df_band.dropna(subset=[mult_column], inplace=True)
                
                # Update the prefix-to-name map if a name column is used
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
                report_lines.append("      (No multipliers on this band for any log)".center(table_width))
                report_lines.append("")
                continue

            missed_mults_on_band = set()
            for call in all_calls:
                missed_mults_on_band.update(union_of_all_mults.difference(mult_sets[call]))

            # --- Format the Table for the Band ---
            header_cells = [f"{call:^{col_width}}" for call in all_calls]
            header = f"{first_col_header:<{first_col_width}} | {' | '.join(header_cells)}"
            report_lines.append(header)

            if not missed_mults_on_band:
                report_lines.append(f"      (No missed {mult_name} on this band)".center(table_width))
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
                        display_mult = f"{mult} ({prefix_to_name_map.get(mult, '')})"

                    row_str = f"{display_mult:<{first_col_width}} | {' | '.join(cell_parts)}"
                    report_lines.append(row_str)

            # --- Footer Calculation and Formatting (runs for every band) ---
            separator_cells = [f"{'---':^{col_width}}" for _ in all_calls]
            separator = f"{'':<{first_col_width}} | {' | '.join(separator_cells)}"
            report_lines.append(separator)
            
            total_counts = {call: len(mult_sets[call]) for call in all_calls}
            union_count = len(union_of_all_mults)
            max_mults = max(total_counts.values()) if total_counts else 0

            worked_cells = [f"{total_counts[call]:>{col_width}}" for call in all_calls]
            worked_line = f"{'Worked:':<{first_col_width}} | {' | '.join(worked_cells)}"
            
            if missed_mults_on_band:
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
                
                report_lines.append(missed_line)
                report_lines.append(delta_line)

            report_lines.append(worked_line)
            report_lines.append("")

            # Accumulate totals for the final summary
            for call in all_calls:
                all_bands_worked[call] += total_counts[call]
                all_bands_missed[call] += union_count - total_counts[call]


        # --- All Bands Summary ---
        report_lines.append(f"        All Bands Summary".center(table_width))
        
        all_header_cells = [f"{call:^{col_width}}" for call in all_calls]
        all_header = f"{first_col_header:<{first_col_width}} | {' | '.join(all_header_cells)}"
        report_lines.append(all_header)

        all_separator_cells = [f"{'---':^{col_width}}" for _ in all_calls]
        all_separator = f"{'':<{first_col_width}} | {' | '.join(all_separator_cells)}"
        report_lines.append(all_separator)

        max_mults_all = max(all_bands_worked.values()) if all_bands_worked else 0

        all_missed_cells = [f"{all_bands_missed[call]:>{col_width}}" for call in all_calls]
        all_missed_line = f"{'Missed:':<{first_col_width}} | {' | '.join(all_missed_cells)}"

        all_delta_cells = []
        for call in all_calls:
            delta = all_bands_worked[call] - max_mults_all
            delta_str = str(delta) if delta != 0 else ""
            all_delta_cells.append(f"{delta_str:>{col_width}}")
        all_delta_line = f"{'Delta:':<{first_col_width}} | {' | '.join(all_delta_cells)}"

        all_worked_cells = [f"{all_bands_worked[call]:>{col_width}}" for call in all_calls]
        all_worked_line = f"{'Worked:':<{first_col_width}} | {' | '.join(all_worked_cells)}"
        
        report_lines.append(all_missed_line)
        report_lines.append(all_delta_line)
        report_lines.append(all_worked_line)
        report_lines.append("")

        # --- Save the Report File ---
        report_content = "\n".join(report_lines)
        os.makedirs(output_path, exist_ok=True)
        
        filename_calls = '_vs_'.join(sorted(all_calls))
        filename = f"{self.report_id}_{mult_name.lower()}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"
