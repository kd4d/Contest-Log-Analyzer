# Contest Log Analyzer/contest_tools/reports/text_score_report.py
#
# Purpose: A text report that generates a detailed score summary for each
#          log, broken down by band.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-03
# Version: 0.28.23-Beta
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
## [0.28.23-Beta] - 2025-08-03
### Fixed
# - Changed the `report_id` from "summary" to "score_report" to resolve
#   a conflict with the `text_summary.py` report.
#
## [0.28.16-Beta] - 2025-08-03
### Added
# - Added new diagnostic sections to the end of the report for callsigns
#   with Unknown DXCC and WPX prefixes.
#
## [0.26.1-Beta] - 2025-08-02
### Fixed
# - Converted report_id, report_name, and report_type from @property methods
#   to simple class attributes to fix a bug in the report generation loop.
## [0.26.0-Beta] - 2025-08-02
### Added
# - The report now generates a summary of unworked multipliers if the
#   'include_missed_summary' flag is set in the contest definition.
from typing import List, Dict, Set
import pandas as pd
import os
import re
from ..contest_log import ContestLog
from ..core_annotations import CtyLookup
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

            location_type = None
            if "ARRL-DX" in contest_name.upper():
                data_dir = os.environ.get('CONTEST_DATA_DIR').strip().strip('"').strip("'")
                cty_dat_path = os.path.join(data_dir, 'cty.dat')
                cty_lookup = CtyLookup(cty_dat_path=cty_dat_path)
                info = cty_lookup.get_cty(callsign)
                location_type = "W/VE" if info.name in ["United States", "Canada"] else "DX"

            all_multiplier_rules = log.contest_definition.multiplier_rules
            
            if location_type:
                multiplier_rules = [
                    rule for rule in all_multiplier_rules 
                    if rule.get('applies_to') == location_type
                ]
            else:
                multiplier_rules = all_multiplier_rules

            mult_cols = [rule['value_column'] for rule in multiplier_rules]
            mult_names = [rule['name'] for rule in multiplier_rules]

            bands = ['160M', '80M', '40M', '20M', '15M', '10M']
            summary_data = []
            
            df_net_full = df_full[df_full['Dupe'] == False].copy()
            
            count_mults_from_zero_pt_qsos = log.contest_definition.mults_from_zero_point_qsos

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
                        band_summary[mult_names[i]] = band_df_valid_mults[band_df_valid_mults[m_col] != 'Unknown'][m_col].nunique()
                
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

                if totaling_method == 'once_per_log':
                    unique_mults = df_net_valid_mults[df_net_valid_mults[mult_col] != 'Unknown'][mult_col].nunique()
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
            report_lines = []
            report_lines.append(f"Contest           : {year} {contest_name}")
            report_lines.append(f"Callsign          : {callsign}")
            report_lines.append("")
            
            header_parts = [f"{name:>{col_widths[name]}}" for name in col_order]
            header = "  ".join(header_parts)
            separator = "-" * len(header)
            
            report_lines.append(header)
            report_lines.append(separator)

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
            
            report_lines.append("=" * len(header))
            report_lines.append(f"                TOTAL SCORE : {final_score:,.0f}")

            for rule in multiplier_rules:
                if rule.get('include_missed_summary') and 'alias_file' in rule:
                    mult_col = rule['value_column']
                    all_possible_mults = _load_all_multipliers_from_alias_file(rule['alias_file'])
                    worked_mults = set(df_net_valid_mults[df_net_valid_mults[mult_col] != 'Unknown'][mult_col].unique())
                    missed_mults = sorted(list(all_possible_mults - worked_mults))
                    
                    if missed_mults:
                        report_lines.append("\n" + "-" * 40)
                        report_lines.append(f"Unworked {rule['name']}:")
                        report_lines.append("-" * 40)
                        
                        col_width = 8
                        num_cols = max(1, len(header) // (col_width + 2))
                        
                        for i in range(0, len(missed_mults), num_cols):
                            line_mults = missed_mults[i:i+num_cols]
                            report_lines.append("  ".join([f"{mult:<{col_width}}" for mult in line_mults]))

            self._add_diagnostic_sections(report_lines)

            report_content = "\n".join(report_lines)
            os.makedirs(output_path, exist_ok=True)
            filename = f"{self.report_id}_{callsign}.txt"
            filepath = os.path.join(output_path, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            final_report_messages.append(f"Text report saved to: {filepath}")

        return "\n".join(final_report_messages)

    def _add_diagnostic_sections(self, report_lines: List[str]):
        """Appends sections for Unknown DXCC and WPX prefixes to the report."""
        log = self.logs[0]
        df = log.get_processed_data()

        unknown_dxcc_calls = sorted(list(df[df['DXCCPfx'] == 'Unknown']['Call'].unique()))
        
        unknown_wpx_calls = []
        if 'Mult1' in df.columns:
            unknown_wpx_calls = sorted(list(df[df['Mult1'] == 'Unknown']['Call'].unique()))

        if unknown_dxcc_calls:
            report_lines.append("\n" + "-" * 40)
            report_lines.append("Callsigns with Unknown DXCC Prefix:")
            report_lines.append("-" * 40)
            col_width = 12
            for i in range(0, len(unknown_dxcc_calls), 5):
                line_calls = unknown_dxcc_calls[i:i+5]
                report_lines.append("  ".join([f"{call:<{col_width}}" for call in line_calls]))

        if unknown_wpx_calls:
            report_lines.append("\n" + "-" * 40)
            report_lines.append("Callsigns with Unknown WPX Prefix (Mult1):")
            report_lines.append("-" * 40)
            col_width = 12
            for i in range(0, len(unknown_wpx_calls), 5):
                line_calls = unknown_wpx_calls[i:i+5]
                report_lines.append("  ".join([f"{call:<{col_width}}" for call in line_calls]))