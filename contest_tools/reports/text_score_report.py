# Contest Log Analyzer/contest_tools/reports/text_score_report.py
#
# Purpose: A text report that generates a detailed score summary for each
#          log, broken down by band.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-04
# Version: 0.28.28-Beta
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
## [0.28.28-Beta] - 2025-08-04
### Fixed
# - Corrected a hardcoded bug that caused DXCC multipliers to be ignored
#   in the final score calculation.
## [0.28.27-Beta] - 2025-08-04
### Changed
# - Standardized the report header to use a two-line title.
# - The redundant per-band breakdown is now correctly hidden for single-band contests.
from typing import List, Dict, Set
import pandas as pd
import os
import re
from ..contest_log import ContestLog
from ..contest_definitions import ContestDefinition
from .report_interface import ContestReport

def _load_all_multipliers_from_alias_file(alias_filename: str) -> Set[str]:
    """
    Parses a .dat alias file to extract the set of all official multiplier abbreviations.
    """
    all_mults = set()
    data_dir = os.environ.get('CONTEST_DATA_DIR').strip().strip('"').strip("'")
    filepath = os.path.join(data_dir, alias_filename)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split(':')
                if len(parts) != 2:
                    continue
                    
                official_part = parts[1]
                match = re.match(r'([A-Z]{2,3})\s+\(.*\)', official_part.strip())
                if match:
                    all_mults.add(match.group(1).upper())
    except FileNotFoundError:
        print(f"Warning: Alias file '{alias_filename}' not found. Cannot generate missed multiplier summary.")
    except Exception as e:
        print(f"Error reading alias file '{alias_filename}': {e}")
        
    return all_mults

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
                print(msg)
                final_report_messages.append(msg)
                continue

            contest_def = log.contest_definition
            location_type = log._my_location_type
            
            all_multiplier_rules = contest_def.multiplier_rules
            
            if location_type:
                multiplier_rules = [
                    rule for rule in all_multiplier_rules 
                    if rule.get('applies_to') == location_type
                ]
            else:
                multiplier_rules = all_multiplier_rules

            mult_cols = [rule['value_column'] for rule in multiplier_rules]
            mult_names = [rule['name'] for rule in multiplier_rules]

            bands = contest_def.valid_bands
            summary_data = []
            
            df_net_full = df_full[df_full['Dupe'] == False].copy()
            
            count_mults_from_zero_pt_qsos = contest_def.mults_from_zero_point_qsos

            for band in bands:
                band_df_full = df_full[df_full['Band'] == band]
                if band_df_full.empty:
                    continue
                
                band_df_net = band_df_full[band_df_full['Dupe'] == False]
                
                if not count_mults_from_zero_pt_qsos:
                    band_df_valid_mults = band_df_net[band_df_net['QSOPoints'] > 0]
                else:
                    band_df_valid_mults = band_df_net

                band_summary = {'Band': band.replace('M', '')}
                band_summary['QSOs'] = len(band_df_net)
                band_summary['Dupes'] = len(band_df_full) - len(band_df_net)
                band_summary['Points'] = band_df_net['QSOPoints'].sum()
                
                for i, m_col in enumerate(mult_cols):
                    if m_col in band_df_valid_mults.columns:
                        band_summary[mult_names[i]] = band_df_valid_mults[band_df_valid_mults[m_col].notna()][m_col].nunique()
                
                band_summary['AVG'] = (band_summary['Points'] / band_summary['QSOs']) if band_summary['QSOs'] > 0 else 0
                summary_data.append(band_summary)
            
            if not summary_data:
                msg = f"Skipping score report for {callsign}: No QSOs on primary contest bands."
                print(msg)
                final_report_messages.append(msg)
                continue

            total_summary = {'Band': 'TOTAL'}
            total_summary['QSOs'] = sum(item['QSOs'] for item in summary_data)
            total_summary['Dupes'] = sum(item['Dupes'] for item in summary_data)
            total_summary['Points'] = sum(item['Points'] for item in summary_data)
            
            total_multiplier_count = 0
            
            df_net_valid_mults = df_net_full[df_net_full['QSOPoints'] > 0] if not count_mults_from_zero_pt_qsos else df_net_full

            for i, rule in enumerate(multiplier_rules):
                mult_name = mult_names[i]
                mult_col = mult_cols[i]
                totaling_method = rule.get('totaling_method', 'sum_by_band')
                
                if mult_col not in df_net_valid_mults.columns:
                    total_summary[mult_name] = 0
                    continue

                if totaling_method == 'once_per_contest':
                    unique_mults = df_net_valid_mults[df_net_valid_mults[mult_col].notna()][mult_col].nunique()
                    total_summary[mult_name] = unique_mults
                    total_multiplier_count += unique_mults
                else: # Default to sum_by_band
                    total_summary[mult_name] = sum(item.get(mult_name, 0) for item in summary_data)
                    total_multiplier_count += total_summary[mult_name]

            total_summary['AVG'] = (total_summary['Points'] / total_summary['QSOs']) if total_summary['QSOs'] > 0 else 0
            final_score = total_summary['Points'] * total_multiplier_count

            all_data_for_width = summary_data + [total_summary]
            col_order = ['Band', 'QSOs'] + mult_names + ['Dupes', 'Points', 'AVG']
            col_widths = {key: len(str(key)) for key in col_order}

            for row in all_data_for_width:
                for key, value in row.items():
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
            if len(title1) > table_width or len(title2) > table_width:
                 report_lines.append(f"{title1.ljust(header_width)}")
                 report_lines.append(f"{title2.center(header_width)}")
            else:
                 report_lines.append(title1.center(header_width))
                 report_lines.append(title2.center(header_width))
            
            report_lines.append("")
            report_lines.append(f"Contest           : {contest_name}")
            report_lines.append(f"Callsign          : {callsign}")
            on_time_str = metadata.get('OperatingTime')
            if on_time_str:
                report_lines.append(f"Operating Time    : {on_time_str}")
            report_lines.append("")
            
            report_lines.append(header)
            report_lines.append(separator)

            if len(summary_data) > 1: # Only show per-band if more than one band
                for item in summary_data:
                    data_parts = [f"{item['Band']:>{col_widths['Band']}}", f"{item['QSOs']:>{col_widths['QSOs']}}"]
                    data_parts.extend([f"{item.get(name, 0):>{col_widths[name]}}" for name in mult_names])
                    data_parts.extend([
                        f"{item['Dupes']:>{col_widths['Dupes']}}",
                        f"{item['Points']:>{col_widths['Points']}}",
                        f"{item['AVG']:>{col_widths['AVG']}.2f}"
                    ])
                    report_lines.append("  ".join(data_parts))
                report_lines.append(separator)
            
            total_parts = [f"{total_summary['Band']:>{col_widths['Band']}}", f"{total_summary['QSOs']:>{col_widths['QSOs']}}"]
            total_parts.extend([f"{total_summary.get(name, 0):>{col_widths[name]}}" for name in mult_names])
            total_parts.extend([
                f"{total_summary['Dupes']:>{col_widths['Dupes']}}",
                f"{total_summary['Points']:>{col_widths['Points']}}",
                f"{total_summary['AVG']:>{col_widths['AVG']}.2f}"
            ])
            report_lines.append("  ".join(total_parts))
            
            report_lines.append("=" * table_width)
            score_text = f"TOTAL SCORE : {final_score:,.0f}"
            report_lines.append(score_text.rjust(table_width))


            self._add_diagnostic_sections(report_lines, contest_def)

            report_content = "\n".join(report_lines)
            os.makedirs(output_path, exist_ok=True)
            filename = f"{self.report_id}_{callsign}.txt"
            filepath = os.path.join(output_path, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            final_report_messages.append(f"Text report saved to: {filepath}")

        return "\n".join(final_report_messages)

    def _add_diagnostic_sections(self, report_lines: List[str], contest_def: ContestDefinition):
        """Appends sections for various unknown data points to the report."""
        df = self.logs[0].get_processed_data()

        # --- Check for Unknown DXCC Prefix ---
        unknown_dxcc_df = df[df['DXCCPfx'] == 'Unknown']
        unknown_dxcc_calls = sorted(list(unknown_dxcc_df['Call'].unique()))
        if unknown_dxcc_calls:
            report_lines.append("\n" + "-" * 40)
            report_lines.append("Callsigns with Unknown DXCC Prefix:")
            report_lines.append("-" * 40)
            col_width = 12
            for i in range(0, len(unknown_dxcc_calls), 5):
                line_calls = unknown_dxcc_calls[i:i+5]
                report_lines.append("  ".join([f"{call:<{col_width}}" for call in line_calls]))

        # --- Context-Aware Check for Unknown Multipliers (WPX Only) ---
        if 'CQ-WPX' in contest_def.contest_name:
            rule = next((r for r in contest_def.multiplier_rules if r.get('name') == 'Prefixes'), None)
            if rule:
                col = rule.get('value_column')
                if col and col in df.columns:
                    unknown_mult_df = df[df[col] == 'Unknown']
                    unknown_calls = sorted(list(unknown_mult_df['Call'].unique()))
                    
                    if unknown_calls:
                        report_lines.append("\n" + "-" * 40)
                        report_lines.append(f"Callsigns with Unknown {rule['name']} ({col}):")
                        report_lines.append("-" * 40)
                        col_width = 12
                        for i in range(0, len(unknown_calls), 5):
                            line_calls = unknown_calls[i:i+5]
                            report_lines.append("  ".join([f"{call:<{col_width}}" for call in line_calls]))