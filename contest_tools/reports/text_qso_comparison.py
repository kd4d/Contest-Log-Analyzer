# Contest Log Analyzer/contest_tools/reports/text_qso_comparison.py
#
# Purpose: A text report that generates a detailed pairwise comparison of QSO statistics.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-02
# Version: 0.26.1-Beta
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

## [0.26.1-Beta] - 2025-08-02
### Fixed
# - Converted report_id, report_name, and report_type from @property methods
#   to simple class attributes to fix a bug in the report generation loop.

## [0.22.0-Beta] - 2025-07-31
### Changed
# - Implemented the boolean support properties, correctly identifying this
#   report as 'pairwise'.

## [0.15.0-Beta] - 2025-07-25
# - Standardized version for final review. No functional changes.

## [0.14.5-Beta] - 2025-07-23
### Fixed
# - Corrected the underlying logic to use QSO counts for all metrics instead of
#   mixing QSO counts and multiplier counts. This ensures all totals and
#   sub-totals in the report are consistent and accurate.

## [0.14.4-Beta] - 2025-07-23
### Changed
# - Updated band titles to include "QSOs" (e.g., "160 Meter QSOs").
# - Split "Unique Run" and "Unique S&P" headers into two lines to narrow columns.
# - Removed redundant "QSOs" from the second line of column headers.

## [0.14.1-Beta] - 2025-07-23
### Changed
# - Reformatted the report to have callsigns as rows and metrics as columns,
#   with a two-line header for readability.

## [0.14.0-Beta] - 2025-07-23
### Changed
# - Updated the report to correctly handle and display the new "Unknown"
#   classification in all relevant metrics.

## [0.12.0-Beta] - 2025-07-23
# - Initial release of the QSO Comparison report (formerly Unique QSOs).

from typing import List, Dict, Any, Set
import pandas as pd
import os
from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a detailed pairwise comparison of QSO statistics, including
    breakdowns by Run/S&P/Unknown for total and unique QSOs.
    """
    report_id: str = "qso_comparison"
    report_name: str = "QSO Comparison Summary"
    report_type: str = "text"
    supports_pairwise = True

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content. This report always excludes dupes.

        Args:
            output_path (str): The directory where any output files should be saved.
            **kwargs: Accepts standard arguments but does not use them.
        """
        if len(self.logs) != 2:
            return "Error: The QSO Comparison report requires exactly two logs."

        log1, log2 = self.logs[0], self.logs[1]
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')

        # --- Dynamic Header Generation ---
        contest_name = log1.get_metadata().get('ContestName', 'UnknownContest')
        first_qso_date = log1.get_processed_data()['Date'].iloc[0]
        year = first_qso_date.split('-')[0] if first_qso_date else "UnknownYear"
        
        title_text = f"{year} {contest_name} QSO Comparison"
        
        report_lines = []

        bands = ['160M', '80M', '40M', '20M', '15M', '10M', 'All Bands']
        
        df1_full = log1.get_processed_data()[log1.get_processed_data()['Dupe'] == False]
        df2_full = log2.get_processed_data()[log2.get_processed_data()['Dupe'] == False]

        # --- Define Table Format ---
        headers1 = ["", "Total", "Run", "S&P", "Unk", "Unique", "Unique", "Unique", "Unique", "Common"]
        headers2 = ["Callsign", "", "", "", "", "", "Run", "S&P", "Unk", ""]
        col_widths = [12, 8, 8, 8, 8, 8, 8, 8, 8, 8]

        header1_str = "".join([f"{h:>{w}}" for h, w in zip(headers1, col_widths)])
        header2_str = "".join([f"{h:>{w}}" for h, w in zip(headers2, col_widths)])
        table_width = len(header1_str)
        
        final_report_lines = [
            f"- {title_text} -".center(table_width),
            "-" * table_width,
            ""
        ]

        for band in bands:
            band_header_text = f"{band.replace('M', '')} Meter QSOs" if band != "All Bands" else "All Band QSOs"
            report_lines.append(band_header_text.center(table_width))
            report_lines.append(header1_str)
            report_lines.append(header2_str)
            report_lines.append("-" * table_width)
            
            if band == 'All Bands':
                df1_band = df1_full
                df2_band = df2_full
            else:
                df1_band = df1_full[df1_full['Band'] == band]
                df2_band = df2_full[df2_full['Band'] == band]

            # --- Calculate Metrics for both logs ---
            for call, df_current, df_other in [(call1, df1_band, df2_band), (call2, df2_band, df1_band)]:
                calls_current_set = set(df_current['Call'].unique())
                calls_other_set = set(df_other['Call'].unique())

                common_calls_set = calls_current_set.intersection(calls_other_set)
                unique_to_current_set = calls_current_set.difference(calls_other_set)

                # --- Total QSO metrics ---
                total_qsos = len(df_current)
                run_total = (df_current['Run'] == 'Run').sum()
                sp_total = (df_current['Run'] == 'S&P').sum()
                unknown_total = (df_current['Run'] == 'Unknown').sum()

                # --- Unique QSO metrics ---
                df_unique = df_current[df_current['Call'].isin(unique_to_current_set)]
                unique_qsos_total = len(df_unique)
                run_unique = (df_unique['Run'] == 'Run').sum()
                sp_unique = (df_unique['Run'] == 'S&P').sum()
                unknown_unique = (df_unique['Run'] == 'Unknown').sum()

                # --- Common QSO metrics ---
                df_common = df_current[df_current['Call'].isin(common_calls_set)]
                common_qsos_total = len(df_common)
                
                # --- Format and Append Row ---
                row_str = (
                    f"{call:<{col_widths[0]}}"
                    f"{total_qsos:>{col_widths[1]}}"
                    f"{run_total:>{col_widths[2]}}"
                    f"{sp_total:>{col_widths[3]}}"
                    f"{unknown_total:>{col_widths[4]}}"
                    f"{unique_qsos_total:>{col_widths[5]}}"
                    f"{run_unique:>{col_widths[6]}}"
                    f"{sp_unique:>{col_widths[7]}}"
                    f"{unknown_unique:>{col_widths[8]}}"
                    f"{common_qsos_total:>{col_widths[9]}}"
                )
                report_lines.append(row_str)
            report_lines.append("")

        # --- Final Assembly and Save ---
        final_report_lines.extend(report_lines)
        report_content = "\n".join(final_report_lines)
        os.makedirs(output_path, exist_ok=True)
        
        filename_calls = f"{call1}_vs_{call2}"
        filename = f"{self.report_id}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"