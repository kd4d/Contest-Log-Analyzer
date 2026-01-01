# contest_tools/reports/html_multiplier_breakdown.py
#
# Purpose: Specialized HTML report for multiplier breakdown (Group Par) with offline visual support.
#
# Author: Gemini AI
# Date: 2025-12-31
# Version: 0.157.3-Beta
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
# [0.157.3-Beta] - 2025-12-31
# - Ported `global_max` calculation logic from views.py to fix invisible vertical bars in offline reports.
# [0.157.0-Beta] - 2025-12-31
# - Implemented Twin Context Architecture: Inlines 'dashboard.css' for offline styling.
# [0.155.3-Beta] - 2025-12-31
# - Corrected static path construction for offline report generator.
# [0.155.2-Beta] - 2025-12-30
# - Added JS Inlining Logic for `html2canvas` to support offline "Camera" feature.
# [0.131.1-Beta] - 2025-12-23
# - Enable single-log support.
# [0.137.0-Beta] - 2025-12-22
# - Initial creation.

import os
from django.template.loader import render_to_string
from django.conf import settings
from .report_interface import ContestReport
from ..data_aggregators.multiplier_stats import MultiplierStatsAggregator
from ._report_utils import _sanitize_filename_part, get_cty_metadata, get_standard_title_lines

class Report(ContestReport):
    report_id = "html_multiplier_breakdown"
    report_name = "Multiplier Breakdown (HTML)"
    is_specialized = False
    supports_multi = True
    supports_single = True

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

        # --- Load html2canvas and CSS for Inlining ---
        # settings.BASE_DIR points to /app/web_app
        # We append 'analyzer/static/...' relative to that base.
        js_content = ""
        css_content = ""
        
        try:
            static_base = os.path.join(settings.BASE_DIR, 'analyzer', 'static')
            js_path = os.path.join(static_base, 'js', 'html2canvas.min.js')
            css_path = os.path.join(static_base, 'css', 'dashboard.css')
            
            if os.path.exists(js_path):
                with open(js_path, 'r', encoding='utf-8') as f:
                    js_content = f.read()
            else:
                print(f"Warning: html2canvas.min.js not found at {js_path}. Capture feature disabled.")

            if os.path.exists(css_path):
                with open(css_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()
            else:
                print(f"Warning: dashboard.css not found at {css_path}. Offline styling may differ.")
                
        except Exception as e:
             print(f"Error reading static assets: {e}")

        # --- Calculate Global Maxima for Scaling (Ported from views.py) ---
        global_max = {'total': 1, 'countries': 1, 'zones': 1} # Default 1 to avoid div/0
        
        # Check 'bands' data if available
        if 'bands' in data:
            for block in data['bands']:
                for row in block['rows']:
                    row_max = 0
                    if row.get('stations'):
                        for stat in row['stations']:
                            val = stat.get('unique_run', 0) + stat.get('unique_sp', 0) + stat.get('unique_unk', 0)
                            if val > row_max: row_max = val
                    
                    # Update global maxes based on row label keywords
                    if row['label'] == 'TOTAL' or row['label'] == block['label']:
                        if row_max > global_max['total']: global_max['total'] = row_max
                    elif 'Countries' in row['label']:
                        if row_max > global_max['countries']: global_max['countries'] = row_max
                    elif 'Zones' in row['label']:
                        if row_max > global_max['zones']: global_max['zones'] = row_max

        context = {
            'report_title_lines': title_lines,
            'creation_date': get_cty_metadata(self.logs),
            'all_calls': all_calls,
            'breakdown_totals': data['totals'],
            'low_bands_data': low_bands_data,
            'high_bands_data': high_bands_data,
            'global_max': global_max,
            'html2canvas_js': js_content, # Pass full JS string
            'css_content': css_content,   # Pass full CSS string
        }

        # 3. Render Template
        html_content = render_to_string('html_multiplier_breakdown.html', context)

        # 4. Save File
        combo_id = "_".join([_sanitize_filename_part(c) for c in all_calls])
        filename = f"html_multiplier_breakdown_{combo_id}.html"

        os.makedirs(output_path, exist_ok=True)
        filepath = os.path.join(output_path, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return f"Report saved to {filepath}"