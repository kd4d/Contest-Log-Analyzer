# Contest Log Analyzer/contest_tools/reports/text_score_report.py
#
# Purpose: A text report that generates a detailed score summary for each
#          log, broken down by band.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-25
# Version: 0.49.5-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0.
# --- Revision History ---
## [0.49.5-Beta] - 2025-08-25
### Fixed
# - Refactored logic to filter zero-point QSOs at the start of the
#   calculation, ensuring the main QSO counts are correct.
## [0.49.4-Beta] - 2025-08-25
### Fixed
# - Corrected a variable name typo that prevented zero-point QSOs from
#   being correctly filtered out of multiplier calculations.
## [0.49.3-Beta] - 2025-08-25
### Fixed
# - Corrected the multiplier counting logic in `_calculate_all_scores` to
#   respect the "applies_to" key, fixing the double-counting bug for
#   contests like ARRL DX.
## [0.49.2-Beta] - 2025-08-24
### Changed
# - Refactored diagnostic logic to use the new, generic
#   `mutually_exclusive_mults` property from the ContestDefinition class.
## [0.49.1-Beta] - 2025-08-24
### Fixed
# - Corrected diagnostic logic to read the `score_report_rules` property
#   from the ContestDefinition class, fixing the bug that caused the
#   mutual-exclusion logic to be skipped.
## [0.48.6-Beta] - 2025-08-24
### Fixed
# - Modified `_add_diagnostic_sections` to honor the
#   `suppress_blank_mult_warnings` flag, hiding irrelevant diagnostic
#   lists for contests like WPX.
## [0.48.5-Beta] - 2025-08-23
### Fixed
# - Reworked per-band summary logic to correctly display "first-worked"
#   counts for multipliers that are counted once per contest.
## [0.48.4-Beta] - 2025-08-23
### Fixed
# - Refactored the `_calculate_all_scores` method to correctly handle the
#   `once_per_log` multiplier totaling method, fixing the WPX score bug.
## [0.48.3-Beta] - 2025-08-23
### Fixed
# - Refactored the `_calculate_all_scores` method to correctly handle the
#   `once_per_log` multiplier totaling method, fixing the WPX score bug.
## [0.48.0-Beta] - 2025-08-23
### Changed
# - Modified score report to read a `suppress_blank_mult_warnings` key
#   from the contest definition to conditionally disable irrelevant
#   warnings and diagnostics for contests like WPX.
from typing import List, Dict, Set, Tuple
import pandas as pd
import os
import re
import json
import logging
import hashlib
from ..contest_log import ContestLog
from ..contest_definitions import ContestDefinition
from .report_interface import ContestReport
from ._report_utils import calculate_multiplier_pivot

