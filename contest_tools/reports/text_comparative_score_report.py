# Contest Log Analyzer/contest_tools/reports/text_comparative_score_report.py
#
# Purpose: A text report that generates an interleaved, comparative score
#          summary, broken down by band, for multiple logs.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-04
# Version: 0.28.29-Beta
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
## [0.28.29-Beta] - 2025-08-04
### Changed
# - Standardized report to have a two-line title followed by a blank line.
# - Reworked table generation to ensure column alignment is always correct.
## [0.28.28-Beta] - 2025-08-03
### Changed
# - Added a second, descriptive title line to the report header.
# - Fixed column alignment by creating a single, unified table structure that
#   includes the On-Time column in the main header.
from typing import List, Set
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

        multiplier_rules = contest_def.multiplier_rules
        mult_names = [rule['name'] for rule in multiplier_rules]
        mult_cols = [rule['value_column'] for rule in multiplier_rules]

        # --- Define the full column order for the entire report ---
        col_order = ['Callsign', 'On-Time', 'QSOs'] + mult_names + ['Dupes', 'Points', 'AVG']

        # --- Pre-calculate all column widths based on totals ---
        total_summaries = [self._calculate_totals(log, mult_cols, mult_names) for log in self.logs]
        col_widths = {key: len(str(key)) for key in col_order}
        col_widths['Callsign'] = max([len(call) for call in all_calls] + [len('Callsign')])
        
        has_on_time = any(s.get('OperatingTime') and s.get('OperatingTime') != 'N/A' for s in total_summaries)
        if has_on_time:
             col_widths['On-Time'] = max(len('On-Time'), max(len(s.get('OperatingTime', '')) for s in total_summaries))
        else:
            col_widths['On-Time'] = 0 # Hide column if no on-time data

        for summary in total_summaries:
             for key, value in summary.items():
                if key in col_widths:
                    val_len = len(f"{value:.2f}") if isinstance(value, float) else len(str(value))
                    col_widths[key] = max(col_widths.get(key, 0), val_len)

        # --- Assemble Final Report ---
        header_parts = [f"{name:<{col_widths[name]}}" if name == 'Callsign' else f"{name:>{col_widths[name]}}" for name in col_order if col_widths.get(name, 0) > 0]
        header = "  ".join(header_parts)
        separator = "-" * len(header)
        
        contest_name = first_log.get_metadata().get('ContestName', 'UnknownContest')
        year = first_log.get_processed_data()['Date'].iloc[0].split('-')[0] if not first_log.get_processed_data().empty else "----"
        subtitle = f"{year} {contest_name} - {', '.join(all_calls)}"

        report_lines = []
        report_lines.append(f"--- {self.report_name} ---".center(len(header)))
        report_lines.append(subtitle.center(len(header)))
        report_lines.append("") # Blank line after titles
        report_lines.append(header)
        report_lines.append(separator)
        
        # --- Generate and add Per-Band Data ---
        bands = contest_def.valid_bands
        bands_with_data = [band for band in bands if any(not log.get_processed_data()[log.get_processed_data()['Band'] == band].empty for log in self.logs)]
        
        if len(bands_with_data) > 1:
            for band in bands_with_data:
                report_lines.append(f"\n--- {band.replace('M', '')} Meters ---")
                for log in self.logs:
                    band_summary = self._calculate_band_summary(log, band, mult_cols, mult_names)
                    report_lines.append(self._format_row(band_summary, col_order, col_widths))

        # --- TOTAL Section ---
        report_lines.append("\n--- TOTAL ---")
        for summary in total_summaries:
            report_lines.append(self._format_row(summary, col_order, col_widths))

        report_lines.append("=" * len(header))
        report_lines.append("")
        for summary in total_summaries:
            callsign = summary['Callsign']
            score = summary['FinalScore']
            score_text = f"TOTAL SCORE ({callsign}) : {score:,.0f}"
            justified_score_line = score_text.rjust(len(header))
            report_lines.append(justified_score_line)

        self._add_diagnostic_sections(report_lines, contest_def)

        report_content = "\n".join(report_lines)
        os.makedirs(output_path, exist_ok=True)
        filename_calls = '_vs_'.join(all_calls)
        filename = f"{self.report_id}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"

    def _format_row(self, data: dict, col_order: list, col_widths: dict) -> str:
        """Formats a single data row for the report table."""
        parts = []
        for name in col_order:
            if col_widths.get(name, 0) == 0:
                continue
            
            align = "<" if name == 'Callsign' else ">"
            val = data.get(name, ' ')
            width = col_widths.get(name, len(str(val)))
            
            if isinstance(val, float):
                formatted_val = f"{val:{align}{width}.2f}"
            else:
                formatted_val = f"{str(val):{align}{width}}"
            parts.append(formatted_val)
        return "  ".join(parts)

    def _calculate_band_summary(self, log: ContestLog, band: str, mult_cols: List[str], mult_names: List[str]) -> dict:
        df_full = log.get_processed_data()
        band_df_full = df_full[df_full['Band'] == band]
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
        return band_summary

    def _calculate_totals(self, log: ContestLog, mult_cols: List[str], mult_names: List[str]) -> dict:
        df_full = log.get_processed_data()
        df_net = df_full[df_full['Dupe'] == False]
        df_valid_mults = df_net[df_net['QSOPoints'] > 0] if not log.contest_definition.mults_from_zero_point_qsos else df_net

        total_summary = {'Callsign': log.get_metadata().get('MyCall', 'Unknown')}
        total_summary['On-Time'] = log.get_metadata().get('OperatingTime')
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

            if totaling_method == 'once_per_contest':
                unique_mults = df_valid_mults[df_valid_mults[mult_col] != 'Unknown'][mult_col].nunique()
                total_summary[mult_name] = unique_mults
                total_multiplier_count += unique_mults
            else: # Default to sum_by_band
                band_mults = df_valid_mults[df_valid_mults[mult_col] != 'Unknown'].groupby('Band')['Mult1'].nunique()
                total_summary[mult_name] = band_mults.sum()
                total_multiplier_count += total_summary[mult_name]

        total_summary['AVG'] = (total_summary['Points'] / total_summary['QSOs']) if total_summary['QSOs'] > 0 else 0
        total_summary['FinalScore'] = total_summary['Points'] * total_multiplier_count
        return total_summary

    def _add_diagnostic_sections(self, report_lines: List[str], contest_def: ContestDefinition):
        combined_df = pd.concat([log.get_processed_data() for log in self.logs])
        if combined_df.empty:
            return

        unknown_dxcc_df = combined_df[combined_df['DXCCPfx'] == 'Unknown']
        unknown_dxcc_calls = sorted(list(unknown_dxcc_df['Call'].unique()))
        if unknown_dxcc_calls:
            report_lines.append("\n" + "-" * 40)
            report_lines.append("Callsigns with Unknown DXCC Prefix:")
            report_lines.append("-" * 40)
            col_width = 12
            for i in range(0, len(unknown_dxcc_calls), 5):
                line_calls = unknown_dxcc_calls[i:i+5]
                report_lines.append("  ".join([f"{call:<{col_width}}" for call in line_calls]))

        if 'CQ-WPX' in contest_def.contest_name:
            rule = next((r for r in contest_def.multiplier_rules if r.get('name') == 'Prefixes'), None)
            if rule:
                col = rule.get('value_column')
                if col and col in combined_df.columns:
                    unknown_mult_df = combined_df[combined_df[col] == 'Unknown']
                    unknown_calls = sorted(list(unknown_mult_df['Call'].unique()))
                    
                    if unknown_calls:
                        report_lines.append("\n" + "-" * 40)
                        report_lines.append(f"Callsigns with Unknown {rule['name']} ({col}):")
                        report_lines.append("-" * 40)
                        col_width = 12
                        for i in range(0, len(unknown_calls), 5):
                            line_calls = unknown_calls[i:i+5]
                            report_lines.append("  ".join([f"{call:<{col_width}}" for call in line_calls]))