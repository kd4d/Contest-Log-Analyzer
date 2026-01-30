# contest_tools/reports/text_rate_sheet.py
#
# Purpose: A text report that generates a detailed hourly rate sheet.
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
import pandas as pd
import os
from ..contest_log import ContestLog
from .report_interface import ContestReport
from contest_tools.utils.report_utils import format_text_header, get_standard_footer, get_standard_title_lines
from ..data_aggregators.time_series import TimeSeriesAggregator
from ..utils.callsign_utils import callsign_to_filename_part

class Report(ContestReport):
    """
    Generates a detailed hourly rate sheet for each log with mode breakdowns.
    """
    report_id: str = "rate_sheet"
    report_name: str = "Hourly Rate Sheet"
    report_type: str = "text"
    supports_single = True
    
    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content. When contest uses points-based scoring,
        produces both QSO and Points variants (like cumulative difference plots).
        """
        include_dupes = kwargs.get('include_dupes', False)
        final_report_messages = []

        # --- Phase 1 Performance Optimization: Use Cached Aggregator Data ---
        get_cached_ts_data = kwargs.get('_get_cached_ts_data')
        if get_cached_ts_data:
            ts_data = get_cached_ts_data()
        else:
            agg = TimeSeriesAggregator(self.logs)
            ts_data = agg.get_time_series_data()
        time_bins = ts_data['time_bins']

        # Determine metrics: always QSOs; add Points when contest uses points-based scoring
        metrics_to_run = ['qsos']
        if self.logs:
            contest_def = self.logs[0].contest_definition
            score_formula = getattr(contest_def, 'score_formula', None) or contest_def._data.get('score_formula', 'points_times_mults')
            if score_formula in ('total_points', 'points_times_mults'):
                metrics_to_run.append('points')

        for metric in metrics_to_run:
            report_id_suffix = '_qsos' if metric == 'qsos' else '_points'
            report_name_metric = (self.report_name + ' (QSOs)') if metric == 'qsos' else (self.report_name + ' (Points)')
            for log in self.logs:
                callsign = log.get_metadata().get('MyCall', 'UnknownCall')

                if callsign not in ts_data['logs']:
                    print(f"Skipping rate sheet for {callsign}: No valid QSOs to report.")
                    continue

                log_data = ts_data['logs'][callsign]
                scalars = log_data['scalars']

                if scalars['gross_qsos'] == 0:
                    print(f"Skipping rate sheet for {callsign}: No valid QSOs to report.")
                    continue

                year = scalars.get('year', "UnknownYear")
                contest_name = scalars.get('contest_name', 'UnknownContest')

                bands = log.contest_definition.valid_bands
                is_single_band = len(bands) == 1

                hourly_data = log_data['hourly']
                if metric == 'qsos':
                    available_modes = sorted(list(hourly_data.get('by_mode', {}).keys()))
                else:
                    available_modes = sorted(list(hourly_data.get('by_mode_points', {}).keys()))
                if not available_modes:
                    available_modes = ["QSO"] if metric == 'qsos' else ["Pts"]

                modes_present = set(available_modes)
                is_single_mode = len(available_modes) == 1

                report_blocks = []

                col_defs = []
                if not is_single_band:
                    for b in bands:
                        col_defs.append({'key': f'band_{b}', 'header': b.replace('M', ''), 'width': 5, 'type': 'band'})
                for m in available_modes:
                    col_defs.append({'key': f'mode_{m}', 'header': m, 'width': 5, 'type': 'mode'})
                col_defs.append({'key': 'hourly_total', 'header': 'Total', 'width': 7, 'type': 'calc'})
                col_defs.append({'key': 'cumul_total', 'header': 'Cumul', 'width': 8, 'type': 'calc'})

                title_main = f"{year} {contest_name} - {callsign} (All Bands)"
                block1 = self._build_table_block(
                    title=title_main,
                    col_defs=col_defs,
                    time_bins=time_bins,
                    data_source=hourly_data,
                    bands=bands,
                    available_modes=available_modes,
                    metric=metric
                )
                report_blocks.append(block1)

                if not is_single_band and not is_single_mode and metric == 'qsos':
                    for band in bands:
                        band_qsos = hourly_data['by_band'].get(band, [])
                        if sum(band_qsos) == 0:
                            continue
                        active_modes_on_band = set()
                        for key in hourly_data.get('by_band_mode', {}).keys():
                            if key.startswith(f"{band}_"):
                                parts = key.split('_')
                                if len(parts) >= 2:
                                    active_modes_on_band.add(parts[1])
                        if len(active_modes_on_band) <= 1:
                            continue
                        detail_col_defs = []
                        for m in available_modes:
                            detail_col_defs.append({'key': f'bm_{band}_{m}', 'header': m, 'width': 5, 'type': 'band_mode'})
                        detail_col_defs.append({'key': f'band_total_{band}', 'header': 'Total', 'width': 7, 'type': 'calc'})
                        detail_col_defs.append({'key': f'band_cumul_{band}', 'header': 'Cumul', 'width': 8, 'type': 'calc'})
                        block_detail = self._build_table_block(
                            title=f"Detail: {band}",
                            col_defs=detail_col_defs,
                            time_bins=time_bins,
                            data_source=hourly_data,
                            bands=[band],
                            available_modes=available_modes,
                            force_band_context=band,
                            metric=metric
                        )
                        report_blocks.append(block_detail)

                if metric == 'qsos':
                    gross_qsos = scalars['gross_qsos']
                    dupes = scalars['dupes']
                    net_qsos = scalars['net_qsos']
                    display_net = gross_qsos if include_dupes else net_qsos
                    footer = f"Gross QSOs={gross_qsos}     Dupes={dupes}     Net QSOs={display_net}"
                else:
                    footer = f"Total Points={scalars.get('points_sum', 0):,}"

                block1_lines = block1.split('\n')
                table_width = len(block1_lines[3]) if len(block1_lines) > 3 else 80
                title_lines = get_standard_title_lines(report_name_metric, [log], "All Bands", None, modes_present)
                meta_lines = ["Contest Log Analytics by KD4D"]
                header_block = format_text_header(table_width, title_lines, meta_lines)

                standard_footer = get_standard_footer([log])
                full_content = "\n".join(header_block) + "\n\n" + "\n\n".join(report_blocks) + "\n\n" + footer + "\n\n" + standard_footer + "\n"

                os.makedirs(output_path, exist_ok=True)
                filename = f"{self.report_id}{report_id_suffix}--{callsign_to_filename_part(callsign)}.txt"
                filepath = os.path.join(output_path, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(full_content)

                final_report_messages.append(f"Text report saved to: {filepath}")

        return "\n".join(final_report_messages)

    def _build_table_block(self, title, col_defs, time_bins, data_source, bands, available_modes, force_band_context=None, metric='qsos'):
        """
        Constructs a formatted text table block.
        metric: 'qsos' or 'points' — selects by_band/by_mode/qsos vs by_band_points/by_mode_points/points.
        """
        lines = []
        
        # 1. Headers
        header1_parts = [f"{'Hour':<5}"]
        header2_parts = [f"{'':<5}"]
        
        for col in col_defs:
            w = col['width']
            header1_parts.append(f"{col['header']:>{w}}")
            header2_parts.append(f"{'':>{w}}") # Underline spacer or second line if needed
            
        header1 = " ".join(header1_parts)
        header2 = " ".join(header2_parts)
        
        # 2. Width Calculation & Title Centering
        table_width = len(header1)
        separator = "-" * table_width
        
        # Center title relative to table width (Left Anchor 0)
        title_line = title.center(table_width)
        
        lines.append(title_line)
        lines.append("")
        lines.append(header1)
        # lines.append(header2) # Optional, usually redundant if header1 is clear
        lines.append(separator)
        
        # 3. Data Rows
        cumulative_total = 0
        
        # Pre-calculate column totals
        col_totals = {col['key']: 0 for col in col_defs}
        
        for i, time_iso in enumerate(time_bins):
            hour_str = time_iso[11:13] + time_iso[14:16]
            
            # Calculate row values first to determine if we skip (skip empty rows)
            row_vals = {}
            row_total = 0
            
            # Fetch data for this row
            for col in col_defs:
                key = col['key']
                ctype = col['type']
                val = 0
                
                if ctype == 'band':
                    b = key.replace('band_', '')
                    band_key = 'by_band_points' if metric == 'points' else 'by_band'
                    data_list = data_source.get(band_key, {}).get(b, [])
                    val = data_list[i] if data_list else 0
                elif ctype == 'mode':
                    m = key.replace('mode_', '')
                    if metric == 'points' and m == 'Pts':
                        data_list = data_source.get('points', [])
                        val = data_list[i] if data_list else 0
                    else:
                        mode_key = 'by_mode_points' if metric == 'points' else 'by_mode'
                        data_list = data_source.get(mode_key, {}).get(m, [])
                        val = data_list[i] if data_list else 0

                if force_band_context: 
                        # This should theoretically not happen in Summary block, 
                        # but if mode column used in detail block, it maps to band_mode
                    pass
                elif ctype == 'band_mode':
                    # key = bm_10M_CW
                    # lookup in by_band_mode
                    lookup_key = key.replace('bm_', '')
                    data_list = data_source['by_band_mode'].get(lookup_key, [])
                    val = data_list[i] if data_list else 0
                
                # 'calc' types (Totals) are derived below
                if ctype not in ['calc']:
                    row_vals[key] = val
            
            # Calculate Row Total
            total_key = 'points' if metric == 'points' else 'qsos'
            if force_band_context:
                row_total = sum(row_vals.values())
            else:
                row_total = data_source.get(total_key, [0] * len(time_bins))[i] if i < len(data_source.get(total_key, [])) else 0

            if row_total > 0:
                cumulative_total += row_total

            # Build Line (show every hour; use "-" for empty/zero data; keep hour and cumulative populated)
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

                # Empty/zero data: show "-"; cumulative and structural columns always show value
                is_cumul = ctype == 'calc' and ('cumul' in key or 'band_cumul' in key)
                if not is_cumul and display_val == 0:
                    line_parts.append(f"{'-':>{w}}")
                else:
                    line_parts.append(f"{display_val:>{w}}")
                
            lines.append(" ".join(line_parts))

        lines.append(separator)
        
        # 4. Total Line
        tot_parts = [f"{'Total':<5}"]
        for col in col_defs:
            key = col['key']
            w = col['width']
            # For cumulative column, show Grand Total or Empty? Usually Grand Total.
            val = col_totals[key]
            # Cumulative column total in a 'Total' row is meaningless/redundant usually, 
            # but legacy often puts the final cumulative there.
            if col['type'] == 'calc' and 'cumul' in key:
                 val = cumulative_total
                 
            tot_parts.append(f"{val:>{w}}")
            
        lines.append(" ".join(tot_parts))
        
        return "\n".join(lines)