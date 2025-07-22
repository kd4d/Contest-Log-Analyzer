# Contest Log Analyzer/contest_tools/reports/text_missed_country_mults.py
#
# Purpose: A text report that generates a comparative "missed multipliers" summary for countries.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-22
# Version: 0.12.0-Beta
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

## [0.12.0-Beta] - 2025-07-22
### Changed
# - Refactored the generate() method to use **kwargs for flexible argument passing.

from typing import List, Dict, Any, Set
import pandas as pd
import numpy as np
import os
from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a comparative report showing country multipliers worked by each station
    on each band, highlighting missed opportunities.
    """
    @property
    def report_id(self) -> str:
        return "missed_country_mults"

    @property
    def report_name(self) -> str:
        return "Missed Country Multipliers"

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
                - mult_type (str): 'dxcc' or 'wae'. Defaults to 'dxcc'.
        """
        include_dupes = kwargs.get('include_dupes', False)
        mult_type = kwargs.get('mult_type', 'dxcc')

        if include_dupes:
            print("Note: The Missed Country Multipliers report always excludes dupes.")
        
        mult_header_text = "WAE Countries" if mult_type == 'wae' else "DXCC Countries"
        
        title_line = f"-    Missed {mult_header_text}    -"
        separator_line = "-" * len(title_line)

        report_lines = [
            separator_line,
            title_line,
            separator_line,
            ""
        ]

        all_calls = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in self.logs])
        bands = ['160M', '80M', '40M', '20M', '15M', '10M']
        col_width = 12 # Set a fixed width for each callsign column

        for band in bands:
            report_lines.append(f"            {band.replace('M', '')} Meters")
            
            # --- Data Aggregation for the Band ---
            band_data: Dict[str, pd.DataFrame] = {}
            mult_sets: Dict[str, Set[str]] = {call: set() for call in all_calls}

            for log in self.logs:
                callsign = log.get_metadata().get('MyCall', 'Unknown')
                df_full = log.get_processed_data()
                
                df = df_full[df_full['Dupe'] == False].copy()
                
                if df.empty:
                    continue

                if mult_type == 'wae':
                    df['MultiplierPfx'] = np.where(
                        (df['WAEPfx'].notna()) & (df['WAEPfx'] != ''), 
                        df['WAEPfx'], 
                        df['DXCCPfx']
                    )
                else: # Default to DXCC
                    df['MultiplierPfx'] = df['DXCCPfx']
                
                df_band = df[df['Band'] == band]
                if df_band.empty:
                    continue
                
                agg_data = df_band.groupby('MultiplierPfx').agg(
                    QSO_Count=('Call', 'size'),
                    Run_SP_Status=('Run', self._get_run_sp_status)
                )
                
                band_data[callsign] = agg_data
                mult_sets[callsign].update(agg_data.index)

            # --- Use Set Operations to Find Missed Multipliers ---
            union_of_all_mults = set.union(*mult_sets.values())
            
            if not union_of_all_mults:
                report_lines.append("      (No QSOs on this band for any log)")
                report_lines.append("")
                continue

            missed_mults = set()
            for call in all_calls:
                missed_mults.update(union_of_all_mults.difference(mult_sets[call]))

            if not missed_mults:
                report_lines.append("      (No missed multipliers on this band)")
                report_lines.append("")
                continue

            # --- Format the Table for the Band ---
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
                
                row_str = f"{mult:<7} | {' | '.join(cell_parts)}"
                report_lines.append(row_str)

            # --- Footer Calculation and Formatting ---
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

        # --- Save the Report File ---
        report_content = "\n".join(report_lines)
        os.makedirs(output_path, exist_ok=True)
        
        filename_calls = '_vs_'.join(sorted(all_calls))
        filename = f"{self.report_id}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"
