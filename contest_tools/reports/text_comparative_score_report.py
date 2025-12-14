# contest_tools/reports/text_comparative_score_report.py
#
# Purpose: A text report that generates an interleaved, comparative score
#          summary, broken down by band, for multiple logs.
#          This version
#          serves as a proof-of-concept for using the tabulate library.
#
# Author: Gemini AI
# Date: 2025-10-09
# Version: 0.113.0-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0.
# If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# --- Revision History ---
# [0.113.0-Beta] - 2025-12-13
# - Standardized filename generation: removed '_vs_' separator and applied strict sanitization to callsigns.
# [0.91.0-Beta] - 2025-10-09
# - Added support for the 'once_per_band_no_mode' multiplier totaling
#   method to correctly calculate WRTC scores.
# [0.90.3-Beta] - 2025-10-05
# - Corrected scoring logic to sum the `QSOPoints` column instead of
#   counting all non-dupe QSOs, bringing it into alignment with the
#   correct logic in `wae_calculator.py`.
# [0.90.0-Beta] - 2025-10-01
# - Set new baseline version for release.

from typing import List, Set, Dict, Tuple
import pandas as pd
import os
from tabulate import tabulate
from ..contest_log import ContestLog
from ..contest_definitions import ContestDefinition
from .report_interface import ContestReport
from ._report_utils import _sanitize_filename_part

