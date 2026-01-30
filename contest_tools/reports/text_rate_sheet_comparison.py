# contest_tools/reports/text_rate_sheet_comparison.py
#
# Purpose: A text report that generates a comparative hourly rate sheet for two or more logs.
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
import pandas as pd
import os
from ..contest_log import ContestLog
from .report_interface import ContestReport
from ..data_aggregators.time_series import TimeSeriesAggregator
from contest_tools.utils.report_utils import _sanitize_filename_part, format_text_header, get_standard_footer, get_standard_title_lines
from contest_tools.utils.callsign_utils import build_callsigns_filename_part

class Report(ContestReport):
    """
    Generates a comparative hourly rate sheet for two or more logs.
    """
    report_id: str = "rate_sheet_comparison"
    report_name: str = "Comparative Rate Sheet"
    report_type: str = "text"
    supports_multi = True
    supports_pairwise = True
    
    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content. When contest uses points-based scoring,
        produces both QSO and Points variants (like single-log rate sheets).
        """
        if len(self.logs) < 2:
            return "Error: The Comparative Rate Sheet report requires at least two logs."

        all_calls = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in self.logs])
        first_log = self.logs[0]
        contest_def = first_log.contest_definition
        bands = contest_def.valid_bands
        is_single_band = len(bands) == 1

        get_cached_ts_data = kwargs.get('_get_cached_ts_data')
        if get_cached_ts_data:
            ts_data = get_cached_ts_data()
        else:
            agg = TimeSeriesAggregator(self.logs)
            ts_data = agg.get_time_series_data()
        time_bins = ts_data['time_bins']

        # Determine metrics: always QSOs; add Points when contest uses points-based scoring
        metrics_to_run = ['qsos']
        score_formula = getattr(contest_def, 'score_formula', None) or contest_def._data.get('score_formula', 'points_times_mults')
        if score_formula in ('total_points', 'points_times_mults'):
            metrics_to_run.append('points')

        callsigns_part = build_callsigns_filename_part(sorted(all_calls))
        created = []

        for metric in metrics_to_run:
            report_id_suffix = '_qsos' if metric == 'qsos' else '_points'
            report_name_metric = (self.report_name + ' (QSOs)') if metric == 'qsos' else (self.report_name + ' (Points)')

            if metric == 'qsos':
                global_modes = set()
                for call in all_calls:
                    entry = ts_data['logs'].get(call)
                    if entry:
                        global_modes.update(entry['hourly'].get('by_mode', {}).keys())
                available_modes = sorted(list(global_modes))
            else:
                global_modes = set()
                for call in all_calls:
                    entry = ts_data['logs'].get(call)
                    if entry:
                        global_modes.update(entry['hourly'].get('by_mode_points', {}).keys())
                available_modes = sorted(list(global_modes))
            if not available_modes:
                available_modes = ['QSO'] if metric == 'qsos' else ['Pts']

            is_single_mode = len(available_modes) == 1
            modes_present = set(available_modes)

            col_defs = []
            if not is_single_band:
                for b in bands:
                    col_defs.append({'key': f'band_{b}', 'header': b.replace('M', ''), 'width': 6, 'type': 'band'})
            else:
                for m in available_modes:
                    col_defs.append({'key': f'mode_{m}', 'header': m, 'width': 5, 'type': 'mode'})
            col_defs.append({'key': 'total', 'header': 'Total', 'width': 7, 'type': 'calc'})
            col_defs.append({'key': 'cumul', 'header': 'Cumul', 'width': 8, 'type': 'calc'})

            report_blocks = []
            block1 = self._build_comparison_block(
                title="Overall Summary",
                col_defs=col_defs,
                time_bins=time_bins,
                ts_data=ts_data,
                all_calls=all_calls,
                force_band_context=None,
                metric=metric
            )
            report_blocks.append(block1)

            if not is_single_band and not is_single_mode and metric == 'qsos':
                for band in bands:
                    has_data = False
                    for call in all_calls:
                        entry = ts_data['logs'].get(call)
                        if entry and sum(entry['hourly']['by_band'].get(band, [])) > 0:
                            has_data = True
                            break
                    if not has_data:
                        continue
                    active_modes_on_band = set()
                    for call in all_calls:
                        entry = ts_data['logs'].get(call)
                        if entry:
                            for key in entry['hourly'].get('by_band_mode', {}).keys():
                                if key.startswith(f"{band}_"):
                                    parts = key.split('_')
                                    if len(parts) >= 2:
                                        active_modes_on_band.add(parts[1])
                    if len(active_modes_on_band) <= 1:
                        continue
                    detail_defs = []
                    for m in available_modes:
                        detail_defs.append({'key': f'bm_{band}_{m}', 'header': m, 'width': 5, 'type': 'band_mode'})
                    detail_defs.append({'key': 'total', 'header': 'Total', 'width': 7, 'type': 'calc'})
                    detail_defs.append({'key': 'cumul', 'header': 'Cumul', 'width': 8, 'type': 'calc'})
                    block_detail = self._build_comparison_block(
                        title=f"Detail: {band}",
                        col_defs=detail_defs,
                        time_bins=time_bins,
                        ts_data=ts_data,
                        all_calls=all_calls,
                        force_band_context=band,
                        metric=metric
                    )
                    report_blocks.append(block_detail)

            block1_lines = block1.split('\n')
            table_width = len(block1_lines[3]) if len(block1_lines) > 3 else 80
            title_lines = get_standard_title_lines(report_name_metric, self.logs, "All Bands", None, modes_present)
            meta_lines = ["Contest Log Analytics by KD4D"]
            header_block = format_text_header(table_width, title_lines, meta_lines)
            standard_footer = get_standard_footer(self.logs)
            full_content = "\n".join(header_block) + "\n\n" + "\n\n".join(report_blocks) + "\n\n" + standard_footer + "\n"

            os.makedirs(output_path, exist_ok=True)
            filename = f"{self.report_id}{report_id_suffix}--{callsigns_part}.txt"
            filepath = os.path.join(output_path, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_content)
            created.append(filepath)

        return "\n".join([f"Text report saved to: {fp}" for fp in created])

    def _build_comparison_block(self, title, col_defs, time_bins, ts_data, all_calls, force_band_context=None, metric='qsos'):
        lines = []
        total_key = 'points' if metric == 'points' else 'qsos'
        band_key = 'by_band_points' if metric == 'points' else 'by_band'
        mode_key = 'by_mode_points' if metric == 'points' else 'by_mode'

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

        cumul_trackers = {call: 0 for call in all_calls}
        grand_totals = {call: {col['key']: 0 for col in col_defs} for call in all_calls}

        for i, time_iso in enumerate(time_bins):
            hour_str = time_iso[11:13] + time_iso[14:16]
            hour_has_data = False
            row_data_cache = {}
            row_totals_cache = {}

            for call in all_calls:
                row_vals = {}
                row_total = 0
                entry = ts_data['logs'].get(call)

                if entry:
                    hourly = entry['hourly']
                    for col in col_defs:
                        key = col['key']
                        ctype = col['type']
                        val = 0
                        if ctype == 'band':
                            b = key.replace('band_', '')
                            data_list = hourly.get(band_key, {}).get(b, [])
                            val = data_list[i] if data_list else 0
                        elif ctype == 'mode':
                            lookup = key.replace('mode_', '')
                            if metric == 'points' and lookup == 'Pts':
                                data_list = hourly.get('points', [])
                                val = data_list[i] if data_list and i < len(data_list) else 0
                            else:
                                data_list = hourly.get(mode_key, {}).get(lookup, [])
                                val = data_list[i] if data_list else 0
                        elif ctype == 'band_mode':
                            lookup = key.replace('bm_', '')
                            data_list = hourly.get('by_band_mode', {}).get(lookup, [])
                            val = data_list[i] if data_list else 0
                        if ctype != 'calc':
                            row_vals[key] = val
                            row_total += val
                    if force_band_context is None:
                        row_total = (hourly.get(total_key) or [0] * len(time_bins))[i] if i < len(hourly.get(total_key) or []) else row_total
                row_data_cache[call] = row_vals
                row_totals_cache[call] = row_total
                if row_total > 0:
                    hour_has_data = True
            
            if not hour_has_data:
                continue
                
            # Print Rows (One per call)
            # Lines format: "HHMM  Call  ..."
            first_call_line = True
            for call in all_calls:
                t_str = hour_str if first_call_line else "     "
                # Let's repeat time for scannability or use " " 
                
                # Update Cumulative
                r_total = row_totals_cache[call]
                cumul_trackers[call] += r_total
                
                line_parts = [f"{t_str:<5}", f"{call:<7}"]
                
                for col in col_defs:
                    key = col['key']
                    w = col['width']
                    ctype = col['type']
                    
                    val = 0
                    if ctype == 'calc':
                        if key == 'total': val = r_total
                        elif key == 'cumul': val = cumul_trackers[call]
                    else:
                        val = row_data_cache[call].get(key, 0)
            
                    grand_totals[call][key] += val
                    if ctype == 'calc' and key == 'cumul':
                        grand_totals[call][key] = val # Keep latest
                        
                    line_parts.append(f"{val:>{w}}")
                    
                lines.append(" ".join(line_parts))

                first_call_line = False
            
            # Optional spacer between hours?
            # lines.append("") 

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