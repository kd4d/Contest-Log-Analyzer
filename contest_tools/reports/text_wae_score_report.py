# contest_tools/reports/text_wae_score_report.py
#
# Purpose: This module provides a detailed score summary for the WAE
#          contest, including QTC points and weighted multipliers.
#
#
# Author: Gemini AI
# Date: 2025-10-05
# Version: 0.90.2-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# --- Revision History ---
# [0.90.2-Beta] - 2025-10-05
# - Corrected scoring logic to sum the `QSOPoints` column instead of
#   counting all non-dupe QSOs, bringing it into alignment with the
#   correct logic in `wae_calculator.py`.
# [0.90.0-Beta] - 2025-10-01
# - Set new baseline version for release.

from typing import List, Dict, Any
import pandas as pd
import os
from prettytable import PrettyTable

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import get_valid_dataframe, create_output_directory, save_debug_data

class Report(ContestReport):
    """
    Generates a detailed, WAE-specific score summary report.
    """
    report_id: str = "text_wae_score_report"
    report_name: str = "WAE Score Summary"
    report_type: str = "text"
    supports_single = True

    _BAND_WEIGHTS = {'80M': 4, '40M': 3, '20M': 2, '15M': 2, '10M': 2}

    def generate(self, output_path: str, **kwargs) -> str:
        """Generates the report content."""
        log = self.logs[0]
        metadata = log.get_metadata()
        callsign = metadata.get('MyCall', 'UnknownCall')
        qsos_df = get_valid_dataframe(log, include_dupes=False)
        qtcs_df = getattr(log, 'qtcs_df', pd.DataFrame())

        if qsos_df.empty:
            return f"Skipping report for {callsign}: No valid QSOs to report."

        # --- Save Debug Data ---
        debug_data_flag = kwargs.get("debug_data", False)
        if debug_data_flag:
            debug_filename = f"{self.report_id}_{callsign}_debug.txt"
            debug_content = {
                "qsos_df_head": qsos_df.head().to_dict(),
                "qtcs_df_head": qtcs_df.head().to_dict(),
                "qsos_df_columns": list(qsos_df.columns),
                "qtcs_df_columns": list(qtcs_df.columns)
            }
            save_debug_data(True, output_path, debug_content, custom_filename=debug_filename)

        # --- Data Calculation ---
        summary_data = []
        band_mode_groups = qsos_df.groupby(['Band', 'Mode'])
        
        for (band, mode), group_df in band_mode_groups:
            qso_pts = len(group_df)
            
            # Weighted Multipliers
            weighted_mults = 0
            mult_cols = ['Mult1', 'Mult2']
            df_mults = group_df[group_df[mult_cols].notna().any(axis=1)]
            
            for col in mult_cols:
                if col in df_mults.columns:
                    unique_mults_on_band = df_mults[col].nunique()
                    weighted_mults += unique_mults_on_band * self._BAND_WEIGHTS.get(band, 1)
        
            summary_data.append({
                'Band': band, 'Mode': mode,
                'QSO Pts': qso_pts,
                'Weighted Mults': weighted_mults
            })

        # --- TOTALS ---
        total_qso_pts = qsos_df['QSOPoints'].sum()
        total_qtc_pts = len(qtcs_df)
        
        total_weighted_mults = 0
        df_mults_all = qsos_df[qsos_df[mult_cols].notna().any(axis=1)]
        for col in mult_cols:
            if col in df_mults_all.columns:
                band_mult_counts = df_mults_all.groupby('Band')[col].nunique()
                for band, count in band_mult_counts.items():
                    total_weighted_mults += count * self._BAND_WEIGHTS.get(band, 1)

        final_score = (total_qso_pts + total_qtc_pts) * total_weighted_mults

        # --- Formatting ---
        table = PrettyTable()
        table.field_names = ["Band", "Mode", "QSO Pts", "Weighted Mults"]
        table.align = 'r'
        table.align['Band'] = 'l'
        
        for row in sorted(summary_data, key=lambda x: (ContestLog._HAM_BANDS.index(([item for item in ContestLog._HAM_BANDS if item[1] == x['Band']][0])), x['Mode'])):
            table.add_row([
                row['Band'], row['Mode'],
                f"{row['QSO Pts']:,}", f"{row['Weighted Mults']:,}"
            ])
        
        table.add_row(['-'*b_len for b_len in [4,4,10,14]], divider=True)
        table.add_row([
            'TOTAL', '',
            f"{total_qso_pts:,}", f"{total_weighted_mults:,}"
        ])
        
        # --- Build Final Report String ---
        year = qsos_df['Date'].iloc[0].split('-')[0]
        contest_name = metadata.get('ContestName', 'UnknownContest')
        title1 = f"--- {self.report_name} ---"
        title2 = f"{year} {contest_name} - {callsign}"
        
        table_str = table.get_string()
        table_width = len(table_str.split('\n')[0])
        header_width = max(table_width, len(title1), len(title2))

        report_lines = [
            title1.center(header_width),
            title2.center(header_width),
            "",
            f"Operating Time: {metadata.get('OperatingTime', 'N/A')}",
            "",
            table_str,
            "",
            "Final Score Summary".center(table_width),
            ("=" * 20).center(table_width)
        ]
        
        # --- Dynamically Formatted Final Score Block ---
        summary_content = {
            'Total QSO Points:': total_qso_pts,
            'Total QTC Points:': total_qtc_pts,
            'Total Contacts:': (total_qso_pts + total_qtc_pts),
            'Total Weighted Multipliers:': total_weighted_mults,
            'FINAL SCORE:': final_score
        }
        max_label_width = max(len(label) for label in summary_content.keys())
        for label, value in summary_content.items():
            report_lines.append(f"{label:<{max_label_width}} {value:>15,}")
            if label == 'Total Weighted Multipliers:':
                report_lines.append("") # Add blank line before final score

        report_content = "\n".join(report_lines) + "\n"
        create_output_directory(output_path)
        filename = f"{self.report_id}_{callsign}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return f"Text report saved to: {filepath}"