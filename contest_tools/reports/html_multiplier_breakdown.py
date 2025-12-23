# contest_tools/reports/html_multiplier_breakdown.py
#
# Purpose: Specialized HTML report for multiplier breakdown (Group Par).
#
# Author: Gemini AI
# Date: 2025-12-22
# Version: 0.137.0-Beta
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
# [0.137.0-Beta] - 2025-12-22
# - Initial creation.

import os
from django.template.loader import render_to_string
from .report_interface import ContestReport
from ..data_aggregators.multiplier_stats import MultiplierStatsAggregator
from ._report_utils import _sanitize_filename_part, get_cty_metadata, get_standard_title_lines

class Report(ContestReport):
    report_id = "html_multiplier_breakdown"
    report_name = "Multiplier Breakdown (HTML)"
    is_specialized = False
    supports_multi = True

    def generate(self, output_path: str, **kwargs) -> str:
        # 1. Aggregate Data
        mult_agg = MultiplierStatsAggregator(self.logs)
        data = mult_agg.get_multiplier_breakdown_data()

        # 2. Setup Context
        all_calls = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in self.logs])
        
        # Smart scoping for title (Modes)
        modes_present = set()
        for log in self.logs:
            df = log.get_processed_data()
            if 'Mode' in df.columns:
                modes_present.update(df['Mode'].dropna().unique())

        title_lines = get_standard_title_lines(
            "Multiplier Breakdown (Group Par)", 
            self.logs, 
            "All Bands", 
            None, 
            modes_present
        )
        
        # Split Bands for Layout (Low vs High) to match template expectation
        low_bands = ['160M', '80M', '40M']
        low_bands_data = []
        high_bands_data = []
        
        for block in data['bands']:
            if block['label'] in low_bands:
                low_bands_data.append(block)
            else:
                high_bands_data.append(block)

        context = {
            'report_title_lines': title_lines,
            'creation_date': get_cty_metadata(self.logs),
            'all_calls': all_calls,
            'breakdown_totals': data['totals'],
            'low_bands_data': low_bands_data,
            'high_bands_data': high_bands_data,
        }

        # 3. Render Template
        html_content = render_to_string('html_multiplier_breakdown.html', context)

        # 4. Save File
        combo_id = "_".join([_sanitize_filename_part(c) for c in all_calls])
        filename = f"html_multiplier_breakdown_{combo_id}.html"

        os.makedirs(output_path, exist_ok=True)
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w') as f:
            f.write(html_content)

        return f"Report saved to {filepath}"