# contest_tools/reports/html_multiplier_breakdown.py
#
# Purpose: Specialized HTML report for multiplier breakdown (Group Par) with offline visual support.
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
import os
from django.template.loader import render_to_string
from django.conf import settings
from .report_interface import ContestReport
from ..data_aggregators.multiplier_stats import MultiplierStatsAggregator
from contest_tools.utils.report_utils import _sanitize_filename_part, get_cty_metadata, get_standard_title_lines
from contest_tools.utils.callsign_utils import build_callsigns_filename_part

class Report(ContestReport):
    report_id = "html_multiplier_breakdown"
    report_name = "Multiplier Breakdown (HTML)"
    is_specialized = False
    supports_multi = True
    supports_single = True

    def generate(self, output_path: str, **kwargs) -> str:
        # 1. Determine dimension (band or mode) based on contest type
        dimension = 'band'  # Default
        if self.logs:
            contest_def = self.logs[0].contest_definition
            valid_bands = contest_def.valid_bands
            valid_modes = getattr(contest_def, 'valid_modes', [])
            is_single_band = len(valid_bands) == 1
            is_multi_mode = len(valid_modes) > 1
            if is_single_band and is_multi_mode:
                dimension = 'mode'
        
        # 2. Aggregate Data
        mult_agg = MultiplierStatsAggregator(self.logs)
        data = mult_agg.get_multiplier_breakdown_data(dimension=dimension)
        
        # Determine dimension key and labels
        dimension_key = 'modes' if dimension == 'mode' else 'bands'
        scope_label = 'All Modes' if dimension == 'mode' else 'All Bands'
        
        # 3. Setup Context
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
            scope_label, 
            None, 
            modes_present
        )
        
        # Split dimension blocks for Layout (Low vs High) to match template expectation
        # For bands: low_bands = ['160M', '80M', '40M']
        # For modes: low_modes = ['CW'] (typically first alphabetically)
        if dimension == 'mode':
            # For modes, we'll use a simple split: first half vs second half
            # Or we could use a specific list if needed
            mode_blocks = data[dimension_key] if dimension_key in data else []
            mid_point = len(mode_blocks) // 2
            low_bands_data = mode_blocks[:mid_point] if mid_point > 0 else mode_blocks
            high_bands_data = mode_blocks[mid_point:] if mid_point > 0 else []
        else:
            # Band dimension: use traditional low/high split
            low_bands = ['160M', '80M', '40M']
            low_bands_data = []
            high_bands_data = []
            
            for block in data[dimension_key]:
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

        # --- Pre-process Data for Display (Inject Missed & Global Max) ---
        global_max = {'total': 1, 'countries': 1, 'zones': 1} # Default 1 to avoid div/0
        
        # Function to process a list of rows
        def process_rows(rows_list):
            for row in rows_list:
                row_max = 0
                if row.get('stations'):
                    for stat in row['stations']:
                        # Inject 'missed' as absolute value of delta
                        stat['missed'] = abs(stat.get('delta', 0))

                        # Calc max unique for scaling
                        val = stat.get('unique_run', 0) + stat.get('unique_sp', 0) + stat.get('unique_unk', 0)
                        if val > row_max: row_max = val
                
                # Update global maxes based on row label keywords
                # Note: 'block_label' isn't available here, but we check row.label
                if row['label'] == 'TOTAL' or (row['label'] in ['160M', '80M', '40M', '20M', '15M', '10M']):
                    if row_max > global_max['total']: global_max['total'] = row_max
                elif 'Countries' in row['label']:
                    if row_max > global_max['countries']: global_max['countries'] = row_max
                elif 'Zones' in row['label']:
                    if row_max > global_max['zones']: global_max['zones'] = row_max

        # Process Totals
        if 'totals' in data:
            process_rows(data['totals'])

        # Process dimension blocks (bands or modes)
        if dimension_key in data:
            for block in data[dimension_key]:
                process_rows(block['rows'])

        # Sweepstakes-specific logic: Get total multiplier count from .dat file
        is_sweepstakes = False
        fixed_multiplier_max = None
        is_solo = (len(self.logs) == 1)
        multiplier_count = 0  # Count of multiplier types (excluding TOTAL row)
        # Reference line is now part of grid-lines-container, no height calculation needed
        
        if self.logs:
            contest_def = self.logs[0].contest_definition
            contest_name = contest_def.contest_name
            if contest_name and contest_name.startswith("ARRL-SS"):
                is_sweepstakes = True
                
                # Load total multiplier count from .dat file
                if data and 'totals' in data:
                    total_row = next((row for row in data['totals'] if row.get('label') == 'TOTAL'), None)
                    if total_row and total_row.get('stations'):
                        try:
                            # Get root input directory from kwargs or environment
                            root_input = kwargs.get('root_input_dir') or os.environ.get('CONTEST_INPUT_DIR', '/app/CONTEST_LOGS_REPORTS')
                            data_dir = os.path.join(root_input, 'data')
                            from contest_tools.contest_specific_annotations.arrl_ss_multiplier_resolver import SectionAliasLookup
                            alias_lookup = SectionAliasLookup(data_dir)
                            fixed_multiplier_max = alias_lookup.get_total_multiplier_count()
                        except Exception as e:
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.warning(f"Failed to load Sweepstakes multiplier count: {e}")
                            fixed_multiplier_max = None
            
            # Count multiplier types from breakdown_totals (excluding TOTAL row)
            if data and 'totals' in data:
                multiplier_count = len([row for row in data['totals'] if row.get('label') != 'TOTAL'])
                
                # Calculate reference line height for Sweepstakes
                if is_sweepstakes:
                    total_row = next((row for row in data['totals'] if row.get('label') == 'TOTAL'), None)
                    if total_row and total_row.get('stations'):
                        # Calculate reference line height: (number of bars * 40px per bar) + 8px margin
                        bar_count = len(total_row['stations'])
                        # Reference line is now part of grid-lines-container, automatically sized
        
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
            'is_sweepstakes': is_sweepstakes,
            'fixed_multiplier_max': fixed_multiplier_max,
            'is_solo': is_solo,
            'multiplier_count': multiplier_count,
            # Reference line is now part of grid-lines-container, automatically sized
        }

        # 3. Render Template
        html_content = render_to_string('html_multiplier_breakdown.html', context)

        # 4. Save File
        callsigns_part = build_callsigns_filename_part(all_calls)
        filename = f"html_multiplier_breakdown--{callsigns_part}.html"

        os.makedirs(output_path, exist_ok=True)
        filepath = os.path.join(output_path, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return f"Report saved to {filepath}"