# Contest Log Analyzer/contest_tools/reports/text_qso_comparison.py
#
# Purpose: A text report that generates a detailed comparison of QSO counts
#          (Total, Unique, Common) between two logs, broken down by Run/S&P status.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-07
# Version: 0.30.37-Beta
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
## [0.30.37-Beta] - 2025-08-07
### Fixed
# - Corrected a NameError by adding the missing import for 'Optional'
#   from the typing library.
## [0.30.8-Beta] - 2025-08-05
### Fixed
# - Corrected a bug in the calculation of Unique and Common QSO counts.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
from .report_interface import ContestReport
from ._report_utils import get_valid_dataframe, create_output_directory
import pandas as pd
from typing import List, Dict, Tuple, Optional
import os

class Report(ContestReport):
    report_id = "qso_comparison"
    report_name = "QSO Comparison"
    report_type = "text"
    supports_pairwise = True

    def generate(self, output_path: str, **kwargs) -> str:
        log1, log2 = self.logs[0], self.logs[1]
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')
        
        df1 = get_valid_dataframe(log1, kwargs.get('include_dupes', False))
        df2 = get_valid_dataframe(log2, kwargs.get('include_dupes', False))
        
        df1_calls = set(df1['Call'])
        df2_calls = set(df2['Call'])
        
        common_calls = df1_calls.intersection(df2_calls)
        
        report = []
        
        for call, df in [(call1, df1), (call2, df2)]:
            other_calls = df2_calls if call == call1 else df1_calls
            
            run_df = df[df['Run/S&P'] == 'Run']
            sp_df = df[df['Run/S&P'] == 'S&P']
            
            total_qsos = len(df)
            run_qsos = len(run_df)
            sp_qsos = len(sp_df)
            
            common_qsos = df['Call'].isin(common_calls).sum()
            unique_qsos = total_qsos - common_qsos
            
            common_run_qsos = run_df['Call'].isin(common_calls).sum()
            unique_run_qsos = run_qsos - common_run_qsos
            
            common_sp_qsos = sp_df['Call'].isin(common_calls).sum()
            unique_sp_qsos = sp_qsos - common_sp_qsos

            report.append(f"--- QSO Breakdown for {call} ---")
            report.append(f"{'Category':<10} | {'Total':>8} | {'Unique':>8} | {'Common':>8}")
            report.append(f"{'-'*10} | {'-'*8} | {'-'*8} | {'-'*8}")
            report.append(f"{'Run':<10} | {run_qsos:>8} | {unique_run_qsos:>8} | {common_run_qsos:>8}")
            report.append(f"{'S&P':<10} | {sp_qsos:>8} | {unique_sp_qsos:>8} | {common_sp_qsos:>8}")
            report.append(f"{'Total':<10} | {total_qsos:>8} | {unique_qsos:>8} | {common_qsos:>8}")
            report.append("")

        callsign_str = f"{call1}_vs_{call2}"
        filename = f"{self.report_id}_{callsign_str}.txt"
        filepath = os.path.join(output_path, filename)
        
        try:
            create_output_directory(output_path)
            with open(filepath, 'w') as f:
                f.write("\n".join(report))
            return f"'{self.report_name}' for {callsign_str} saved to {filepath}"
        except Exception as e:
            return f"Error generating report '{self.report_name}' for {callsign_str}: {e}"