# contest_tools/reports/text_wae_comparative_score_report.py
#
# Purpose: A text report that generates a comparative, interleaved score
#          summary for the WAE contest.
#
#
# Author: Gemini AI
# Date: 2025-10-05
# Version: 0.90.3-Beta
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
# [0.90.3-Beta] - 2025-10-05
# - Corrected scoring logic to sum the `QSOPoints` column instead of
#   counting all non-dupe QSOs, bringing it into alignment with the
#   correct logic in `wae_calculator.py`.
# [0.90.0-Beta] - 2025-10-01
# - Set new baseline version for release.

from typing import List, Set, Dict, Tuple
import pandas as pd
import os
from prettytable import PrettyTable
from ..contest_log import ContestLog
from ..contest_definitions import ContestDefinition
from .report_interface import ContestReport
from ._report_utils import get_valid_dataframe, create_output_directory

class Report(ContestReport):
    """
    Generates a comparative, interleaved WAE score summary report.
    """
    report_id: str = "text_wae_comparative_score_report"
    report_name: str = "WAE Comparative Score Report"
    report_type: str = "text"
    supports_multi = True
    supports_pairwise = True
    
    _BAND_WEIGHTS = {'80M': 4, '40M': 3, '20M': 2, '15M': 2, '10M': 2}

    def generate(self, output_path: str, **kwargs) -> str:
        """Generates the report content."""
        all_calls = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in self.logs])
        
        # --- Data Aggregation by Band and Mode ---
        band_mode_summaries = {}
        for log in self.logs:
            call = log.get_metadata().get('MyCall', 'Unknown')
            qsos_df = get_valid_dataframe(log, include_dupes=False)
            if qsos_df.empty:
                continue
            
            grouped = qsos_df.groupby(['Band', 'Mode'])
            for (band, mode), group_df in grouped:
                key = (band, mode)
                if key not in band_mode_summaries:
                    band_mode_summaries[key] = []
                
                summary = self._calculate_band_mode_summary(group_df, call)
                band_mode_summaries[key].append(summary)

        # --- Report Generation using PrettyTable ---
        canonical_band_order = [band[1] for band in ContestLog._HAM_BANDS]
        sorted_keys = sorted(band_mode_summaries.keys(), key=lambda x: (canonical_band_order.index(x[0]), x[1]))

        report_lines = []
        table = PrettyTable()
        table.field_names = ["Callsign", "QSO Pts", "Weighted Mults"]
        table.align = 'r'
        table.align['Callsign'] = 'l'

        for key in sorted_keys:
            band, mode = key
            report_lines.append(f"\n--- {band} {mode} ---")
            
            table.clear_rows()
            for row in sorted(band_mode_summaries[key], key=lambda x: x['Callsign']):
                table.add_row([row['Callsign'], f"{row['QSO Pts']:,}", f"{row['Weighted Mults']:,}"])
            report_lines.append(table.get_string())

        # --- TOTALS Section ---
        total_summaries, final_scores = self._calculate_totals()
        report_lines.append("\n--- TOTAL ---")
        
        total_table = PrettyTable()
        total_table.field_names = ["Callsign", "On-Time", "QSO Pts", "QTC Pts", "Weighted Mults"]
        total_table.align = 'r'
        total_table.align['Callsign'] = 'l'
        total_table.align['On-Time'] = 'l'
        for call in all_calls:
            if call in total_summaries:
                data = total_summaries[call]
                total_table.add_row([
                    call, data.get('On-Time', 'N/A'), f"{data['QSO Pts']:,}", 
                    f"{data['QTC Pts']:,}", f"{data['Weighted Mults']:,}"
                ])
        report_lines.append(total_table.get_string())
        
        # --- Final Score Summary ---
        final_score_lines = ["", "Final Score Summary", "="*20]
        max_label_width = max(len(f"TOTAL SCORE ({call})") for call in all_calls)
        for call in all_calls:
            label = f"TOTAL SCORE ({call})"
            score_str = f"{final_scores.get(call, 0):,}"
            final_score_lines.append(f"{label:<{max_label_width}} : {score_str}")
        report_lines.extend(final_score_lines)

        # --- Prepend Titles ---
        first_log = self.logs[0]
        year = first_log.get_processed_data()['Date'].iloc[0].split('-')[0]
        contest_name = first_log.get_metadata().get('ContestName')
        title1 = f"--- {self.report_name} ---"
        title2 = f"{year} {contest_name} - {', '.join(all_calls)}"
        
        final_report_str = "\n".join([title1, title2] + report_lines) + "\n"
        
        # --- Save to File ---
        create_output_directory(output_path)
        filename_calls = '_vs_'.join(all_calls)
        filename = f"{self.report_id}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_report_str)
        
        return f"Text report saved to: {filepath}"

    def _calculate_band_mode_summary(self, df_band_mode: pd.DataFrame, callsign: str) -> dict:
        summary = {'Callsign': callsign}
        summary['QSO Pts'] = df_band_mode['QSOPoints'].sum()
        
        band = df_band_mode['Band'].iloc[0]
        weighted_mults = 0
        mult_cols = ['Mult1', 'Mult2']
        df_mults = df_band_mode[df_band_mode[mult_cols].notna().any(axis=1)]
        
        for col in mult_cols:
            if col in df_mults.columns:
                unique_mults_on_band = df_mults[col].nunique()
                weighted_mults += unique_mults_on_band * self._BAND_WEIGHTS.get(band, 1)
        
        summary['Weighted Mults'] = weighted_mults
        return summary

    def _calculate_totals(self) -> Tuple[Dict[str, Dict], Dict[str, int]]:
        total_summaries = {}
        final_scores = {}

        for log in self.logs:
            call = log.get_metadata().get('MyCall', 'Unknown')
            qsos_df = get_valid_dataframe(log, False)
            qtcs_df = getattr(log, 'qtcs_df', pd.DataFrame())

            total_qso_pts = qsos_df['QSOPoints'].sum()
            total_qtc_pts = len(qtcs_df)
            
            total_weighted_mults = 0
            mult_cols = ['Mult1', 'Mult2']
            df_mults_all = qsos_df[qsos_df[mult_cols].notna().any(axis=1)]
            
            if not df_mults_all.empty:
                for col in mult_cols:
                    if col in df_mults_all.columns:
                        band_mult_counts = df_mults_all.groupby('Band')[col].nunique()
                        for band, count in band_mult_counts.items():
                            total_weighted_mults += count * self._BAND_WEIGHTS.get(band, 1)

            total_summaries[call] = {
                'On-Time': log.get_metadata().get('OperatingTime'),
                'QSO Pts': total_qso_pts,
                'QTC Pts': total_qtc_pts,
                'Weighted Mults': total_weighted_mults
            }
            final_scores[call] = (total_qso_pts + total_qtc_pts) * total_weighted_mults

        return total_summaries, final_scores