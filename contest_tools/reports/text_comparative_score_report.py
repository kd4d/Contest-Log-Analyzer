# Contest Log Analyzer/contest_tools/reports/text_comparative_score_report.py
#
# Purpose: A text report that generates an interleaved, comparative score
#          summary, broken down by band, for multiple logs.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-12
# Version: 0.32.12-Beta
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
## [0.32.12-Beta] - 2025-08-12
### Fixed
# - Added the missing `Tuple` to the `typing` import to resolve a NameError.
## [0.32.11-Beta] - 2025-08-12
### Changed
# - Refactored data aggregation to be mode-aware, grouping by both Band and Mode.
# - Added logic to _calculate_totals to correctly handle the "once_per_mode"
#   multiplier totaling method.
## [0.31.21-Beta] - 2025-08-09
### Fixed
# - Modified multiplier counting logic to explicitly exclude "Unknown" values.
## [0.28.30-Beta] - 2025-08-04
### Fixed
# - Corrected the `report_id` to its unique value, fixing the duplicate ID
#   warning and resolving downstream scoring and on-time calculation bugs.
## [0.28.29-Beta] - 2025-08-04
### Changed
# - Standardized report to have a two-line title followed by a blank line.
# - Reworked table generation to ensure column alignment is always correct.
# - The redundant per-band summary is now correctly hidden for single-band contests.

from typing import List, Set, Dict, Tuple
import pandas as pd
import os
from ..contest_log import ContestLog
from ..contest_definitions import ContestDefinition
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a comparative, interleaved score summary report.
    """
    report_id: str = "comparative_score_report"
    report_name: str = "Comparative Score Report"
    report_type: str = "text"
    supports_multi = True
    supports_pairwise = True
    
    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content.
        """
        all_calls = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in self.logs])
        first_log = self.logs[0]
        contest_def = first_log.contest_definition

        total_summaries = [self._calculate_totals(log) for log in self.logs]
        
        # --- Formatting ---
        mult_names = [rule['name'] for rule in contest_def.multiplier_rules]
        col_order = ['Callsign', 'On-Time', 'QSOs'] + mult_names + ['Points', 'AVG']

        col_widths = {key: len(str(key)) for key in col_order}
        col_widths['Callsign'] = max([len(call) for call in all_calls] + [len('Callsign')])
        
        has_on_time = any(s[0].get('On-Time') and s[0].get('On-Time') != 'N/A' for s in total_summaries)
        if not has_on_time:
            col_order.remove('On-Time')
            del col_widths['On-Time']

        for summary, _ in total_summaries:
             for key, value in summary.items():
                if key in col_widths:
                    val_len = len(f"{value:.2f}") if isinstance(value, float) else len(str(value))
                    col_widths[key] = max(col_widths.get(key, 0), val_len)

        header_parts = [f"{name:<{col_widths[name]}}" if name == 'Callsign' else f"{name:>{col_widths[name]}}" for name in col_order]
        table_header = "  ".join(header_parts)
        table_width = len(table_header)
        separator = "-" * table_width
        
        contest_name = first_log.get_metadata().get('ContestName', 'UnknownContest')
        year = first_log.get_processed_data()['Date'].iloc[0].split('-')[0] if not first_log.get_processed_data().empty else "----"
        
        title1 = f"--- {self.report_name} ---"
        title2 = f"{year} {contest_name} - {', '.join(all_calls)}"
        
        report_lines = []
        header_width = max(table_width, len(title1), len(title2))
        report_lines.append(title1.center(header_width))
        report_lines.append(title2.center(header_width))
        report_lines.append("")
        
        report_lines.append(table_header)
        report_lines.append(separator)
        
        # --- Data Aggregation by Band and Mode ---
        band_mode_summaries = {}
        for log in self.logs:
            call = log.get_metadata().get('MyCall', 'Unknown')
            df_net = log.get_processed_data()[log.get_processed_data()['Dupe'] == False]
            if not df_net.empty:
                grouped = df_net.groupby(['Band', 'Mode'])
                for (band, mode), group_df in grouped:
                    key = (band, mode)
                    if key not in band_mode_summaries:
                        band_mode_summaries[key] = []
                    
                    summary = self._calculate_band_mode_summary(group_df, call, contest_def.multiplier_rules)
                    band_mode_summaries[key].append(summary)

        # --- Report Generation ---
        canonical_band_order = [band[1] for band in ContestLog._HF_BANDS]
        sorted_keys = sorted(band_mode_summaries.keys(), key=lambda x: (canonical_band_order.index(x[0]), x[1]))

        for key in sorted_keys:
            band, mode = key
            report_lines.append(f"\n--- {band} {mode} ---")
            for summary in band_mode_summaries[key]:
                report_lines.append(self._format_row(summary, col_order, col_widths))

        report_lines.append("\n--- TOTAL ---")
        for summary, _ in total_summaries:
            report_lines.append(self._format_row(summary, col_order, col_widths))

        report_lines.append("=" * table_width)
        report_lines.append("")
        for summary, score in total_summaries:
            callsign = summary['Callsign']
            score_text = f"TOTAL SCORE ({callsign}) : {score:,.0f}"
            report_lines.append(score_text.rjust(table_width))

        report_content = "\n".join(report_lines)
        os.makedirs(output_path, exist_ok=True)
        filename_calls = '_vs_'.join(all_calls)
        filename = f"{self.report_id}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"

    def _format_row(self, data: dict, col_order: list, col_widths: dict) -> str:
        parts = []
        for name in col_order:
            align = "<" if name == 'Callsign' else ">"
            val = data.get(name, ' ')
            width = col_widths.get(name, len(str(val)))
            
            if isinstance(val, float):
                formatted_val = f"{val:{align}{width}.2f}"
            else:
                formatted_val = f"{str(val):{align}{width}}"
            parts.append(formatted_val)
        return "  ".join(parts)

    def _calculate_band_mode_summary(self, df_band_mode: pd.DataFrame, callsign: str, multiplier_rules: List) -> dict:
        summary = {'Callsign': callsign}
        summary['QSOs'] = len(df_band_mode)
        summary['Points'] = df_band_mode['QSOPoints'].sum()
        
        for rule in multiplier_rules:
            m_col = rule['value_column']
            m_name = rule['name']
            if m_col in df_band_mode.columns:
                summary[m_name] = df_band_mode[m_col].nunique()
        
        summary['AVG'] = (summary['Points'] / summary['QSOs']) if summary['QSOs'] > 0 else 0
        return summary

    def _calculate_totals(self, log: ContestLog) -> Tuple[Dict, int]:
        df_full = log.get_processed_data()
        df_net = df_full[df_full['Dupe'] == False]
        contest_def = log.contest_definition
        multiplier_rules = contest_def.multiplier_rules
        mult_names = [rule['name'] for rule in multiplier_rules]

        total_summary = {'Callsign': log.get_metadata().get('MyCall', 'Unknown')}
        total_summary['On-Time'] = log.get_metadata().get('OperatingTime')
        total_summary['QSOs'] = len(df_net)
        total_summary['Points'] = df_net['QSOPoints'].sum()

        total_multiplier_count = 0
        for i, rule in enumerate(multiplier_rules):
            mult_name = mult_names[i]
            mult_col = rule['value_column']
            totaling_method = rule.get('totaling_method', 'sum_by_band')

            if mult_col not in df_net.columns:
                total_summary[mult_name] = 0
                continue

            df_valid_mults = df_net[df_net[mult_col].notna()]

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
        final_score = total_summary['Points'] * total_multiplier_count
        
        return total_summary, final_score