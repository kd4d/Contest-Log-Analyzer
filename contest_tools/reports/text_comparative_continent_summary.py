# Contest Log Analyzer/contest_tools/reports/text_comparative_continent_summary.py
#
# Purpose: A text report that generates a side-by-side comparison of QSOs
#          per continent for multiple logs.
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
    report_id = "text_comparative_continent_summary"
    report_name = "Comparative Continent Summary"
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

        # --- Table ---
        all_dfs = [get_valid_dataframe(log) for log in self.logs]
        all_continents = sorted(pd.concat([df['Continent'] for df in all_dfs]).dropna().unique())
        
        header = f"{'Continent':<12}" + "".join([f"| {call:<8}" for call in all_calls])
        report_lines.append(header)
        report_lines.append("-" * len(header))
        
        for continent in all_continents:
            row = f"{continent:<12}"
            for df in all_dfs:
                count = len(df[df['Continent'] == continent])
                row += f"| {count:>8}"
            report_lines.append(row)
            
        # --- Totals ---
        report_lines.append("-" * len(header))
        total_row = f"{'Total':<12}"
        for df in all_dfs:
            total_row += f"| {len(df[df['Continent'].notna()]):>8}"
        report_lines.append(total_row)
        report_lines.append("=" * len(header))

        # --- Diagnostic Sections ---
        self._add_diagnostic_sections(report_lines, first_log.contest_definition)
        
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

    def _add_diagnostic_sections(self, report_lines: List[str], contest_def):
        """Adds sections for unknown continents and prefixes."""
        
        all_unknown_continents = {}
        all_unknown_prefixes = {}

        for log in self.logs:
            call = log.get_metadata().get('MyCall', 'Unknown')
            df = get_valid_dataframe(log)
            
            unknown_continent_calls = sorted(df[df['Continent'].isna()]['Call'].unique())
            if unknown_continent_calls:
                all_unknown_continents[call] = unknown_continent_calls
                
            if 'CQ-WPX' in contest_def.name:
                unknown_prefix_calls = sorted(df[df['Prefix_Mult'].isna()]['Call'].unique())
                if unknown_prefix_calls:
                    all_unknown_prefixes[call] = unknown_prefix_calls

        if all_unknown_continents:
            report_lines.append("\n--- Callsigns with Unknown Continents ---")
            for call, calls in all_unknown_continents.items():
                report_lines.append(f"{call}: {', '.join(calls)}")
        
        if all_unknown_prefixes:
            report_lines.append("\n--- Callsigns with Unknown Prefixes (WPX) ---")
            for call, calls in all_unknown_prefixes.items():
                report_lines.append(f"{call}: {', '.join(calls)}")