class Report(ContestReport):
    """
    Generates a detailed score summary report for each log.
    """
    report_id: str = "score_report"
    report_name: str = "Score Summary"
    report_type: str = "text"
    supports_single = True
    
    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content.
        """
        final_report_messages = []

        for log in self.logs:
            metadata = log.get_metadata()
            df_full = log.get_processed_data()

            callsign = metadata.get('MyCall', 'UnknownCall')
            contest_name = metadata.get('ContestName', 'UnknownContest')

            if df_full.empty:
                msg = f"Skipping score report for {callsign}: No QSO data available."
                final_report_messages.append(msg)
                continue

            # --- All calculations are now performed in a single, authoritative function ---
            summary_data, total_summary, final_score = self._calculate_all_scores(log, output_path, **kwargs)
            
            # --- Formatting ---
            mult_names = [rule['name'] for rule in log.contest_definition.multiplier_rules]
            col_order = ['Band', 'Mode', 'QSOs'] + mult_names + ['Points', 'AVG']
            col_widths = {key: len(str(key)) for key in col_order}

            all_data_for_width = summary_data + [total_summary]
            for row in all_data_for_width:
                for key, value in row.items():
                    if key in col_widths:
                        val_len = len(f"{value:.2f}") if isinstance(value, float) else len(str(value))
                        col_widths[key] = max(col_widths.get(key, 0), val_len)

            year = df_full['Date'].iloc[0].split('-')[0] if not df_full.empty and not df_full['Date'].dropna().empty else "----"
            
            header_parts = [f"{name:>{col_widths[name]}}" for name in col_order]
            header = "  ".join(header_parts)
            table_width = len(header)
            separator = "-" * table_width
            
            title1 = f"--- {self.report_name} ---"
            title2 = f"{year} {contest_name} - {callsign}"
            
            report_lines = []
            header_width = max(table_width, len(title1), len(title2))
            report_lines.append(title1.center(header_width))
            report_lines.append(title2.center(header_width))
            
            report_lines.append("")
            on_time_str = metadata.get('OperatingTime')
            if on_time_str:
                report_lines.append(f"Operating Time: {on_time_str}")
            report_lines.append("")
            
            report_lines.append(header)
            report_lines.append(separator)

            # Sort data for display
            canonical_band_order = [band[1] for band in ContestLog._HF_BANDS]
            summary_data.sort(key=lambda x: (canonical_band_order.index(x['Band']), x['Mode']))

            for item in summary_data:
                data_parts = [f"{str(item.get(name, '')):{'>' if name != 'Band' else '<'}{col_widths[name]}}" for name in ['Band', 'Mode', 'QSOs']]
                data_parts.extend([f"{item.get(name, 0):>{col_widths[name]}}" for name in mult_names])
                data_parts.extend([
                    f"{item.get('Points', 0):>{col_widths['Points']}}",
                    f"{item.get('AVG', 0):>{col_widths['AVG']}.2f}"
                ])
                report_lines.append("  ".join(data_parts))
            
            report_lines.append(separator)
            
            total_parts = [f"{str(total_summary.get(name, '')):{'>' if name != 'Band' else '<'}{col_widths[name]}}" for name in ['Band', 'Mode', 'QSOs']]
            total_parts.extend([f"{total_summary.get(name, 0):>{col_widths[name]}}" for name in mult_names])
            total_parts.extend([
                f"{total_summary.get('Points', 0):>{col_widths['Points']}}",
                f"{total_summary.get('AVG', 0):>{col_widths['AVG']}.2f}"
            ])
            report_lines.append("  ".join(total_parts))
            
            report_lines.append("=" * table_width)
            score_text = f"TOTAL SCORE : {final_score:,.0f}"
            report_lines.append(score_text.rjust(table_width))

            self._add_diagnostic_sections(report_lines, df_full, log)

            report_content = "\n".join(report_lines) + "\n"
            os.makedirs(output_path, exist_ok=True)
            filename = f"{self.report_id}_{callsign}.txt"
            filepath = os.path.join(output_path, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            final_report_messages.append(f"Text report saved to: {filepath}")

        return "\n".join(final_report_messages)

    def _add_diagnostic_sections(self, report_lines: List[str], df: pd.DataFrame, log: ContestLog):
        """Appends sections for 'Unknown' and 'Unassigned' multipliers."""
        if df.empty:
            return

        contest_def = log.contest_definition
        if getattr(contest_def, 'suppress_blank_mult_warnings', False):
            return
            
        log_location_type = getattr(log, '_my_location_type', None)
        exclusive_groups = contest_def.mutually_exclusive_mults

        for rule in contest_def.multiplier_rules:
            applies_to = rule.get('applies_to')
            if applies_to and log_location_type and applies_to != log_location_type:
                continue

            mult_name = rule['name']
            mult_col = rule['value_column']

            if mult_col not in df.columns:
                continue

            # --- Check for "Unknown" Multipliers ---
            unknown_df = df[df[mult_col] == 'Unknown']
            unknown_calls = sorted(list(unknown_df['Call'].unique()))
            if unknown_calls:
                report_lines.append("\n" + "-" * 40)
                report_lines.append(f"Callsigns with 'Unknown' {mult_name}:")
                report_lines.append("-" * 40)
                for i in range(0, len(unknown_calls), 5):
                    line_calls = unknown_calls[i:i+5]
                    report_lines.append("  ".join([f"{call:<12}" for call in line_calls]))

            # --- Check for "Unassigned" (NaN) Multipliers ---
            unassigned_df = df[df[mult_col].isna()]
            
            # Filter out intentional blanks for mutually exclusive mults
            for group in exclusive_groups:
                if mult_col in group:
                    partner_cols = [p for p in group if p != mult_col and p in df.columns]
                    if partner_cols:
                        indices_to_check = unassigned_df.index
                        partner_values_exist = df.loc[indices_to_check, partner_cols].notna().any(axis=1)
                        unassigned_df = unassigned_df.loc[~partner_values_exist]
            
            unassigned_calls = sorted(list(unassigned_df['Call'].unique()))
            if unassigned_calls:
                report_lines.append("\n" + "-" * 40)
                report_lines.append(f"Callsigns with Unassigned {mult_name}:")
                report_lines.append("-" * 40)
                for i in range(0, len(unassigned_calls), 5):
                    line_calls = unassigned_calls[i:i+5]
                    report_lines.append("  ".join([f"{call:<12}" for call in line_calls]))

    def _calculate_all_scores(self, log: ContestLog, output_path: str, **kwargs) -> Tuple[List[Dict], Dict, int]:
        df_full = log.get_processed_data()
        contest_def = log.contest_definition
        multiplier_rules = contest_def.multiplier_rules
        
        # Start with a DataFrame of non-duplicate QSOs
        df_net = df_full[df_full['Dupe'] == False].copy()
        
        # If the contest rules require it, filter out zero-point QSOs for all counts
        if not contest_def.mults_from_zero_point_qsos:
            df_net = df_net[df_net['QSOPoints'] > 0].copy()
        
        # --- Pre-computation for all multiplier types ---
        per_band_mult_counts = {}
        first_worked_mult_counts = {}
        log_location_type = getattr(log, '_my_location_type', None)
        
        for rule in multiplier_rules:
            mult_col = rule['value_column']
            if mult_col not in df_net.columns: continue

            df_valid_mults = df_net[df_net[mult_col].notna() & (df_net[mult_col] != 'Unknown')]
            
            if rule.get('totaling_method') == 'once_per_log':
                df_sorted = df_valid_mults.sort_values(by='Datetime')
                overall_seen_mults = set()
                new_mults_per_band_mode = {}
                
                band_mode_groups = df_sorted.groupby(['Band', 'Mode'])
                for (band, mode), group_df in band_mode_groups:
                    mults_in_group = set(group_df[mult_col].unique())
                    new_mults = mults_in_group - overall_seen_mults
                    new_mults_per_band_mode[(band, mode)] = len(new_mults)
                    overall_seen_mults.update(new_mults)
                first_worked_mult_counts[mult_col] = new_mults_per_band_mode
            else:
                pivot = calculate_multiplier_pivot(df_valid_mults, mult_col, group_by_call=False)
                per_band_mult_counts[mult_col] = (pivot > 0).sum(axis=0)

        # --- Per-Band/Mode Summary Calculation ---
        summary_data = []
        if not df_net.empty:
            band_mode_groups = df_net.groupby(['Band', 'Mode'])
            for (band, mode), group_df in band_mode_groups:
                band_mode_summary = {'Band': band, 'Mode': mode}
                band_mode_summary['QSOs'] = len(group_df)
                band_mode_summary['Points'] = group_df['QSOPoints'].sum()
                
                for rule in multiplier_rules:
                    m_col = rule['value_column']
                    m_name = rule['name']
                    
                    if rule.get('totaling_method') == 'once_per_log':
                        band_mode_summary[m_name] = first_worked_mult_counts.get(m_col, {}).get((band, mode), 0)
                    else:
                        band_counts_series = per_band_mult_counts.get(m_col)
                        if band_counts_series is not None:
                            band_mode_summary[m_name] = band_counts_series.get(band, 0)
                        else:
                            band_mode_summary[m_name] = 0

                band_mode_summary['AVG'] = (band_mode_summary['Points'] / band_mode_summary['QSOs']) if band_mode_summary['QSOs'] > 0 else 0
                summary_data.append(band_mode_summary)
                
        # --- TOTAL Summary Calculation ---
        total_summary = {'Band': 'TOTAL', 'Mode': ''}
        total_summary['QSOs'] = df_net.shape[0]
        total_summary['Points'] = df_net['QSOPoints'].sum()

        total_multiplier_count = 0
        for rule in multiplier_rules:
            mult_name = rule['name']
            mult_col = rule['value_column']

            applies_to = rule.get('applies_to')
            if applies_to and log_location_type and applies_to != log_location_type:
                total_summary[mult_name] = 0
                continue
            
            if mult_col in df_net.columns:
                df_valid_mults = df_net[df_net[mult_col].notna() & (df_net[mult_col] != 'Unknown')]

                if rule.get('totaling_method') == 'once_per_log':
                    total_mults_for_rule = df_valid_mults[mult_col].nunique()
                else:
                    total_mults_for_rule = per_band_mult_counts.get(mult_col, pd.Series()).sum()
            
                total_summary[mult_name] = total_mults_for_rule
                total_multiplier_count += total_mults_for_rule
            
        total_summary['AVG'] = (total_summary['Points'] / total_summary['QSOs']) if total_summary['QSOs'] > 0 else 0
        
        # --- Data-driven score calculation ---
        if contest_def.score_formula == 'qsos_times_mults':
            final_score = total_summary['QSOs'] * total_multiplier_count
        else: # Default to points_times_mults
            final_score = total_summary['Points'] * total_multiplier_count
        
        return summary_data, total_summary, final_score