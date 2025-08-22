# Contest Log Analyzer/contest_tools/reports/text_score_report.py
#
# Purpose: A text report that generates a detailed score summary for each
#          log, broken down by band.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-22
# Version: 0.47.2-Beta
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
## [0.47.2-Beta] - 2025-08-22
### Fixed
# - Replaced the per-band calculation logic with a direct lookup from the
#   authoritative pivot_table results. This is the final correction to
#   ensure all calculations are consistent.
## [0.47.1-Beta] - 2025-08-22
### Changed
# - Refactored the script to use the new calculate_multiplier_pivot()
#   shared utility function, ensuring consistent logic with other reports.
## [0.46.0-Beta] - 2025-08-22
### Fixed
# - Corrected the per-band multiplier calculation to source its data
#   directly from the authoritative pivot_table. This resolves the bug
#   causing inconsistent counts between the report body and the total line.
## [0.45.1-Beta] - 2025-08-22
### Added
# - Added a diagnostic logging statement to show the shape of the dataframe
#   used for multiplier calculations to help isolate a bug.
## [0.45.0-Beta] - 2025-08-22
### Fixed
# - Unified the multiplier calculation logic within the report. Both the
#   per-band rows and the final total are now derived from a single,
#   authoritative pivot_table calculation, ensuring internal consistency
#   and correcting the long-standing count discrepancy bug.
## [0.44.0-Beta] - 2025-08-22
### Fixed
# - Refactored the script to perform all multiplier and score calculations
#   within a single function (_calculate_totals). This ensures the per-band
#   breakdown and the final totals are derived from the same robust
#   pivot_table logic, fixing the inconsistency bug.
## [0.43.0-Beta] - 2025-08-21
### Fixed
# - Replaced the flawed groupby().nunique() aggregation logic with a more
#   robust pivot_table() method to fix the multiplier overcount bug and
#   ensure consistency with the multiplier_summary report.
## [0.42.0-Beta] - 2025-08-21
### Added
# - Added logic to save the intermediate df_valid_mults DataFrame to a
#   CSV file when the --debug-mults flag is used.
## [0.41.0-Beta] - 2025-08-21
### Added
# - Added a temporary diagnostic log to print the source rows for the
#   40M SD multiplier to debug a counting inconsistency.
from typing import List, Dict, Set, Tuple
import pandas as pd
import os
import re
import json
import logging
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

            year = df_full['Date'].iloc[0].split('-')[0]
            
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

            report_content = "\n".join(report_lines) + "\n"
            os.makedirs(output_path, exist_ok=True)
            filename = f"{self.report_id}_{callsign}.txt"
            filepath = os.path.join(output_path, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            final_report_messages.append(f"Text report saved to: {filepath}")

        return "\n".join(final_report_messages)

    def _calculate_all_scores(self, log: ContestLog, output_path: str, **kwargs) -> Tuple[List[Dict], Dict, int]:
        df_full = log.get_processed_data()
        df_net = df_full[df_full['Dupe'] == False].copy()
        contest_def = log.contest_definition
        multiplier_rules = contest_def.multiplier_rules

        # --- Apply contest rule for multipliers from zero-point QSOs ---
        if not contest_def.mults_from_zero_point_qsos:
            df_net = df_net[df_net['QSOPoints'] > 0]

        # --- Authoritative Multiplier Calculation using Pivot Table ---
        band_mult_counts = {}
        for rule in multiplier_rules:
            mult_col = rule['value_column']
            if mult_col in df_net.columns:
                df_valid = df_net[df_net[mult_col].notna() & (df_net[mult_col] != 'Unknown')]
                pivot = calculate_multiplier_pivot(df_valid, mult_col, group_by_call=False)
                band_mult_counts[mult_col] = (pivot > 0).sum(axis=0)

        # --- Per-Band/Mode Summary Calculation (derived from correct data) ---
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
                    # Get the count for this band directly from the authoritative pivot results
                    band_counts_series = band_mult_counts.get(m_col)
                    if band_counts_series is not None:
                         band_mode_summary[m_name] = band_counts_series.get(band, 0)
                    else:
                         band_mode_summary[m_name] = 0

                band_mode_summary['AVG'] = (band_mode_summary['Points'] / band_mode_summary['QSOs']) if band_mode_summary['QSOs'] > 0 else 0
                summary_data.append(band_mode_summary)
                
        # --- TOTAL Summary Calculation (derived from correct data) ---
        total_summary = {'Band': 'TOTAL', 'Mode': ''}
        total_summary['QSOs'] = df_net.shape[0]
        total_summary['Points'] = df_net['QSOPoints'].sum()

        total_multiplier_count = 0
        for rule in multiplier_rules:
            mult_name = rule['name']
            
            band_mult_sum = band_mult_counts.get(rule['value_column'], pd.Series()).sum()
            total_summary[mult_name] = band_mult_sum
            total_multiplier_count += band_mult_sum
            
        total_summary['AVG'] = (total_summary['Points'] / total_summary['QSOs']) if total_summary['QSOs'] > 0 else 0
        
        # --- Data-driven score calculation ---
        if contest_def.score_formula == 'qsos_times_mults':
            final_score = total_summary['QSOs'] * total_multiplier_count
        else: # Default to points_times_mults
            final_score = total_summary['Points'] * total_multiplier_count
        
        return summary_data, total_summary, final_score