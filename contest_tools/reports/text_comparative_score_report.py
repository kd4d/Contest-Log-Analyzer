# Contest Log Analyzer/contest_tools/reports/text_comparative_score_report.py
#
# Purpose: A text report that generates a side-by-side comparison of the
#          final scores for multiple logs.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-07
# Version: 0.30.54-Beta
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
## [0.30.54-Beta] - 2025-08-07
### Fixed
# - Corrected an AttributeError by using the correct 'name' attribute of
#   the ContestDefinition object.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
from .report_interface import ContestReport
from ._report_utils import get_valid_dataframe, create_output_directory
import pandas as pd
from typing import List, Dict
import os

class Report(ContestReport):
    report_id = "text_comparative_score_report"
    report_name = "Comparative Score Report"
    report_type = "text"
    supports_multi = True

    def generate(self, output_path: str, **kwargs) -> str:
        all_calls = sorted([log.get_metadata().get('MyCall', f'Log{i+1}') for i, log in enumerate(self.logs)])
        callsign_str = '_'.join(all_calls)

        report_lines = []
        
        # --- Title ---
        first_log = self.logs[0]
        metadata = first_log.get_metadata()
        year = get_valid_dataframe(first_log)['Date'].dropna().iloc[0].split('-')[0]
        contest_name = metadata.get('ContestName', '')
        event_id = metadata.get('EventID', '')

        title_line1 = f"{event_id} {year} {contest_name}".strip()
        title_line2 = f"{self.report_name} ({callsign_str})"
        report_lines.append(f"{title_line1}\n{title_line2}")
        report_lines.append("=" * len(title_line2))

        # --- Data Prep ---
        contest_def = first_log.contest_definition
        mult_rules = contest_def.multiplier_rules
        mult_cols = [rule['value_column'] for rule in mult_rules]
        mult_names = [rule['name'] for rule in mult_rules]
        
        total_summaries = [self._calculate_totals(log, mult_cols, mult_names) for log in self.logs]

        # --- Table ---
        header = f"{'Category':<15}" + "".join([f"| {call:<12}" for call in all_calls])
        report_lines.append(header)
        report_lines.append("-" * len(header))
        
        for key, name in [("QSOs", "QSOs"), ("Points", "Points")] + list(zip(mult_cols, mult_names)) + [("Score", "Score")]:
            row = f"{name:<15}"
            for summary in total_summaries:
                val = summary.get(key, 0)
                row += f"| {val:>12,}"
            report_lines.append(row)
            
        report_lines.append("=" * len(header))

        # --- Diagnostic Sections ---
        self._add_diagnostic_sections(report_lines, contest_def)

        # --- Save to File ---
        filename = f"{self.report_id}_{callsign_str}.txt"
        filepath = os.path.join(output_path, filename)
        
        try:
            create_output_directory(output_path)
            with open(filepath, 'w') as f:
                f.write("\n".join(report_lines))
            return f"'{self.report_name}' for {callsign_str} saved to {filepath}"
        except Exception as e:
            return f"Error generating report '{self.report_name}' for {callsign_str}: {e}"

    def _calculate_totals(self, log, mult_cols, mult_names):
        df_net = get_valid_dataframe(log, include_dupes=False)
        df_gross = get_valid_dataframe(log, include_dupes=True)

        summary = {
            "QSOs": len(df_net),
            "Points": df_net['QSOPoints'].sum(),
        }

        df_valid_mults = df_net[df_net['QSOPoints'] > 0] if not log.contest_definition.mults_from_zero_point_qsos else df_gross
        
        total_mults = 0
        for col in mult_cols:
            mult_count = df_valid_mults[col].nunique()
            summary[col] = mult_count
            total_mults += mult_count
            
        summary["Score"] = summary["Points"] * total_mults
        return summary

    def _add_diagnostic_sections(self, report_lines: List[str], contest_def):
        """Adds sections for unknown multipliers."""
        
        all_unknown_mults = {}

        for log in self.logs:
            call = log.get_metadata().get('MyCall', 'Unknown')
            df = get_valid_dataframe(log)
            
            for rule in contest_def.multiplier_rules:
                mult_col = rule['value_column']
                name_col = rule.get('name_column')
                
                if name_col and name_col in df.columns:
                    unknown_mult_calls = sorted(df[df[name_col].isna()][mult_col].unique())
                    if unknown_mult_calls:
                        key = f"{call} - Unknown {rule['name']}"
                        all_unknown_mults[key] = [str(m) for m in unknown_mult_calls if pd.notna(m)]
        
        if 'CQ-WPX' in contest_def.name:
            all_unknown_prefixes = {}
            for log in self.logs:
                call = log.get_metadata().get('MyCall', 'Unknown')
                df = get_valid_dataframe(log)
                unknown_prefix_calls = sorted(df[df['Prefix_Mult'].isna()]['Call'].unique())
                if unknown_prefix_calls:
                    all_unknown_prefixes[call] = unknown_prefix_calls
            
            if all_unknown_prefixes:
                report_lines.append("\n--- Callsigns with Unknown Prefixes (WPX) ---")
                for call, calls in all_unknown_prefixes.items():
                    report_lines.append(f"{call}: {', '.join(calls)}")

        if all_unknown_mults:
            report_lines.append("\n--- Unresolved Multipliers ---")
            for key, mults in all_unknown_mults.items():
                report_lines.append(f"{key}: {', '.join(mults)}")