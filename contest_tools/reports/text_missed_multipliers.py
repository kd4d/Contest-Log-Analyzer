# Contest Log Analyzer/contest_tools/reports/text_missed_multipliers.py
#
# Purpose: A data-driven text report that generates a comparative "missed multipliers"
#          summary for any multiplier type defined in a contest's JSON file.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-22
# Version: 0.13.0-Beta
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

## [0.13.0-Beta] - 2025-07-22
# - Initial release of the generic Missed Multipliers report.
# - The report is now data-driven by the 'multiplier_rules' in the contest JSON.
# - Requires a 'mult_name' argument to specify which multiplier to analyze.
# - Uses set operations and correct formatting for the output table.

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

        Args:
            output_path (str): The directory where any output files should be saved.
            **kwargs:
                - include_dupes (bool): This report always excludes dupes.
                - mult_name (str): The name of the multiplier to analyze (e.g., 'Countries', 'Zones').
        """
        include_dupes = kwargs.get('include_dupes', False)
        mult_name = kwargs.get('mult_name')

        if not mult_name:
            return "Error: 'mult_name' argument is required for the Missed Multipliers report."

        first_log_def = self.logs[0].contest_definition
        mult_column = None
        for rule in first_log_def.multiplier_rules:
            if rule.get('name', '').lower() == mult_name.lower():
                mult_column = rule.get('column')
                break
        
        if not mult_column:
            return f"Error: Multiplier type '{mult_name}' not found in definition for {first_log_def.contest_name}."

        if include_dupes:
            print(f"Note: The Missed {mult_name} report always excludes dupes.")
        
        title_line = f"-    Missed {mult_name}    -"
        separator_line = "-" * len(title_line)

        report_lines = [separator_line, title_line, separator_line, ""]

        all_calls = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in self.logs])
        bands = ['160M', '80M', '40M', '20M', '15M', '10M']
        col_width = 12

        for band in bands:
            report_lines.append(f"            {band.replace('M', '')} Meters")
            
            band_data: Dict[str, pd.DataFrame] = {}
            mult_sets: Dict[str, Set[str]] = {call: set() for call in all_calls}

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

                agg_data = df_band.groupby(mult_column).agg(
                    QSO_Count=('Call', 'size'),
                    Run_SP_Status=('Run', self._get_run_sp_status)
                )
                
                band_data[callsign] = agg_data
                mult_sets[callsign].update(agg_data.index)

            union_of_all_mults = set.union(*mult_sets.values())
            
            if not union_of_all_mults:
                report_lines.append("      (No multipliers on this band for any log)")
                report_lines.append("")
                continue

            missed_mults = set()
            for call in all_calls:
                missed_mults.update(union_of_all_mults.difference(mult_sets[call]))

            if not missed_mults:
                report_lines.append(f"      (No missed {mult_name} on this band)")
                report_lines.append("")
                continue

            header_cells = [f"{call:^{col_width}}" for call in all_calls]
            header = f"{'':<7} | {' | '.join(header_cells)}"
            report_lines.append(header)

            for mult in sorted(list(missed_mults)):
                cell_parts = []
                for call in all_calls:
                    cell_content = "0"
                    if call in band_data and mult in band_data[call].index:
                        qso_count = band_data[call].loc[mult, 'QSO_Count']
                        run_sp = band_data[call].loc[mult, 'Run_SP_Status']
                        cell_content = f"{qso_count} ({run_sp})"
                    
                    cell_parts.append(f"{cell_content:^{col_width}}")
                
                row_str = f"{str(mult):<7} | {' | '.join(cell_parts)}"
                report_lines.append(row_str)

            separator_cells = [f"{'---':^{col_width}}" for _ in all_calls]
            separator = f"{'':<7} | {' | '.join(separator_cells)}"
            report_lines.append(separator)
            
            mult_counts = {call: len(mult_sets[call]) for call in all_calls}
            max_mults = max(mult_counts.values()) if mult_counts else 0

            mults_cells = [f"{mult_counts[call]:^{col_width}}" for call in all_calls]
            mults_line = f"{'Mults:':<7} | {' | '.join(mults_cells)}"
            
            delta_cells = []
            for call in all_calls:
                delta = mult_counts[call] - max_mults
                delta_str = str(delta) if delta != 0 else ""
                delta_cells.append(f"{delta_str:^{col_width}}")
            delta_line = f"{'Delta:':<7} | {' | '.join(delta_cells)}"

            report_lines.append(mults_line)
            report_lines.append(delta_line)
            report_lines.append("")

        report_content = "\n".join(report_lines)
        os.makedirs(output_path, exist_ok=True)
        
        filename_calls = '_vs_'.join(sorted(all_calls))
        filename = f"{self.report_id}_{mult_name.lower()}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"
