# Contest Log Analyzer/contest_tools/reports/text_missed_multipliers.py
#
# Purpose: A data-driven text report that generates a comparative "missed multipliers"
#          summary. This version uses the `tabulate` library for formatting.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-24
# Version: 0.40.15-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0.
# --- Revision History ---
## [0.40.15-Beta] - 2025-08-24
### Added
# - Initial creation of this parallel report as a proof-of-concept for
#   the `tabulate` library.
### Changed
# - Replaced all custom table formatting logic with the `tabulate` library
#   using the 'psql' format for improved simplicity and robustness.
from typing import List, Dict, Any, Set
import pandas as pd
import os
import logging
from tabulate import tabulate
from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a comparative report showing a specific multiplier worked by each
    station on each band, highlighting missed opportunities (tabulate version).
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
        report_lines = [title1, title2]

        totaling_method = mult_rule.get('totaling_method', 'sum_by_band')
        report_scope = first_log_def.multiplier_report_scope
        bands = first_log.contest_definition.valid_bands
        
        if totaling_method == 'once_per_log':
            self._generate_missed_mult_table(
                "All Bands", all_calls, log_data_to_process, mult_rule, report_lines
            )
        elif report_scope in ['per_band', 'per_mode']:
            for band in bands:
                self._generate_missed_mult_table(
                    band, all_calls, log_data_to_process, mult_rule, report_lines
                )
        else:
             self._generate_missed_mult_table(
                "All Bands", all_calls, log_data_to_process, mult_rule, report_lines
            )

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
        
        band_data: Dict[str, pd.DataFrame] = {}
        mult_sets: Dict[str, Set[str]] = {call: set() for call in all_calls}
        prefix_to_name_map = {}

        for log_data in log_data_to_process:
            callsign = log_data['meta'].get('MyCall', 'Unknown')
            df = log_data['df'][log_data['df']['Dupe'] == False].copy()
            
            if df.empty or mult_column not in df.columns: continue
            
            df_scope = df if band == "All Bands" else df[df['Band'] == band].copy()
            df_scope = df_scope[df_scope[mult_column] != 'Unknown']
            df_scope = df_scope[df_scope[mult_column].notna()]
            
            if df_scope.empty: continue
            
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
        missed_mults_on_band = set()
        for call in all_calls:
            missed_mults_on_band.update(union_of_all_mults.difference(mult_sets[call]))
            
        first_col_header = mult_name[:-1] if mult_name.lower().endswith('s') else mult_name
        first_col_header = first_col_header.capitalize()

        band_header_text = f"\n{band.replace('M', '')} Meters Missed Multipliers" if band != "All Bands" else f"\nOverall Missed Multipliers"
        report_lines.append(band_header_text)

        if not union_of_all_mults:
            report_lines.append(f"     (No multipliers found for this scope)")
            return

        # --- Table Generation with tabulate ---
        headers = [first_col_header] + all_calls
        main_table_data = []

        if not missed_mults_on_band:
            report_lines.append(f"     (No missed {mult_name} for this scope)")
        else:
            for mult in sorted(list(missed_mults_on_band)):
                display_mult = str(mult)
                if name_column and mult in prefix_to_name_map:
                    clean_name = str(prefix_to_name_map[mult]).split(';')[0].strip()
                    display_mult = f"{mult} ({clean_name})"
                
                row = {first_col_header: display_mult}
                for call in all_calls:
                    if call in band_data and mult in band_data[call].index:
                        qso_count = band_data[call].loc[mult, 'QSO_Count']
                        run_sp = band_data[call].loc[mult, 'Run_SP_Status']
                        row[call] = f"({run_sp}) {qso_count}"
                    else:
                        row[call] = "0"
                main_table_data.append(row)

            report_lines.append(tabulate(main_table_data, headers="keys", tablefmt="psql", stralign="left", numalign="right"))

        # --- Summary Table ---
        summary_table_data = []
        total_counts = {call: len(mult_sets[call]) for call in all_calls}
        union_count = len(union_of_all_mults)
        max_mults = max(total_counts.values()) if total_counts else 0

        worked_row = {' ': 'Worked:'}
        missed_row = {' ': 'Missed:'}
        delta_row = {' ': 'Delta:'}

        for call in all_calls:
            worked_row[call] = total_counts.get(call, 0)
            missed_row[call] = union_count - total_counts.get(call, 0)
            delta = total_counts.get(call, 0) - max_mults
            delta_row[call] = delta if delta != 0 else ''

        summary_table_data.extend([worked_row, missed_row, delta_row])
        report_lines.append(tabulate(summary_table_data, headers="keys", tablefmt="psql", stralign="left", numalign="right"))