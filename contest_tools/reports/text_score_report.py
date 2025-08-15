# Contest Log Analyzer/contest_tools/reports/text_score_report.py
#
# Purpose: A text report that generates a detailed score summary for each
#          log, broken down by band.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-15
# Version: 0.36.1-Beta
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
## [0.36.1-Beta] - 2025-08-15
### Fixed
# - Refactored the `_calculate_totals` function to be data-driven, using
#   only the multiplier columns explicitly defined in the contest's JSON
#   file to prevent double-counting.
## [0.36.0-Beta] - 2025-08-15
### Fixed
# - Refactored the `_calculate_totals` function to be data-driven, using
#   only the multiplier columns explicitly defined in the contest's JSON
#   file to prevent double-counting.
## [0.35.0-Beta] - 2025-08-13
### Changed
# - Refactored score calculation to be data-driven, using the new
#   `score_formula` from the contest definition.
from typing import List, Dict, Set, Tuple
import pandas as pd
import os
import re
from ..contest_log import ContestLog
from ..contest_definitions import ContestDefinition
from .report_interface import ContestReport

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

            contest_def = log.contest_definition
            total_summary, final_score = self._calculate_totals(log)
            
            # --- Data Aggregation by Band and Mode ---
            summary_data = []
            df_net = df_full[df_full['Dupe'] == False].copy()
            
            if not df_net.empty:
                grouped = df_net.groupby(['Band', 'Mode'])
                for (band, mode), group_df in grouped:
                    band_mode_summary = {'Band': band, 'Mode': mode}
                    band_mode_summary['QSOs'] = len(group_df)
                    band_mode_summary['Points'] = group_df['QSOPoints'].sum()
                    
                    for rule in contest_def.multiplier_rules:
                        m_col = rule['value_column']
                        m_name = rule['name']
                        if m_col in group_df.columns:
                            band_mode_summary[m_name] = group_df[m_col].nunique()
                    
                    band_mode_summary['AVG'] = (band_mode_summary['Points'] / band_mode_summary['QSOs']) if band_mode_summary['QSOs'] > 0 else 0
                    summary_data.append(band_mode_summary)

            # --- Formatting ---
            mult_names = [rule['name'] for rule in contest_def.multiplier_rules]
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

            report_content = "\n".join(report_lines)
            os.makedirs(output_path, exist_ok=True)
            filename = f"{self.report_id}_{callsign}.txt"
            filepath = os.path.join(output_path, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            final_report_messages.append(f"Text report saved to: {filepath}")

        return "\n".join(final_report_messages)

    def _calculate_totals(self, log: ContestLog) -> Tuple[Dict, int]:
        df_full = log.get_processed_data()
        df_net = df_full[df_full['Dupe'] == False]
        contest_def = log.contest_definition
        multiplier_rules = contest_def.multiplier_rules

        total_summary = {'Band': 'TOTAL', 'Mode': ''}
        total_summary['QSOs'] = len(df_net)
        total_summary['Points'] = df_net['QSOPoints'].sum()

        total_multiplier_count = 0
        for rule in multiplier_rules:
            mult_name = rule['name']
            mult_col = rule['value_column']
            totaling_method = rule.get('totaling_method', 'sum_by_band')

            if mult_col not in df_net.columns:
                total_summary[mult_name] = 0
                continue

            df_valid_mults = df_net[df_net[mult_col].notna()]
            df_valid_mults = df_valid_mults[df_valid_mults[mult_col] != 'Unknown']

            if totaling_method == 'once_per_mode':
                mode_mults = df_valid_mults.groupby('Mode')[mult_col].nunique()
                total_summary[mult_name] = mode_mults.sum()
                total_multiplier_count += mode_mults.sum()
            elif totaling_method == 'once_per_log':
                unique_mults = df_valid_mults[mult_col].nunique()
                total_summary[mult_name] = unique_mults
                total_multiplier_count += unique_mults
            else: # Default to sum_by_band
                band_mults = df_valid_mults.groupby('Band')[mult_col].nunique()
                total_summary[mult_name] = band_mults.sum()
                total_multiplier_count += band_mults.sum()

        total_summary['AVG'] = (total_summary['Points'] / total_summary['QSOs']) if total_summary['QSOs'] > 0 else 0
        
        # --- Data-driven score calculation ---
        if contest_def.score_formula == 'qsos_times_mults':
            final_score = total_summary['QSOs'] * total_multiplier_count
        else: # Default to points_times_mults
            final_score = total_summary['Points'] * total_multiplier_count
        
        return total_summary, final_score