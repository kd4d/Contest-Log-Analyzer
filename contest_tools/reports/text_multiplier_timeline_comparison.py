# contest_tools/reports/text_multiplier_timeline_comparison.py
#
# Purpose: A text report that generates a comparative multiplier acquisition timeline
#          for two or more logs, showing when new multipliers are first worked each hour.
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

from typing import List
import os
from ..contest_log import ContestLog
from .report_interface import ContestReport
from ..data_aggregators.time_series import TimeSeriesAggregator
from contest_tools.utils.report_utils import _sanitize_filename_part, format_text_header, get_standard_footer, get_standard_title_lines
from contest_tools.utils.callsign_utils import build_callsigns_filename_part

class Report(ContestReport):
    """
    Generates a comparative multiplier acquisition timeline for two or more logs.
    Shows hourly progression of new multipliers (when each multiplier is first worked).
    """
    report_id: str = "multiplier_timeline_comparison"
    report_name: str = "Comparative Multiplier Acquisition Timeline"
    report_type: str = "text"
    supports_multi = True
    supports_pairwise = True
    
    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content, saves it to a file, and returns a summary.
        """
        if len(self.logs) < 2:
            return "Error: The Comparative Multiplier Acquisition Timeline report requires at least two logs."
        
        all_calls = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in self.logs])
        first_log = self.logs[0]
        contest_def = first_log.contest_definition
        bands = contest_def.valid_bands
        is_single_band = len(bands) == 1
        
        # Data Aggregation
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
        
        # Determine available modes globally across all logs
        global_modes = set()
        for call in all_calls:
            entry = ts_data['logs'].get(call)
            if entry:
                global_modes.update(entry['hourly'].get('by_mode', {}).keys())
        available_modes = sorted(list(global_modes))
        if not available_modes: 
            available_modes = ['QSO']

        report_blocks = []

        # --- BLOCK 1: Overall Summary ---
        # Columns: [Bands...] | [New] | [Cumul]
        
        col_defs = []
        if not is_single_band:
            for b in bands:
                col_defs.append({'key': f'band_{b}', 'header': b.replace('M',''), 'width': 6, 'type': 'band'})
        else:
            # Single band: Show mode columns instead
            for m in available_modes:
                col_defs.append({'key': f'mode_{m}', 'header': m, 'width': 5, 'type': 'mode'})

        col_defs.append({'key': 'total', 'header': 'New', 'width': 7, 'type': 'calc'})
        col_defs.append({'key': 'cumul', 'header': 'Cumul', 'width': 8, 'type': 'calc'})

        # --- Extract Metadata from DAL Scalars (Safe Access) ---
        first_call = all_calls[0]
        first_log_scalars = ts_data['logs'].get(first_call, {}).get('scalars', {})
        
        contest_name = first_log_scalars.get('contest_name', 'UnknownContest')
        year = first_log_scalars.get('year', '----')
        
        # Calculate modes present for smart scoping
        modes_present = set(available_modes)

        block1 = self._build_comparison_block(
            title="Overall Summary",
            col_defs=col_defs,
            time_bins=time_bins,
            ts_data=ts_data,
            all_calls=all_calls,
            bands=bands,
            is_single_band=is_single_band,
            available_modes=available_modes
        )
        report_blocks.append(block1)
        
        # --- Generate Standard Header ---
        # Measure width from the first block
        block1_lines = block1.split('\n')
        table_width = len(block1_lines[3]) if len(block1_lines) > 3 else 80
        
        title_lines = get_standard_title_lines(self.report_name, self.logs, "All Bands", None, modes_present)
        meta_lines = ["Contest Log Analytics by KD4D"]
        
        header_block = format_text_header(table_width, title_lines, meta_lines)
        
        # Prepend header to blocks and append standard footer
        standard_footer = get_standard_footer(self.logs)
        full_content = "\n".join(header_block) + "\n\n" + "\n\n".join(report_blocks) + "\n\n" + standard_footer + "\n"

        # --- Output ---
        
        os.makedirs(output_path, exist_ok=True)
        callsigns_part = build_callsigns_filename_part(sorted(all_calls))
        filename = f"{self.report_id}--{callsigns_part}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        return f"Text report saved to: {filepath}"

    def _build_comparison_block(self, title, col_defs, time_bins, ts_data, all_calls, bands, is_single_band, available_modes):
        lines = []
        
        # 1. Header Construction
        # Header Format:
        # Time   Call     [Cols...]
        
        header1_parts = [f"{'Hour':<5}", f"{'Call':<7}"]
        for col in col_defs:
            w = col['width']
            header1_parts.append(f"{col['header']:>{w}}")
            
        header1 = " ".join(header1_parts)
        table_width = len(header1)
        separator = "-" * table_width
        
        lines.append(title.center(table_width))
        lines.append("")
        lines.append(header1)
        lines.append(separator)
        
        # 2. State Tracking
        # Need cumulative totals per call
        cumul_trackers = {call: 0 for call in all_calls}
        grand_totals = {call: {col['key']: 0 for col in col_defs} for call in all_calls}

        # 3. Iterate Time
        for i, time_iso in enumerate(time_bins):
            hour_str = time_iso[11:13] + time_iso[14:16]
            
            row_data_cache = {}  # Map call -> {col_key: val}
            row_totals_cache = {}  # Map call -> total
            cumulative_cache = {}  # Map call -> cumulative

            for call in all_calls:
                row_vals = {}
                row_total = 0
                entry = ts_data['logs'].get(call)
                
                if entry:
                    hourly = entry['hourly']
                    new_mults_by_band = hourly.get('new_mults_by_band', {})
                    cumulative_mults = hourly.get('cumulative_mults', [])
                    
                    # Get cumulative for this hour
                    if i < len(cumulative_mults):
                        cumulative_cache[call] = cumulative_mults[i]
                    else:
                        cumulative_cache[call] = 0
                    
                    for col in col_defs:
                        key = col['key']
                        ctype = col['type']
                        val = 0
                        
                        if ctype == 'band':
                            b = key.replace('band_', '')
                            data_list = new_mults_by_band.get(b, [])
                            val = data_list[i] if i < len(data_list) else 0
                        elif ctype == 'mode':
                            # For single-band mode, we don't have mode-specific multiplier data
                            # Use band data instead (since it's single band)
                            if bands:
                                b = bands[0]
                                data_list = new_mults_by_band.get(b, [])
                                val = data_list[i] if i < len(data_list) else 0
                        
                        if ctype != 'calc':
                            row_vals[key] = val
                            row_total += val
                    
                    # Calculate row total
                    if not row_vals:
                        # Single band case - calculate from cumulative difference
                        if i == 0:
                            row_total = cumulative_cache[call]
                        else:
                            prev_cumul = cumulative_mults[i-1] if i > 0 and i-1 < len(cumulative_mults) else 0
                            row_total = cumulative_cache[call] - prev_cumul
                    else:
                        # Multi-band case - sum of band values
                        row_total = sum(row_vals.values())
                else:
                    # Missing log
                    cumulative_cache[call] = 0
                
                row_data_cache[call] = row_vals
                row_totals_cache[call] = row_total

            # Print Rows (One per call) - show every hour; use "-" for empty data; keep hour, call, cumulative populated
            first_call_line = True
            for call in all_calls:
                t_str = hour_str if first_call_line else "     "

                r_total = row_totals_cache[call]
                cumul_trackers[call] = cumulative_cache[call]

                line_parts = [f"{t_str:<5}", f"{call:<7}"]

                for col in col_defs:
                    key = col['key']
                    w = col['width']
                    ctype = col['type']

                    val = 0
                    if ctype == 'calc':
                        if key == 'total':
                            val = r_total
                        elif key == 'cumul':
                            val = cumul_trackers[call]
                    else:
                        val = row_data_cache[call].get(key, 0)

                    grand_totals[call][key] += val
                    if ctype == 'calc' and key == 'cumul':
                        grand_totals[call][key] = val  # Keep latest

                    # Empty/zero data: show "-"; cumulative always shows value
                    if ctype == 'calc' and key == 'cumul':
                        line_parts.append(f"{val:>{w}}")
                    elif val == 0:
                        line_parts.append(f"{'-':>{w}}")
                    else:
                        line_parts.append(f"{val:>{w}}")

                lines.append(" ".join(line_parts))

                first_call_line = False

        lines.append(separator)
        
        # 4. Totals
        lines.append("TOTALS")
        for call in all_calls:
            line_parts = [f"{'':<5}", f"{call:<7}"]
            for col in col_defs:
                key = col['key']
                w = col['width']
                val = grand_totals[call][key]
                line_parts.append(f"{val:>{w}}")
            lines.append(" ".join(line_parts))

        return "\n".join(lines)
