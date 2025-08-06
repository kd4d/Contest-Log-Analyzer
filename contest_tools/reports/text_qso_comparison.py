# Contest Log Analyzer/contest_tools/reports/text_qso_comparison.py
#
# Purpose: Generates a text-based report that provides a detailed pairwise
#          comparison of QSO counts (Total, Unique, Common) between two logs,
#          broken down by band and Run/S&P status.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-06
# Version: 0.30.39-Beta
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
## [0.30.39-Beta] - 2025-08-06
### Fixed
# - Corrected the logic in the 'TOTALS' section to correctly sum the
#   per-band unique and common QSO counts instead of recalculating them.
## [0.30.38-Beta] - 2025-08-06
### Fixed
# - Corrected the logic for calculating Common and Unique QSO counts to be
#   performed independently for each log, ensuring Total = Unique + Common.
from .report_interface import ContestReport
from ._report_utils import get_valid_dataframe, create_output_directory
import pandas as pd
import os
from ..contest_log import ContestLog

class Report(ContestReport):
    report_id = "qso_comparison"
    report_name = "QSO Comparison Summary"
    report_type = "text"
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

        canonical_band_order = [band[1] for band in ContestLog._HF_BANDS]
        all_bands_in_logs = pd.concat([df1['Band'], df2['Band']]).unique()
        bands = sorted(all_bands_in_logs, key=lambda b: canonical_band_order.index(b) if b in canonical_band_order else -1)
        
        report_lines = []
        report_lines.append(f"QSO Comparison: {call1} vs {call2}\n" + "="*40)
        
        # Initialize accumulators for the grand totals
        total_qso_1, total_unique_1, total_common_1 = 0, 0, 0
        total_qso_2, total_unique_2, total_common_2 = 0, 0, 0
        total_run_unique_1, total_sp_unique_1 = 0, 0
        total_run_unique_2, total_sp_unique_2 = 0, 0

        for band in bands:
            report_lines.append(f"\n--- {band} ---")
            
            c1_band = df1[df1['Band'] == band]
            c2_band = df2[df2['Band'] == band]

            calls1_band = set(c1_band['Call'])
            calls2_band = set(c2_band['Call'])
            
            common_calls_on_band = calls1_band.intersection(calls2_band)
            
            common_count_1 = len(c1_band[c1_band['Call'].isin(common_calls_on_band)])
            common_count_2 = len(c2_band[c2_band['Call'].isin(common_calls_on_band)])

            total_count_1 = len(c1_band)
            total_count_2 = len(c2_band)
            
            unique_count_1 = total_count_1 - common_count_1
            unique_count_2 = total_count_2 - common_count_2

            unique_calls_for_1 = calls1_band - calls2_band
            unique_calls_for_2 = calls2_band - calls1_band
            u1_band = c1_band[c1_band['Call'].isin(unique_calls_for_1)]
            u2_band = c2_band[c2_band['Call'].isin(unique_calls_for_2)]

            def get_run_sp(df):
                run_count = (df['Run'] == 'Run').sum()
                sp_count = (df['Run'] == 'S&P').sum()
                return f"{run_count}/{sp_count}"

            report_lines.append(f"          {'Total':>8} {'Unique':>8} {'Common':>8}   {'Run/S&P':>8}")
            report_lines.append(f"          {'-'*8} {'-'*8} {'-'*8}   {'-'*8}")
            
            report_lines.append(f"{call1:<9} {total_count_1:>8} {unique_count_1:>8} {common_count_1:>8} | Unique:  {get_run_sp(u1_band)}")
            report_lines.append(f"{call2:<9} {total_count_2:>8} {unique_count_2:>8} {common_count_2:>8} | Unique:  {get_run_sp(u2_band)}")

            # Accumulate totals
            total_qso_1 += total_count_1
            total_unique_1 += unique_count_1
            total_common_1 += common_count_1
            total_run_unique_1 += (u1_band['Run'] == 'Run').sum()
            total_sp_unique_1 += (u1_band['Run'] == 'S&P').sum()

            total_qso_2 += total_count_2
            total_unique_2 += unique_count_2
            total_common_2 += common_count_2
            total_run_unique_2 += (u2_band['Run'] == 'Run').sum()
            total_sp_unique_2 += (u2_band['Run'] == 'S&P').sum()
        
        # --- TOTALS Section ---
        report_lines.append("\n" + "="*40 + "\n--- TOTALS ---")

        report_lines.append(f"          {'Total':>8} {'Unique':>8} {'Common':>8}   {'Run/S&P':>8}")
        report_lines.append(f"          {'-'*8} {'-'*8} {'-'*8}   {'-'*8}")
        
        run_sp_1_total = f"{total_run_unique_1}/{total_sp_unique_1}"
        run_sp_2_total = f"{total_run_unique_2}/{total_sp_unique_2}"
        
        report_lines.append(f"{call1:<9} {total_qso_1:>8} {total_unique_1:>8} {total_common_1:>8} | Unique:  {run_sp_1_total}")
        report_lines.append(f"{call2:<9} {total_qso_2:>8} {total_unique_2:>8} {total_common_2:>8} | Unique:  {run_sp_2_total}")
        
        # Save to file
        output_filename = os.path.join(output_path, f"{self.report_id}_{call1}_vs_{call2}.txt")
        try:
            with open(output_filename, 'w') as f:
                f.write("\n".join(report_lines))
            return f"'{self.report_name}' saved to {output_filename}"
        except Exception as e:
            return f"Error generating report '{self.report_name}': {e}"