class Report(ContestReport):
    """
    Generates a comparative, interleaved score summary report (tabulate version).
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
        
        # --- Define Column Order and Header Formatting ---
        if contest_def.score_formula == 'total_points':
            mult_names = []
        else:
            mult_names = [rule['name'] for rule in contest_def.multiplier_rules]
            
        col_order = ['Callsign', 'On-Time', 'QSOs'] + mult_names + ['Points', 'AVG']

        has_on_time = any(s[0].get('On-Time') and s[0].get('On-Time') != 'N/A' for s in total_summaries)
        if not has_on_time:
            col_order.remove('On-Time')
        
        header_map = {col: col.replace(' ', '\n') for col in col_order}

        # --- Report Lines List ---
        report_lines = []
        
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
                    
                    summary = self._calculate_band_mode_summary(group_df, call, contest_def.multiplier_rules, log)
                    band_mode_summaries[key].append(summary)

        # --- Report Generation using tabulate ---
        canonical_band_order = [band[1] for band in ContestLog._HAM_BANDS]
        sorted_keys = sorted(band_mode_summaries.keys(), key=lambda x: (canonical_band_order.index(x[0]), x[1]))

        for key in sorted_keys:
            band, mode = key
            report_lines.append(f"\n--- {band} {mode} ---")
            
            summary_df = pd.DataFrame(band_mode_summaries[key])
            summary_df = summary_df.reindex(columns=col_order)
            
            if 'On-Time' in summary_df.columns:
                summary_df['On-Time'] = summary_df['On-Time'].fillna('')

            summary_df.rename(columns=header_map, inplace=True)
            table_string = tabulate(summary_df, headers='keys', tablefmt='psql', floatfmt=".2f", showindex="never")
            report_lines.append(table_string)

        report_lines.append("\n--- TOTAL ---")
        
        total_summary_list = [s[0] for s in total_summaries]
        total_df = pd.DataFrame(total_summary_list)
        total_df = total_df.reindex(columns=col_order)
        total_df.rename(columns=header_map, inplace=True)
        
        total_table_string = tabulate(total_df, headers='keys', tablefmt='psql', floatfmt=".2f", showindex="never")
        report_lines.append(total_table_string)
        
        table_width = len(total_table_string.split('\n')[0])
        report_lines.append("=" * table_width)
        report_lines.append("")
        
        # --- Final Score Formatting with Aligned Colons and Scores ---
        score_labels = [f"TOTAL SCORE ({s[0]['Callsign']})" for s in total_summaries]
        score_values = [f"{s[1]:,.0f}" for s in total_summaries]
        
        max_label_width = max(len(label) for label in score_labels) if score_labels else 0
        max_score_width = max(len(value) for value in score_values) if score_values else 0

        for i in range(len(total_summaries)):
            label = score_labels[i]
            score_str = score_values[i]
            
            padded_label = f"{label:>{max_label_width}}"
            padded_score = f"{score_str:>{max_score_width}}"
            
            line = f"{padded_label} : {padded_score}"
            
            padding = table_width - len(line)
            final_line = " " * padding + line
            report_lines.append(final_line)

        # --- Prepend Centered Titles ---
        contest_name = first_log.get_metadata().get('ContestName', 'UnknownContest')
        year = first_log.get_processed_data()['Date'].iloc[0].split('-')[0] if not first_log.get_processed_data().empty else "----"
        
        title1 = f"--- {self.report_name} ---"
        title2 = f"{year} {contest_name} - {', '.join(all_calls)}"
        
        header_width = max(table_width, len(title1), len(title2))
        final_header = [
            title1.center(header_width),
            title2.center(header_width),
            ""
        ]
        report_lines = final_header + report_lines

        # --- Save to File ---
        report_content = "\n".join(report_lines) + "\n"
        os.makedirs(output_path, exist_ok=True)
        filename_calls = '_'.join([_sanitize_filename_part(c) for c in sorted(all_calls)])
        filename = f"{self.report_id}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"

    def _calculate_band_mode_summary(self, df_band_mode: pd.DataFrame, callsign: str, multiplier_rules: List, log: ContestLog) -> dict:
        summary = {'Callsign': callsign}
        summary['QSOs'] = len(df_band_mode)
        summary['Points'] = df_band_mode['QSOPoints'].sum()
        
        log_location_type = getattr(log, '_my_location_type', None)
        
        for rule in multiplier_rules:
            m_col = rule['value_column']
            m_name = rule['name']

            applies_to = rule.get('applies_to')
            if applies_to and log_location_type and applies_to != log_location_type:
                summary[m_name] = 0
                continue
            
            if m_col in df_band_mode.columns:
                summary[m_name] = df_band_mode[m_col].nunique()
            else:
                summary[m_name] = 0
        
        summary['AVG'] = (summary['Points'] / summary['QSOs']) if summary['QSOs'] > 0 else 0
        return summary

    def _calculate_totals(self, log: ContestLog) -> Tuple[Dict, int]:
        df_full = log.get_processed_data()
        df_net = df_full[df_full['Dupe'] == False]
        contest_def = log.contest_definition
        multiplier_rules = contest_def.multiplier_rules
        mult_names = [rule['name'] for rule in multiplier_rules]
        log_location_type = getattr(log, '_my_location_type', None)

        total_summary = {'Callsign': log.get_metadata().get('MyCall', 'Unknown')}
        total_summary['On-Time'] = log.get_metadata().get('OperatingTime')
        total_summary['QSOs'] = len(df_net)
        total_summary['Points'] = df_net['QSOPoints'].sum()

        total_multiplier_count = 0
        for i, rule in enumerate(multiplier_rules):
            mult_name = mult_names[i]
            mult_col = rule['value_column']
            
            applies_to = rule.get('applies_to')
            if applies_to and log_location_type and applies_to != log_location_type:
                total_summary[mult_name] = 0
                continue
            
            totaling_method = rule.get('totaling_method', 'sum_by_band')

            if mult_col not in df_net.columns:
                total_summary[mult_name] = 0
                continue

            df_valid_mults = df_net[df_net[mult_col].notna()]

            if totaling_method == 'once_per_log':
                unique_mults = df_valid_mults[mult_col].nunique()
                total_summary[mult_name] = unique_mults
                total_multiplier_count += unique_mults
            elif totaling_method == 'once_per_mode':
                mode_mults = df_valid_mults.groupby('Mode')[mult_col].nunique()
                total_summary[mult_name] = mode_mults.sum()
                total_multiplier_count += mode_mults.sum()
            elif totaling_method == 'once_per_band_no_mode':
                band_mults = df_valid_mults.groupby('Band')[mult_col].nunique()
                total_summary[mult_name] = band_mults.sum()
                total_multiplier_count += band_mults.sum()
            else: # Default to sum_by_band
                band_mults = df_valid_mults.groupby('Band')[mult_col].nunique()
                total_summary[mult_name] = band_mults.sum()
                total_multiplier_count += band_mults.sum()
        
        total_summary['AVG'] = (total_summary['Points'] / total_summary['QSOs']) if total_summary['QSOs'] > 0 else 0
        
        if contest_def.score_formula == 'qsos_times_mults':
            final_score = total_summary['QSOs'] * total_multiplier_count
        elif contest_def.score_formula == 'total_points':
            final_score = total_summary['Points']
        else: # Default to points_times_mults
            final_score = total_summary['Points'] * total_multiplier_count
        
        return total_summary, final_score