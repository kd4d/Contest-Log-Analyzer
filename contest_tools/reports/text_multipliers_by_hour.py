# Contest Log Analyzer/contest_tools/reports/text_multipliers_by_hour.py
#
# Purpose: A text report that generates a summary of new multipliers worked
#          per hour of the contest.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-07
# Version: 0.30.65-Beta
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
## [0.30.65-Beta] - 2025-08-07
### Fixed
# - Corrected a FileNotFoundError by using the new `_sanitize_filename_part`
#   helper function.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
# ---
from .report_interface import ContestReport
from ._report_utils import get_valid_dataframe, create_output_directory, _sanitize_filename_part
import pandas as pd
from typing import List, Dict
import os

class Report(ContestReport):
    report_id = "text_multipliers_by_hour"
    report_name = "Multipliers by Hour"
    report_type = "text"
    supports_single = True

    def generate(self, output_path: str, **kwargs) -> str:
        mult_name = kwargs.get('mult_name')
        if not mult_name:
            return "Skipping 'Multipliers by Hour': Multiplier name not specified."

        log = self.logs[0]
        callsign = log.get_metadata().get('MyCall', 'Log')
        contest_def = log.contest_definition

        mult_rule = next((rule for rule in contest_def.multiplier_rules if rule['name'] == mult_name), None)
        if not mult_rule:
            return f"Skipping 'Multipliers by Hour': Multiplier rule '{mult_name}' not found."

        mult_col = mult_rule['value_column']
        df = get_valid_dataframe(log)
        
        if mult_col not in df.columns or df[mult_col].isna().all():
            return f"Skipping report '{self.report_name}' for {callsign}: No valid '{mult_name}' data to report."

        df_sorted = df.sort_values('Datetime')
        df_unique_mults = df_sorted.drop_duplicates(subset=[mult_col])

        hourly_mults = df_unique_mults.groupby('Hour')[mult_col].count()
        
        report_lines = []

        # --- Title ---
        year = df['Date'].dropna().iloc[0].split('-')[0]
        title1 = f"New {mult_name} Worked per Hour"
        title2 = f"{year} {contest_def.name} - {callsign}"
        report_lines.append(f"{title1}\n{title2}")
        report_lines.append("=" * len(title2))
        
        # --- Table ---
        header = f"{'Hour':<6} | {'New Mults':<10}"
        report_lines.append(header)
        report_lines.append("-" * len(header))
        
        for hour in range(24):
            hour_str = f"{hour:02d}"
            count = hourly_mults.get(hour_str, 0)
            report_lines.append(f"{hour_str:<6} | {count:<10}")
            
        report_lines.append("-" * len(header))
        total_row = f"{'Total':<6} | {hourly_mults.sum():<10}"
        report_lines.append(total_row)
        report_lines.append("=" * len(header))

        # --- Save to File ---
        filename_mult_name = _sanitize_filename_part(mult_name)
        filename = f"{self.report_id}_{filename_mult_name}_{callsign}.txt"
        filepath = os.path.join(output_path, filename)

        try:
            create_output_directory(output_path)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            return f"'{self.report_name}' for {mult_name} ({callsign}) saved to {filepath}"
        except Exception as e:
            return f"Error generating report '{self.report_name}' for {mult_name}: {e}"