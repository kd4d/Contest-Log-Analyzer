# Contest Log Analyzer/contest_tools/reports/text_qso_comparison.py
#
# Purpose: Generates a text-based report that provides a detailed pairwise
#          comparison of QSO counts (Total, Unique, Common) between two logs,
#          broken down by band and Run/S&P status.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-05
# Version: 0.30.11-Beta
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
## [0.30.11-Beta] - 2025-08-05
### Fixed
# - Corrected the key for sorting bands to prevent a ValueError, aligning it
#   with the fixes made to the other report files.
## [0.30.10-Beta] - 2025-08-05
### Fixed
# - Removed erroneous plotting code.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
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

        # Find common and unique QSOs
        common_calls = pd.merge(df1, df2, on='Call', how='inner')['Call']
        unique_to_1 = df1[~df1['Call'].isin(common_calls)]
        unique_to_2 = df2[~df2['Call'].isin(common_calls)]
        
        # --- FIX: Correct the key for sorting bands ---
        canonical_band_order = [band[1] for band in ContestLog._HF_BANDS]
        all_bands_in_logs = pd.concat([df1['Band'], df2['Band']]).unique()
        bands = sorted(all_bands_in_logs, key=lambda b: canonical_band_order.index(b) if b in canonical_band_order else -1)
        
        report_lines = []
        report_lines.append(f"QSO Comparison: {call1} vs {call2}\n" + "="*40)

        for band in bands:
            report_lines.append(f"\n--- {band} ---")
            
            # Data for the current band
            c1_band = df1[df1['Band'] == band]
            c2_band = df2[df2['Band'] == band]
            u1_band = unique_to_1[unique_to_1['Band'] == band]
            u2_band = unique_to_2[unique_to_2['Band'] == band]
            common_band = df1[(df1['Band'] == band) & (df1['Call'].isin(common_calls))]

            # Helper to get Run/S&P counts
            def get_run_sp(df):
                run_count = (df['Run'] == 'Run').sum()
                sp_count = len(df) - run_count
                return f"{run_count}/{sp_count}"

            report_lines.append(f"          {'Total':>8} {'Unique':>8} {'Common':>8}   {'Run/S&P':>8}")
            report_lines.append(f"          {'-'*8} {'-'*8} {'-'*8}   {'-'*8}")
            
            report_lines.append(f"{call1:<9} {len(c1_band):>8} {len(u1_band):>8} {len(common_band):>8} | Unique:  {get_run_sp(u1_band)}")
            report_lines.append(f"{call2:<9} {len(c2_band):>8} {len(u2_band):>8} {len(common_band):>8} | Unique:  {get_run_sp(u2_band)}")
        
        # Total Summary
        report_lines.append("\n" + "="*40 + "\n--- TOTALS ---")
        report_lines.append(f"          {'Total':>8} {'Unique':>8} {'Common':>8}   {'Run/S&P':>8}")
        report_lines.append(f"          {'-'*8} {'-'*8} {'-'*8}   {'-'*8}")
        report_lines.append(f"{call1:<9} {len(df1):>8} {len(unique_to_1):>8} {len(common_calls):>8} | Unique:  {get_run_sp(unique_to_1)}")
        report_lines.append(f"{call2:<9} {len(df2):>8} {len(unique_to_2):>8} {len(common_calls):>8} | Unique:  {get_run_sp(unique_to_2)}")
        
        # Save to file
        output_filename = os.path.join(output_path, f"{self.report_id}_{call1}_vs_{call2}.txt")
        try:
            with open(output_filename, 'w') as f:
                f.write("\n".join(report_lines))
            return f"'{self.report_name}' saved to {output_filename}"
        except Exception as e:
            return f"Error generating report '{self.report_name}': {e}"