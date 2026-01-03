# contest_tools/reports/text_wae_score_report.py
#
# Purpose: This module provides a detailed score summary for the WAE
#          contest, including QTC points and weighted multipliers.
#
# Author: Gemini AI
# Date: 2026-01-03
# Version: 0.151.2-Beta
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
# [0.151.2-Beta] - 2026-01-03
# - Refactored imports to use absolute path `contest_tools.utils.report_utils` to resolve circular dependencies.
# [0.134.1-Beta] - 2025-12-20
# - Added standard report header generation using `format_text_header`.
# [0.91.4-Beta] - 2025-11-24
# - Refactored to use WaeStatsAggregator (DAL) for scoring logic.
# [0.91.3-Beta] - 2025-10-10
# - Marked report as specialized to enable the new opt-in logic.
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
from contest_tools.utils.report_utils import get_valid_dataframe, create_output_directory, save_debug_data, format_text_header, get_cty_metadata, get_standard_title_lines
from ..data_aggregators.wae_stats import WaeStatsAggregator

class Report(ContestReport):
    """
    Generates a detailed, WAE-specific score summary report.
    """
    report_id: str = "text_wae_score_report"
    report_name: str = "WAE Score Summary"
    report_type: str = "text"
    is_specialized = True
    supports_single = True

    def generate(self, output_path: str, **kwargs) -> str:
        """Generates the report content."""
        log = self.logs[0]
        metadata = log.get_metadata()
        callsign = metadata.get('MyCall', 'UnknownCall')
        
        # We still need raw DF for debug data dump if requested, 
        # or we could trust the aggregator.
        # For legacy compatibility with the "Debug Data" block below, we pull it briefly.
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

        # --- Data Calculation (via DAL) ---
        aggregator = WaeStatsAggregator()
        wae_data = aggregator.get_wae_breakdown([log])
        log_data = wae_data["logs"].get(callsign)
        
        if not log_data:
             return f"Skipping report for {callsign}: No data returned from aggregator."
        
        # --- Formatting ---
        table = PrettyTable()
        table.field_names = ["Band", "Mode", "QSO Pts", "Weighted Mults"]
        table.align = 'r'
        table.align['Band'] = 'l'
        
        # Aggregator already sorts by Canonical Band Order then Mode
        for row in log_data['breakdown']:
            table.add_row([
                row['band'], row['mode'],
                f"{row['qso_points']:,}", f"{row['weighted_mults']:,}"
            ])
        
        table.add_row(['-'*b_len for b_len in [4,4,10,14]], divider=True)

        scalars = log_data['scalars']
        table.add_row([
            'TOTAL', '',
            f"{scalars['total_qso_points']:,}", f"{scalars['total_weighted_mults']:,}"
        ])
        
        # --- Build Final Report String ---
        table_str = table.get_string()
        table_width = len(table_str.split('\n')[0])
        
        # Standard Header
        modes_present = set(qsos_df['Mode'].dropna().unique())
        title_lines = get_standard_title_lines(self.report_name, [log], "All Bands", None, modes_present)
        meta_lines = ["Contest Log Analytics by KD4D", get_cty_metadata([log])]
        header_block = format_text_header(table_width, title_lines, meta_lines)

        report_lines = header_block + [
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
            'Total QSO Points:': scalars['total_qso_points'],
            'Total QTC Points:': scalars['total_qtc_points'],
            'Total Contacts:': (scalars['total_qso_points'] + scalars['total_qtc_points']),
            'Total Weighted Multipliers:': scalars['total_weighted_mults'],
            'FINAL SCORE:': scalars['final_score']
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