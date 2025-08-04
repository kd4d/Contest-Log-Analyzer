# Contest Log Analyzer/contest_tools/reports/text_qso_comparison.py
#
# Purpose: A text report that generates a detailed pairwise comparison of QSO statistics.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-04
# Version: 0.26.3-Beta
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
## [0.26.3-Beta] - 2025-08-04
### Changed
# - Standardized the report header to use a two-line title.
## [0.26.2-Beta] - 2025-08-03
### Changed
# - The report now uses the dynamic `valid_bands` list from the contest
#   definition instead of a hardcoded list.
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

        # --- Define Table Format ---
        headers1 = ["", "Total", "Run", "S&P", "Unk", "Unique", "Unique", "Unique", "Unique", "Common"]
        headers2 = ["Callsign", "", "", "", "", "", "Run", "S&P", "Unk", ""]
        col_widths = [12, 8, 8, 8, 8, 8, 8, 8, 8, 8]
        header1_str = "".join([f"{h:>{w}}" for h, w in zip(headers1, col_widths)])
        header2_str = "".join([f"{h:>{w}}" for h, w in zip(headers2, col_widths)])
        table_width = len(header1_str)
        
        # --- Dynamic Header Generation ---
        contest_name = log1.get_metadata().get('ContestName', 'UnknownContest')
        year = log1.get_processed_data()['Date'].iloc[0].split('-')[0] if not log1.get_processed_data().empty else "----"
        subtitle = f"{year} {contest_name} - {call1} vs {call2}"
        
        final_report_lines = [
            f"--- {self.report_name} ---".center(table_width),
            subtitle.center(table_width),
            ""
        ]

        bands = self.logs[0].contest_definition.valid_bands + ['All Bands']
        
        df1_full = log1.get_processed_data()[log1.get_processed_data()['Dupe'] == False]
        df2_full = log2.get_processed_data()[log2.get_processed_data()['Dupe'] == False]

        for band in bands:
            band_header_text = f"{band.replace('M', '')} Meter QSOs" if band != "All Bands" else "All Band QSOs"
            final_report_lines.append(band_header_text.center(table_width))
            final_report_lines.append(header1_str)
            final_report_lines.append(header2_str)
            final_report_lines.append("-" * table_width)
            
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

                total_qsos = len(df_current)
                run_total = (df_current['Run'] == 'Run').sum()
                sp_total = (df_current['Run'] == 'S&P').sum()
                unknown_total = (df_current['Run'] == 'Unknown').sum()

                df_unique = df_current[df_current['Call'].isin(unique_to_current_set)]
                unique_qsos_total = len(df_unique)
                run_unique = (df_unique['Run'] == 'Run').sum()
                sp_unique = (df_unique['Run'] == 'S&P').sum()
                unknown_unique = (df_unique['Run'] == 'Unknown').sum()

                df_common = df_current[df_current['Call'].isin(common_calls_set)]
                common_qsos_total = len(df_common)
                
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
                final_report_lines.append(row_str)
            final_report_lines.append("")

        # --- Final Assembly and Save ---
        report_content = "\n".join(final_report_lines)
        os.makedirs(output_path, exist_ok=True)
        
        filename_calls = f"{call1}_vs_{call2}"
        filename = f"{self.report_id}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"