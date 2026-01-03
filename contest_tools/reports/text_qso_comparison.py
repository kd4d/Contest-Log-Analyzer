# contest_tools/reports/text_qso_comparison.py
#
# Purpose: Generates a text-based report that provides a detailed pairwise
#          comparison of QSO counts (Total, Unique, Common) between two logs,
#          broken down by band and Run/S&P status.
#
# Author: Gemini AI
# Date: 2025-12-20
# Version: 0.134.0-Beta
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
# [0.134.0-Beta] - 2025-12-20
# - Standardized report header to use `_report_utils`.
# [0.90.1-Beta] - 2025-12-06
# Refactored report to show Run/S&P/Unknown breakdown for Common QSOs.
# Updated table layout with scoped super-headers.
#
# [0.90.0-Beta] - 2025-10-01
# Set new baseline version for release.

from .report_interface import ContestReport
from contest_tools.utils.report_utils import get_valid_dataframe, create_output_directory, format_text_header, get_cty_metadata, get_standard_title_lines
import pandas as pd
import os
from ..contest_log import ContestLog

class Report(ContestReport):
    report_id: str = "qso_comparison"
    report_name: str = "QSO Comparison Summary"
    report_type: str = "text"
    supports_single = False
    supports_pairwise = True
    supports_multi = False

    def generate(self, output_path: str, **kwargs) -> str:
        create_output_directory(output_path)
        include_dupes = kwargs.get('include_dupes', False)

        if len(self.logs) != 2:
            return f"Report '{self.report_name}' requires exactly two logs for pairwise comparison. Skipping."
        
        log1, log2 = self.logs[0], self.logs[1]
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')

        df1 = get_valid_dataframe(log1, include_dupes)
        df2 = get_valid_dataframe(log2, include_dupes)

        if df1.empty or df2.empty:
            return f"Skipping '{self.report_name}': At least one log has no valid QSOs."

        canonical_band_order = [band[1] for band in ContestLog._HAM_BANDS]
        all_bands_in_logs = pd.concat([df1['Band'], df2['Band']]).unique()
        bands = sorted(all_bands_in_logs, key=lambda b: canonical_band_order.index(b) if b in canonical_band_order else -1)
        
        # --- Header Generation ---
        table_width = 86
        modes_present = set(pd.concat([df1['Mode'], df2['Mode']]).dropna().unique())
        title_lines = get_standard_title_lines(self.report_name, self.logs, "All Bands", None, modes_present)
        meta_lines = ["Contest Log Analytics by KD4D", get_cty_metadata(self.logs)]
        
        report_lines = []
        report_lines.extend(format_text_header(table_width, title_lines, meta_lines))
        report_lines.append("="*86)
        
        # Initialize accumulators for the grand totals
        # Structure: [Total_QSO, Unique_Total, Common_Total]
        total_qso_1, total_unique_1, total_common_1 = 0, 0, 0
        total_qso_2, total_unique_2, total_common_2 = 0, 0, 0
        
        # Structure: [Run, S&P, Unk] for Unique
        total_run_unique_1, total_sp_unique_1, total_unk_unique_1 = 0, 0, 0
        total_run_unique_2, total_sp_unique_2, total_unk_unique_2 = 0, 0, 0
        
        # Structure: [Run, S&P, Unk] for Common
        total_run_common_1, total_sp_common_1, total_unk_common_1 = 0, 0, 0
        total_run_common_2, total_sp_common_2, total_unk_common_2 = 0, 0, 0

        # Helper to print the table header
        def append_table_header():
            report_lines.append(f"{'':9} {'TOTAL':>8} | {'UNIQUE (Breakdown)':^27} | {'COMMON (Breakdown)':^27}")
            report_lines.append(f"{'Call':<9} {'QSOs':>8} | {'Tot':>6} {'Run':>6} {'S&P':>6} {'Unk':>6} | {'Tot':>6} {'Run':>6} {'S&P':>6} {'Unk':>6}")
            report_lines.append(f"{'-'*9} {'-'*8} | {'-'*27} | {'-'*27}")

        def get_run_sp_unk_counts(df):
            run_count = (df['Run'] == 'Run').sum()
            sp_count = (df['Run'] == 'S&P').sum()
            unk_count = (df['Run'] == 'Unknown').sum()
            return run_count, sp_count, unk_count

        for band in bands:
            report_lines.append(f"\n--- {band} ---")
            append_table_header()
            
            c1_band = df1[df1['Band'] == band]
            c2_band = df2[df2['Band'] == band]

            calls1_band = set(c1_band['Call'])
            calls2_band = set(c2_band['Call'])
            
            # --- COMMON CALCULATION ---
            common_calls_on_band = calls1_band.intersection(calls2_band)
            
            # Dataframes for Common QSOs
            common_df_1 = c1_band[c1_band['Call'].isin(common_calls_on_band)]
            common_df_2 = c2_band[c2_band['Call'].isin(common_calls_on_band)]
            
            common_count_1 = len(common_df_1)
            common_count_2 = len(common_df_2)
            
            rc1, sc1, uc1 = get_run_sp_unk_counts(common_df_1)
            rc2, sc2, uc2 = get_run_sp_unk_counts(common_df_2)

            # --- UNIQUE CALCULATION ---
            total_count_1 = len(c1_band)
            total_count_2 = len(c2_band)
            
            unique_count_1 = total_count_1 - common_count_1
            unique_count_2 = total_count_2 - common_count_2

            unique_calls_for_1 = calls1_band - calls2_band
            unique_calls_for_2 = calls2_band - calls1_band
            
            # Dataframes for Unique QSOs
            u1_band = c1_band[c1_band['Call'].isin(unique_calls_for_1)]
            u2_band = c2_band[c2_band['Call'].isin(unique_calls_for_2)]

            ru1, su1, uu1 = get_run_sp_unk_counts(u1_band)
            ru2, su2, uu2 = get_run_sp_unk_counts(u2_band)
            
            # --- PRINT ROW ---
            # Call | Total | Unique(Tot, Run, SP, Unk) | Common(Tot, Run, SP, Unk)
            report_lines.append(f"{call1:<9} {total_count_1:>8} | {unique_count_1:>6} {ru1:>6} {su1:>6} {uu1:>6} | {common_count_1:>6} {rc1:>6} {sc1:>6} {uc1:>6}")
            report_lines.append(f"{call2:<9} {total_count_2:>8} | {unique_count_2:>6} {ru2:>6} {su2:>6} {uu2:>6} | {common_count_2:>6} {rc2:>6} {sc2:>6} {uc2:>6}")

            # --- ACCUMULATE TOTALS ---
            # Log 1
            total_qso_1 += total_count_1
            total_unique_1 += unique_count_1
            total_common_1 += common_count_1
            total_run_unique_1 += ru1
            total_sp_unique_1 += su1
            total_unk_unique_1 += uu1
            total_run_common_1 += rc1
            total_sp_common_1 += sc1
            total_unk_common_1 += uc1

            # Log 2
            total_qso_2 += total_count_2
            total_unique_2 += unique_count_2
            total_common_2 += common_count_2
            total_run_unique_2 += ru2
            total_sp_unique_2 += su2
            total_unk_unique_2 += uu2
            total_run_common_2 += rc2
            total_sp_common_2 += sc2
            total_unk_common_2 += uc2
        
        # --- TOTALS Section ---
        report_lines.append("\n" + "="*86 + "\n--- GRAND TOTALS ---")
        append_table_header()
        
        report_lines.append(f"{call1:<9} {total_qso_1:>8} | {total_unique_1:>6} {total_run_unique_1:>6} {total_sp_unique_1:>6} {total_unk_unique_1:>6} | {total_common_1:>6} {total_run_common_1:>6} {total_sp_common_1:>6} {total_unk_common_1:>6}")
        report_lines.append(f"{call2:<9} {total_qso_2:>8} | {total_unique_2:>6} {total_run_unique_2:>6} {total_sp_unique_2:>6} {total_unk_unique_2:>6} | {total_common_2:>6} {total_run_common_2:>6} {total_sp_common_2:>6} {total_unk_common_2:>6}")
        
        # Save to file
        output_filename = os.path.join(output_path, f"{self.report_id}_{call1}_vs_{call2}.txt")
        try:
            with open(output_filename, 'w') as f:
                f.write("\n".join(report_lines) + "\n")
            return f"'{self.report_name}' saved to {output_filename}"
        except Exception as e:
            return f"Error generating report '{self.report_name}': {e}"