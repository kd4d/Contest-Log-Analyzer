# Contest Log Analyzer/contest_tools/reports/text_score_report.py
#
# Purpose: A text report that generates a detailed score summary for each
#          log, broken down by band.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-31
# Version: 0.22.0-Beta
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

## [0.22.0-Beta] - 2025-07-31
### Changed
# - Implemented the boolean support properties, correctly identifying this
#   report as 'single'.

## [0.21.13-Beta] - 2025-07-29
### Changed
# - "Unknown" country multipliers are now excluded from multiplier totals.
# - Added a diagnostic list of non-maritime mobile callsigns that resulted
#   in an "Unknown" country classification.

## [0.21.12-Beta] - 2025-07-29
### Fixed
# - Removed comma separators from all numeric fields in the report table,
#   except for the final score line, to improve readability.

## [0.21.11-Beta] - 2025-07-29
### Fixed
# - Corrected a ValueError in the dynamic column width calculation that
#   occurred when trying to apply numeric formatting to a string.

## [0.21.10-Beta] - 2025-07-29
### Changed
# - The report header now includes the year of the contest.
# - Column headers now use full names (e.g., "Countries", "Zones") instead
#   of abbreviations.
# - Column widths are now calculated dynamically to fit the data, improving
#   readability and alignment.

## [0.21.0-Beta] - 2025-07-29
# - Initial release of the Score Summary report.

from typing import List, Dict
import pandas as pd
import os
from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a detailed score summary report for each log.
    """
    supports_single = True
    
    @property
    def report_id(self) -> str:
        return "score_report"

    @property
    def report_name(self) -> str:
        return "Score Summary"

    @property
    def report_type(self) -> str:
        return "text"

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

            # --- Data-driven Multiplier Setup ---
            multiplier_rules = log.contest_definition.multiplier_rules
            mult_cols = [rule['value_column'] for rule in multiplier_rules]
            mult_names = [rule['name'] for rule in multiplier_rules]

            # --- Data Aggregation ---
            bands = ['160M', '80M', '40M', '20M', '15M', '10M']
            summary_data = []
            
            # --- Separate Unknowns for Diagnostics ---
            unknown_mult_callsigns = set()
            for m_col in mult_cols:
                unknown_df = df_full[(df_full[m_col] == 'Unknown') & (~df_full['Call'].str.endswith('/MM', na=False))]
                unknown_mult_callsigns.update(unknown_df['Call'].unique())

            for band in bands:
                band_df_full = df_full[df_full['Band'] == band]
                if band_df_full.empty:
                    continue
                
                band_df_net = band_df_full[band_df_full['Dupe'] == False]

                band_summary = {'Band': band.replace('M', '')}
                band_summary['QSOs'] = len(band_df_net)
                band_summary['Dupes'] = len(band_df_full) - len(band_df_net)
                band_summary['Points'] = band_df_net['QSOPoints'].sum()
                
                for i, m_col in enumerate(mult_cols):
                    # Exclude 'Unknown' from multiplier counts
                    band_summary[mult_names[i]] = band_df_net[band_df_net[m_col] != 'Unknown'][m_col].nunique()
                
                band_summary['AVG'] = (band_summary['Points'] / band_summary['QSOs']) if band_summary['QSOs'] > 0 else 0
                summary_data.append(band_summary)
            
            if not summary_data:
                msg = f"Skipping score report for {callsign}: No QSOs on primary contest bands."
                print(msg)
                final_report_messages.append(msg)
                continue

            # --- Calculate Totals ---
            total_summary = {'Band': 'TOTAL'}
            total_summary['QSOs'] = sum(item['QSOs'] for item in summary_data)
            total_summary['Dupes'] = sum(item['Dupes'] for item in summary_data)
            total_summary['Points'] = sum(item['Points'] for item in summary_data)
            for name in mult_names:
                total_summary[name] = sum(item[name] for item in summary_data)
            total_summary['AVG'] = (total_summary['Points'] / total_summary['QSOs']) if total_summary['QSOs'] > 0 else 0
            
            total_multiplier_count = sum(total_summary[name] for name in mult_names)
            final_score = total_summary['Points'] * total_multiplier_count

            # --- Dynamic Column Width Calculation ---
            all_data_for_width = summary_data + [total_summary]
            col_order = ['Band', 'QSOs'] + mult_names + ['Dupes', 'Points', 'AVG']
            col_widths = {key: len(str(key)) for key in col_order}

            for row in all_data_for_width:
                for key, value in row.items():
                    if isinstance(value, float):
                        val_len = len(f"{value:.2f}")
                    else:
                        val_len = len(str(value))
                    col_widths[key] = max(col_widths.get(key, 0), val_len)

            # --- Formatting ---
            year = df_full['Date'].iloc[0].split('-')[0]
            report_lines = []
            report_lines.append(f"Contest         : {year} {contest_name}")
            report_lines.append(f"Callsign        : {callsign}")
            report_lines.append("")
            
            header_parts = [f"{name:>{col_widths[name]}}" for name in col_order]
            header = "  ".join(header_parts)
            separator = "-" * len(header)
            
            report_lines.append(header)
            report_lines.append(separator)

            for item in summary_data:
                data_parts = [
                    f"{item['Band']:>{col_widths['Band']}}",
                    f"{item['QSOs']:>{col_widths['QSOs']}}",
                ]
                data_parts.extend([f"{item.get(name, 0):>{col_widths[name]}}" for name in mult_names])
                data_parts.extend([
                    f"{item['Dupes']:>{col_widths['Dupes']}}",
                    f"{item['Points']:>{col_widths['Points']}}",
                    f"{item['AVG']:>{col_widths['AVG']}.2f}"
                ])
                report_lines.append("  ".join(data_parts))

            report_lines.append(separator)
            
            total_parts = [
                f"{total_summary['Band']:>{col_widths['Band']}}",
                f"{total_summary['QSOs']:>{col_widths['QSOs']}}",
            ]
            total_parts.extend([f"{total_summary.get(name, 0):>{col_widths[name]}}" for name in mult_names])
            total_parts.extend([
                f"{total_summary['Dupes']:>{col_widths['Dupes']}}",
                f"{total_summary['Points']:>{col_widths['Points']}}",
                f"{total_summary['AVG']:>{col_widths['AVG']}.2f}"
            ])
            report_lines.append("  ".join(total_parts))
            
            report_lines.append("=" * len(header))
            report_lines.append(f"        TOTAL SCORE : {final_score:,.0f}")

            # --- Add Diagnostic List for Unknown Calls ---
            if unknown_mult_callsigns:
                report_lines.append("\n" + "-" * 40)
                report_lines.append("Callsigns with 'Unknown' Country Multiplier:")
                report_lines.append("(Excludes Maritime Mobile /MM stations)")
                report_lines.append("-" * 40)
                
                sorted_unknowns = sorted(list(unknown_mult_callsigns))
                col_width = 12
                num_cols = max(1, len(header) // (col_width + 2))
                
                for i in range(0, len(sorted_unknowns), num_cols):
                    line_calls = sorted_unknowns[i:i+num_cols]
                    report_lines.append("  ".join([f"{call:<{col_width}}" for call in line_calls]))

            # --- Save the Report File ---
            report_content = "\n".join(report_lines)
            os.makedirs(output_path, exist_ok=True)
            filename = f"{self.report_id}_{callsign}.txt"
            filepath = os.path.join(output_path, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            final_report_messages.append(f"Text report saved to: {filepath}")

        return "\n".join(final_report_messages)
