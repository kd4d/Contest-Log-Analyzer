# contest_tools/reports/text_multiplier_timeline.py
#
# Purpose: A text report that generates a multiplier acquisition timeline showing
#          when new multipliers are first worked each hour.
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

from typing import List, Dict, Any
import os
from ..contest_log import ContestLog
from .report_interface import ContestReport
from contest_tools.utils.report_utils import format_text_header, get_standard_footer, get_standard_title_lines
from ..data_aggregators.time_series import TimeSeriesAggregator

class Report(ContestReport):
    """
    Generates a multiplier acquisition timeline showing hourly progression of new multipliers.
    Shows when each multiplier is first worked (count of new multipliers per hour).
    """
    report_id: str = "multiplier_timeline"
    report_name: str = "Multiplier Acquisition Timeline"
    report_type: str = "text"
    supports_single = True
    
    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content.
        """
        final_report_messages = []

        # --- Phase 1 Performance Optimization: Use Cached Aggregator Data ---
        get_cached_ts_data = kwargs.get('_get_cached_ts_data')
        if get_cached_ts_data:
            # Use cached time series data (avoids recreating aggregator and recomputing)
            ts_data = get_cached_ts_data()
        else:
            # Fallback to old behavior for backward compatibility
            agg = TimeSeriesAggregator(self.logs)
            ts_data = agg.get_time_series_data()
        time_bins = ts_data['time_bins']

        for log in self.logs:
            callsign = log.get_metadata().get('MyCall', 'UnknownCall')
            
            if callsign not in ts_data['logs']:
                print(f"Skipping multiplier timeline for {callsign}: No valid QSOs to report.")
                continue

            log_data = ts_data['logs'][callsign]
            scalars = log_data['scalars']
            
            if scalars['gross_qsos'] == 0:
                print(f"Skipping multiplier timeline for {callsign}: No valid QSOs to report.")
                continue

            year = scalars.get('year', "UnknownYear")
            contest_name = scalars.get('contest_name', 'UnknownContest')
            
            bands = log.contest_definition.valid_bands
            is_single_band = len(bands) == 1

            # Get hourly multiplier data
            hourly_data = log_data['hourly']
            new_mults_by_band = hourly_data.get('new_mults_by_band', {})
            cumulative_mults = hourly_data.get('cumulative_mults', [])

            # Check if we have multiplier data
            has_mult_data = False
            for band in bands:
                if band in new_mults_by_band and sum(new_mults_by_band[band]) > 0:
                    has_mult_data = True
                    break
            
            if not has_mult_data:
                print(f"Skipping multiplier timeline for {callsign}: No multiplier data available.")
                continue

            report_blocks = []

            # --- BLOCK 1: Overall Summary by Band ---
            # Columns: [Bands...] | Total New | Cumulative
            
            col_defs = []
            
            # 1. Band Columns (Only if multi-band)
            if not is_single_band:
                for b in bands:
                    col_defs.append({'key': f'band_{b}', 'header': b.replace('M',''), 'width': 5, 'type': 'band'})
            
            # 2. Totals
            col_defs.append({'key': 'hourly_total', 'header': 'New', 'width': 7, 'type': 'calc'})
            col_defs.append({'key': 'cumul_total', 'header': 'Cumul', 'width': 8, 'type': 'calc'})

            title_main = f"{year} {contest_name} - {callsign} - Multiplier Acquisition Timeline"
            block1 = self._build_table_block(
                title=title_main,
                col_defs=col_defs,
                time_bins=time_bins,
                new_mults_by_band=new_mults_by_band,
                cumulative_mults=cumulative_mults,
                bands=bands
            )
            report_blocks.append(block1)

            # --- Footer ---
            gross_qsos = scalars['gross_qsos']
            dupes = scalars['dupes']
            net_qsos = scalars['net_qsos']
            footer = f"Gross QSOs={gross_qsos}     Dupes={dupes}     Net QSOs={net_qsos}"

            # --- Generate Standard Header ---
            # Measure width from the first block
            block1_lines = block1.split('\n')
            table_width = len(block1_lines[3]) if len(block1_lines) > 3 else 80

            # Get available modes for title
            available_modes = sorted(list(hourly_data.get('by_mode', {}).keys()))
            if not available_modes:
                available_modes = ["QSO"]
            modes_present = set(available_modes)

            title_lines = get_standard_title_lines(self.report_name, [log], "All Bands", None, modes_present)
            meta_lines = ["Contest Log Analytics by KD4D"]
            header_block = format_text_header(table_width, title_lines, meta_lines)

            # --- Assembly ---
            standard_footer = get_standard_footer([log])
            full_content = "\n".join(header_block) + "\n\n" + "\n\n".join(report_blocks) + "\n\n" + footer + "\n\n" + standard_footer + "\n"
            
            os.makedirs(output_path, exist_ok=True)
            filename = f"{self.report_id}--{callsign}.txt"
            filepath = os.path.join(output_path, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            final_report_messages.append(f"Text report saved to: {filepath}")

        return "\n".join(final_report_messages)

    def _build_table_block(self, title, col_defs, time_bins, new_mults_by_band, cumulative_mults, bands):
        """
        Constructs a formatted text table block for multiplier timeline.
        """
        lines = []
        
        # 1. Headers
        header1_parts = [f"{'Hour':<5}"]
        
        for col in col_defs:
            w = col['width']
            header1_parts.append(f"{col['header']:>{w}}")
            
        header1 = " ".join(header1_parts)
        
        # 2. Width Calculation & Title Centering
        table_width = len(header1)
        separator = "-" * table_width
        
        # Center title relative to table width
        title_line = title.center(table_width)
        
        lines.append(title_line)
        lines.append("")
        lines.append(header1)
        lines.append(separator)
        
        # 3. Data Rows
        cumulative_total = 0
        
        # Pre-calculate column totals
        col_totals = {col['key']: 0 for col in col_defs}
        
        for i, time_iso in enumerate(time_bins):
            hour_str = time_iso[11:13] + time_iso[14:16]
            
            # Calculate row values
            row_vals = {}
            row_total = 0
            
            # Fetch data for this row
            for col in col_defs:
                key = col['key']
                ctype = col['type']
                val = 0
                
                if ctype == 'band':
                    # key = band_10M
                    b = key.replace('band_', '')
                    data_list = new_mults_by_band.get(b, [])
                    val = data_list[i] if i < len(data_list) else 0
                    row_vals[key] = val
                    row_total += val
            
            # Get cumulative total for this hour
            if i < len(cumulative_mults):
                cumulative_total = cumulative_mults[i]
            
            # Calculate row total (sum of all bands)
            if not row_vals:
                # Single band case - use cumulative difference
                if i == 0:
                    row_total = cumulative_total
                else:
                    prev_cumul = cumulative_mults[i-1] if i > 0 and i-1 < len(cumulative_mults) else 0
                    row_total = cumulative_total - prev_cumul
            else:
                # Multi-band case - sum of band values
                row_total = sum(row_vals.values())
            
            # Skip empty rows
            if row_total == 0 and cumulative_total == 0:
                continue

            # Build Line
            line_parts = [f"{hour_str:<5}"]
            
            for col in col_defs:
                key = col['key']
                w = col['width']
                ctype = col['type']
                
                display_val = 0
                
                if ctype == 'calc':
                    if key.startswith('hourly_total') or key.startswith('band_total'):
                        display_val = row_total
                    elif key.startswith('cumul_total') or key.startswith('band_cumul'):
                        display_val = cumulative_total
                else:
                    display_val = row_vals.get(key, 0)
                
                col_totals[key] += display_val
                
                line_parts.append(f"{display_val:>{w}}")
                
            lines.append(" ".join(line_parts))

        lines.append(separator)
        
        # 4. Total Line
        tot_parts = [f"{'Total':<5}"]
        for col in col_defs:
            key = col['key']
            w = col['width']
            # For cumulative column, show final cumulative value
            if col['type'] == 'calc' and 'cumul' in key:
                val = cumulative_total if cumulative_mults else 0
            else:
                val = col_totals[key]
                
            tot_parts.append(f"{val:>{w}}")
            
        lines.append(" ".join(tot_parts))
        
        return "\n".join(lines)
