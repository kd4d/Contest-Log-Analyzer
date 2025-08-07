# Contest Log Analyzer/contest_tools/reports/text_missed_multipliers.py
#
# Purpose: A text report that generates a list of multipliers that were
#          missed by each station in a pairwise comparison.
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
## [0.30.55-Beta] - 2025-08-07
### Fixed
# - Corrected an AttributeError by using the correct 'name' attribute of
#   the ContestDefinition object.
# ---
from .report_interface import ContestReport
from ._report_utils import get_valid_dataframe, create_output_directory, _sanitize_filename_part
import pandas as pd
from typing import List, Dict
import os

class Report(ContestReport):
    report_id = "text_missed_multipliers"
    report_name = "Missed Multipliers"
    report_type = "text"
    supports_pairwise = True

    def generate(self, output_path: str, **kwargs) -> str:
        mult_name = kwargs.get('mult_name')
        if not mult_name:
            return "Skipping 'Missed Multipliers': Multiplier name not specified."

        log1, log2 = self.logs[0], self.logs[1]
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')
        first_log_def = log1.contest_definition

        mult_rule = next((rule for rule in first_log_def.multiplier_rules if rule['name'] == mult_name), None)
        if not mult_rule:
            return f"Skipping 'Missed Multipliers': Multiplier rule '{mult_name}' not found."

        report_scope = first_log_def.multiplier_report_scope
        
        df1 = get_valid_dataframe(log1)
        df2 = get_valid_dataframe(log2)

        if report_scope == 'per_contest':
            missed_by_log1, missed_by_log2 = self._get_missed_mults(df1, df2, mult_rule)
            report_lines = self._format_report(missed_by_log1, missed_by_log2, call1, call2, mult_rule)
        else: # per_band
            all_bands = sorted(pd.concat([df1['Band'], df2['Band']]).unique())
            report_lines = []
            for band in all_bands:
                df1_band = df1[df1['Band'] == band]
                df2_band = df2[df2['Band'] == band]
                missed_by_log1, missed_by_log2 = self._get_missed_mults(df1_band, df2_band, mult_rule)
                
                if missed_by_log1 or missed_by_log2:
                    report_lines.append(f"\n--- {band} ---")
                    report_lines.extend(self._format_report(missed_by_log1, missed_by_log2, call1, call2, mult_rule))

        # --- Title ---
        year = df1['Date'].dropna().iloc[0].split('-')[0]
        title1 = f"Missed Multiplier Report for {mult_name}"
        title2 = f"{year} {first_log_def.name} - {call1} vs {call2}"
        report_lines.insert(0, f"{title1}\n{title2}\n{'=' * len(title2)}")
        
        # --- Save to File ---
        callsign_str = f"{call1}_vs_{call2}"
        filename_mult_name = _sanitize_filename_part(mult_name)
        filename = f"{self.report_id}_{filename_mult_name}_{callsign_str}.txt"
        filepath = os.path.join(output_path, filename)

        try:
            create_output_directory(output_path)
            with open(filepath, 'w') as f:
                f.write("\n".join(report_lines))
            return f"'{self.report_name}' for {mult_name} ({callsign_str}) saved to {filepath}"
        except Exception as e:
            return f"Error generating report '{self.report_name}' for {mult_name}: {e}"

    def _get_missed_mults(self, df1, df2, mult_rule):
        mult_col = mult_rule['value_column']
        name_col = mult_rule.get('name_column')
        
        mults1 = set(df1[mult_col].dropna().unique())
        mults2 = set(df2[mult_col].dropna().unique())

        missed_by_1 = mults2 - mults1
        missed_by_2 = mults1 - mults2
        
        if name_col:
            name_map = pd.concat([df1[[mult_col, name_col]], df2[[mult_col, name_col]]]).drop_duplicates().set_index(mult_col)[name_col].to_dict()
            missed_by_1_named = sorted([name_map.get(m, m) for m in missed_by_1])
            missed_by_2_named = sorted([name_map.get(m, m) for m in missed_by_2])
            return missed_by_1_named, missed_by_2_named
        else:
            return sorted(list(missed_by_1)), sorted(list(missed_by_2))

    def _format_report(self, missed_by_1, missed_by_2, call1, call2, mult_rule):
        lines = []
        if missed_by_1:
            lines.append(f"\nMultipliers worked by {call2} but missed by {call1}:")
            lines.append(", ".join(map(str, missed_by_1)))
        if missed_by_2:
            lines.append(f"\nMultipliers worked by {call1} but missed by {call2}:")
            lines.append(", ".join(map(str, missed_by_2)))
        return lines