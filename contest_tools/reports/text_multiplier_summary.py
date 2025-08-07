# Contest Log Analyzer/contest_tools/reports/text_multiplier_summary.py
#
# Purpose: A text report that generates a summary of QSOs per multiplier.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-07
# Version: 0.30.53-Beta
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
## [0.30.53-Beta] - 2025-08-07
### Fixed
# - Corrected an AttributeError by using the correct 'name' attribute of
#   the ContestDefinition object.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
from .report_interface import ContestReport
from ._report_utils import get_valid_dataframe, create_output_directory
import pandas as pd
from typing import List, Dict, Tuple
import os

class Report(ContestReport):
    report_id = "text_multiplier_summary"
    report_name = "Multiplier Summary"
    report_type = "text"
    supports_multi = True
    supports_single = True

    def generate(self, output_path: str, **kwargs) -> str:
        mult_name = kwargs.get('mult_name')
        if not mult_name:
            return "Skipping 'Multiplier Summary': Multiplier name not specified."

        dfs = [get_valid_dataframe(log) for log in self.logs]
        all_calls = [log.get_metadata().get('MyCall', f'Log{i+1}') for i, log in enumerate(self.logs)]
        
        return self._generate_report_for_logs(
            dfs=dfs, 
            all_calls=all_calls, 
            mult_name=mult_name, 
            output_path=output_path,
            contest_def=self.logs[0].contest_definition
        )

    def _generate_report_for_logs(self, dfs: List[pd.DataFrame], all_calls: List[str], mult_name: str, output_path: str, contest_def) -> str:
        mult_rule = next((rule for rule in contest_def.multiplier_rules if rule['name'] == mult_name), None)
        if not mult_rule:
            return f"Skipping 'Multiplier Summary': Multiplier rule '{mult_name}' not found."

        mult_col = mult_rule['value_column']
        mult_name_col = mult_rule.get('name_column')
        
        all_mults_data = []
        for df in dfs:
            if mult_col in df.columns:
                all_mults_data.append(df[[mult_col, mult_name_col] if mult_name_col else mult_col].dropna())
        
        if not all_mults_data:
            return f"Skipping 'Multiplier Summary' for '{mult_name}': No multiplier data found."

        if mult_name_col:
            all_mults_df = pd.concat(all_mults_data).drop_duplicates().sort_values(by=mult_name_col)
            mult_list = all_mults_df.to_records(index=False)
        else:
            mult_list = sorted(pd.concat(all_mults_data).unique())

        report_lines = []
        
        # --- Title ---
        year = dfs[0]['Date'].dropna().iloc[0].split('-')[0]
        title1 = f"Multiplier Summary for {mult_name}"
        title2 = f"{year} {contest_def.name} - {', '.join(all_calls)}"
        report_lines.append(f"{title1}\n{title2}")
        report_lines.append("=" * len(title2))

        # --- Table ---
        header = f"{mult_name:<20}" + "".join([f"| {call:<8}" for call in all_calls])
        report_lines.append(header)
        report_lines.append("-" * len(header))

        for mult_val in mult_list:
            display_val, mult_key = (mult_val[1], mult_val[0]) if mult_name_col else (mult_val, mult_val)
            
            row = f"{display_val:<20}"
            for df in dfs:
                count = len(df[df[mult_col] == mult_key])
                row += f"| {count:>8}"
            report_lines.append(row)

        # --- Totals ---
        report_lines.append("-" * len(header))
        total_row = f"{'Total Multipliers':<20}"
        for df in dfs:
            total_row += f"| {df[mult_col].nunique():>8}"
        report_lines.append(total_row)
        report_lines.append("=" * len(header))

        # --- Save to File ---
        callsign_str = '_'.join(sorted(all_calls))
        filename = f"{self.report_id}_{mult_name.lower()}_{callsign_str}.txt"
        filepath = os.path.join(output_path, filename)
        
        try:
            create_output_directory(output_path)
            with open(filepath, 'w') as f:
                f.write("\n".join(report_lines))
            return f"'{self.report_name}' for {mult_name} ({callsign_str}) saved to {filepath}"
        except Exception as e:
            return f"Error generating report '{self.report_name}' for {mult_name}: {e}"