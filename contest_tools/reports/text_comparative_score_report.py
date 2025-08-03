# Contest Log Analyzer/contest_tools/reports/text_comparative_score_report.py
#
# Purpose: A text report that generates an interleaved, comparative score
#          summary, broken down by band, for multiple logs.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-03
# Version: 0.28.24-Beta
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
## [0.28.24-Beta] - 2025-08-03
### Changed
# - Adjusted formatting in the TOTAL section: removed a separator line,
#   added a blank line before final scores, and right-justified the
#   final score lines to align with the table.
#
## [0.28.22-Beta] - 2025-08-03
### Added
# - The report now includes the final calculated score for each log at the
#   bottom of the TOTAL section.
#
## [0.28.14-Beta] - 2025-08-03
### Added
# - Initial release of the Comparative Score Report.
# - Report groups data by band and interleaves rows from each log.
# - Includes new diagnostic sections for Unknown DXCC and WPX prefixes.
from typing import List
import pandas as pd
import os
from ..contest_log import ContestLog
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

        multiplier_rules = first_log.contest_definition.multiplier_rules
        mult_cols = [rule['value_column'] for rule in multiplier_rules]
        mult_names = [rule['name'] for rule in multiplier_rules]

        col_order = ['Callsign', 'QSOs'] + mult_names + ['Dupes', 'Points', 'AVG']
        col_widths = {key: len(str(key)) for key in col_order}
        col_widths['Callsign'] = max([len(call) for call in all_calls] + [len('Callsign')])

        report_lines = []
        bands = ['160M', '80M', '40M', '20M', '15M', '10M']
        
        for band in bands:
            band_has_data = False
            band_lines = []
            
            for log in self.logs:
                df_full = log.get_processed_data()
                band_df_full = df_full[df_full['Band'] == band]
                if band_df_full.empty:
                    continue
                
                band_has_data = True
                band_df_net = band_df_full[band_df_full['Dupe'] == False]
                band_df_valid_mults = band_df_net[band_df_net['QSOPoints'] > 0] if not log.contest_definition.mults_from_zero_point_qsos else band_df_net

                band_summary = {'Callsign': log.get_metadata().get('MyCall', 'Unknown')}
                band_summary['QSOs'] = len(band_df_net)
                band_summary['Dupes'] = len(band_df_full) - len(band_df_net)
                band_summary['Points'] = band_df_net['QSOPoints'].sum()
                
                for i, m_col in enumerate(mult_cols):
                    if m_col in band_df_valid_mults.columns:
                        band_summary[mult_names[i]] = band_df_valid_mults[band_df_valid_mults[m_col] != 'Unknown'][m_col].nunique()
                
                band_summary['AVG'] = (band_summary['Points'] / band_summary['QSOs']) if band_summary['QSOs'] > 0 else 0
                
                for key, value in band_summary.items():
                    val_len = len(f"{value:.2f}") if isinstance(value, float) else len(str(value))
                    col_widths[key] = max(col_widths.get(key, 0), val_len)

                band_lines.append(band_summary)

            if band_has_data:
                report_lines.append(f"\n--- {band.replace('M', '')} Meters ---")
                for row_data in band_lines:
                    data_parts = [f"{row_data[name]:<{col_widths[name]}}" if name == 'Callsign' else f"{row_data.get(name, 0):>{col_widths[name]}}" if not isinstance(row_data.get(name), float) else f"{row_data.get(name, 0):>{col_widths[name]}.2f}" for name in col_order]
                    report_lines.append("  ".join(data_parts))

        header_parts = [f"{name:>{col_widths[name]}}" for name in col_order]
        header = "  ".join(header_parts)
        separator = "-" * len(header)
        
        report_lines.insert(0, header)
        report_lines.insert(1, separator)
        
        report_lines.append("\n--- TOTAL ---")
        
        total_summaries = [self._calculate_totals(log, mult_cols, mult_names) for log in self.logs]

        for summary in total_summaries:
            total_parts = [f"{summary[name]:<{col_widths[name]}}" if name == 'Callsign' else f"{summary.get(name, 0):>{col_widths[name]}}" if not isinstance(summary.get(name), float) else f"{summary.get(name, 0):>{col_widths[name]}.2f}" for name in col_order]
            report_lines.append("  ".join(total_parts))

        report_lines.append("=" * len(header))
        report_lines.append("") # Add blank line before scores
        for summary in total_summaries:
            callsign = summary['Callsign']
            score = summary['FinalScore']
            score_text = f"TOTAL SCORE ({callsign}) : {score:,.0f}"
            # Right-justify the score line to the width of the table header
            justified_score_line = score_text.rjust(len(header))
            report_lines.append(justified_score_line)

        self._add_diagnostic_sections(report_lines)

        report_content = "\n".join(report_lines)
        os.makedirs(output_path, exist_ok=True)
        filename_calls = '_vs_'.join(all_calls)
        filename = f"{self.report_id}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"

    def _calculate_totals(self, log: ContestLog, mult_cols: List[str], mult_names: List[str]) -> dict:
        df_full = log.get_processed_data()
        df_net = df_full[df_full['Dupe'] == False]
        df_valid_mults = df_net[df_net['QSOPoints'] > 0] if not log.contest_definition.mults_from_zero_point_qsos else df_net

        total_summary = {'Callsign': log.get_metadata().get('MyCall', 'Unknown')}
        total_summary['QSOs'] = len(df_net)
        total_summary['Dupes'] = df_full['Dupe'].sum()
        total_summary['Points'] = df_net['QSOPoints'].sum()

        total_multiplier_count = 0
        for i, rule in enumerate(log.contest_definition.multiplier_rules):
            mult_name = mult_names[i]
            mult_col = mult_cols[i]
            totaling_method = rule.get('totaling_method', 'sum_by_band')
            
            if mult_col not in df_valid_mults.columns:
                total_summary[mult_name] = 0
                continue

            if totaling_method == 'once_per_log':
                unique_mults = df_valid_mults[df_valid_mults[mult_col] != 'Unknown'][mult_col].nunique()
                total_summary[mult_name] = unique_mults
                total_multiplier_count += unique_mults
            else: # Default to sum_by_band
                band_mults = df_valid_mults[df_valid_mults[mult_col] != 'Unknown'].groupby('Band')[mult_col].nunique()
                total_summary[mult_name] = band_mults.sum()
                total_multiplier_count += total_summary[mult_name]

        total_summary['AVG'] = (total_summary['Points'] / total_summary['QSOs']) if total_summary['QSOs'] > 0 else 0
        total_summary['FinalScore'] = total_summary['Points'] * total_multiplier_count
        return total_summary

    def _add_diagnostic_sections(self, report_lines: List[str]):
        unknown_dxcc_calls = set()
        unknown_wpx_calls = set()

        for log in self.logs:
            df = log.get_processed_data()
            unknown_dxcc_df = df[df['DXCCPfx'] == 'Unknown']
            unknown_dxcc_calls.update(unknown_dxcc_df['Call'].unique())

            if 'Mult1' in df.columns:
                unknown_wpx_df = df[df['Mult1'] == 'Unknown']
                unknown_wpx_calls.update(unknown_wpx_df['Call'].unique())

        if unknown_dxcc_calls:
            report_lines.append("\n" + "-" * 40)
            report_lines.append("Callsigns with Unknown DXCC Prefix:")
            report_lines.append("-" * 40)
            col_width = 12
            sorted_calls = sorted(list(unknown_dxcc_calls))
            for i in range(0, len(sorted_calls), 5):
                line_calls = sorted_calls[i:i+5]
                report_lines.append("  ".join([f"{call:<{col_width}}" for call in line_calls]))

        if unknown_wpx_calls:
            report_lines.append("\n" + "-" * 40)
            report_lines.append("Callsigns with Unknown WPX Prefix (Mult1):")
            report_lines.append("-" * 40)
            col_width = 12
            sorted_calls = sorted(list(unknown_wpx_calls))
            for i in range(0, len(sorted_calls), 5):
                line_calls = sorted_calls[i:i+5]
                report_lines.append("  ".join([f"{call:<{col_width}}" for call in line_calls]))