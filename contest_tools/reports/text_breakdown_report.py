# contest_tools/reports/text_breakdown_report.py
#
# Purpose: Generates a WriteLog-style breakdown report showing QSO/Multiplier
#          activity by hour, broken down by band (or mode for single-band contests).
#          Derived from WriteLog Breakdown Report Format.
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

from typing import List, Dict, Set, Tuple
import pandas as pd
import os
import logging
from ..contest_log import ContestLog
from .report_interface import ContestReport
from contest_tools.utils.report_utils import format_text_header, get_standard_footer, get_valid_dataframe
from contest_tools.data_aggregators.time_series import TimeSeriesAggregator

logger = logging.getLogger(__name__)

class Report(ContestReport):
    """
    Generates a WriteLog-style breakdown report showing QSO/Multiplier by hour.
    """
    report_id: str = "breakdown_report"
    report_name: str = "QSO/Multiplier Breakdown by Hour"
    report_type: str = "text"
    supports_single = True
    
    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the breakdown report content.
        """
        final_report_messages = []

        for log in self.logs:
            metadata = log.get_metadata()
            callsign = metadata.get('MyCall', 'UnknownCall')
            contest_name = metadata.get('ContestName', 'UnknownContest')

            # Check for valid data
            df_full = get_valid_dataframe(log, include_dupes=True)  # For year extraction
            if df_full.empty:
                msg = f"Skipping breakdown report for {callsign}: No QSO data available."
                final_report_messages.append(msg)
                logger.warning(msg)
                continue

            # Determine dimension (band vs mode)
            contest_def = log.contest_definition
            valid_bands = contest_def.valid_bands
            valid_modes = getattr(contest_def, 'valid_modes', [])
            is_single_band = len(valid_bands) == 1
            is_multi_mode = len(valid_modes) > 1
            dimension = 'mode' if (is_single_band and is_multi_mode) else 'band'
            
            # Get multiplier names and combine them
            if contest_def.score_formula == 'total_points':
                mult_names = []
            else:
                mult_names = [rule['name'] for rule in contest_def.multiplier_rules]
            
            # Build multiplier label for header (e.g., "QSO/ZN+DX")
            if mult_names:
                mult_label = '+'.join(mult_names)
            else:
                mult_label = "Mults"
            
            # Get time series data from DAL
            ts_agg = TimeSeriesAggregator([log])
            ts_data = ts_agg.get_time_series_data()
            log_entry = ts_data['logs'].get(callsign, {})
            
            if not log_entry:
                msg = f"Skipping breakdown report for {callsign}: No time series data available."
                final_report_messages.append(msg)
                logger.warning(msg)
                continue
            
            # Get master time index from time_bins
            time_bins = ts_data.get('time_bins', [])
            if not time_bins:
                msg = f"Skipping breakdown report for {callsign}: No time bins available."
                final_report_messages.append(msg)
                logger.warning(msg)
                continue
            
            # Convert ISO strings back to DatetimeIndex for processing
            import pandas as pd
            master_index = pd.to_datetime(time_bins)
            
            # Get hourly QSO data from DAL
            hourly = log_entry.get('hourly', {})
            if dimension == 'mode':
                hourly_data = hourly.get('by_mode', {})
                hourly_new_mults = hourly.get('new_mults_by_mode', {})
                valid_dimensions = valid_modes if valid_modes else ['CW', 'SSB']  # Fallback
            else:
                hourly_data = hourly.get('by_band', {})
                hourly_new_mults = hourly.get('new_mults_by_band', {})
                valid_dimensions = valid_bands
            
            # Get cumulative data from DAL
            cumulative = log_entry.get('cumulative', {})
            cum_qsos = cumulative.get('qsos', [])
            cum_score = cumulative.get('score', [])
            
            # Use hourly cumulative_mults (combined all multiplier types)
            # This is more appropriate for breakdown report than cumulative.mults
            # which may respect totaling_method differently
            hourly_cum_mults = hourly.get('cumulative_mults', [])
            
            # Fallback to cumulative.mults if hourly not available
            if not hourly_cum_mults:
                hourly_cum_mults = cumulative.get('mults', [])
            
            # Extract year
            year = df_full['Date'].iloc[0].split('-')[0] if not df_full.empty and not df_full['Date'].dropna().empty else "----"
            
            # Build report
            report_lines = self._build_report_lines(
                year, contest_name, callsign, mult_label, dimension, valid_dimensions,
                master_index, hourly_data, hourly_new_mults, hourly_cum_mults,
                cum_qsos, cum_score, log=log
            )
            
            # Write file
            standard_footer = get_standard_footer([log])
            report_content = "\n".join(report_lines) + "\n\n" + standard_footer + "\n"
            os.makedirs(output_path, exist_ok=True)
            filename = f"{self.report_id}_{callsign.lower().replace('/', '-')}.txt"
            filepath = os.path.join(output_path, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            final_report_messages.append(f"Breakdown report saved to: {filepath}")

        return "\n".join(final_report_messages)
    
    
    def _build_report_lines(
        self, year: str, contest_name: str, callsign: str, mult_label: str,
        dimension: str, valid_dimensions: List[str], master_index: pd.DatetimeIndex,
        hourly_data: Dict[str, List[int]], hourly_new_mults: Dict[str, List[int]],
        hourly_cum_mults: List[int], cum_qsos: List[int], cum_score: List[int],
        log: ContestLog = None
    ) -> List[str]:
        """
        Builds the formatted report lines.
        """
        report_lines = []
        
        # Header
        title_lines = [
            f"--- {self.report_name} ---",
            f"{year} {contest_name} - {callsign}",
            f"Derived from WriteLog Breakdown Report Format"
        ]
        meta_lines = [f"QSO/{mult_label} by hour and {dimension}", "Contest Log Analytics by KD4D"]
        
        # Calculate column widths - need to account for QSO/Mult format (e.g., "1234/567")
        # Find max width needed for QSO/Mult pairs in each dimension
        max_qso_mult_width = 7  # Minimum width for "1234/567" format
        for dim in valid_dimensions:
            qsos_list = hourly_data.get(dim, [])
            mults_list = hourly_new_mults.get(dim, [])
            if qsos_list and mults_list:
                for qsos, mults in zip(qsos_list, mults_list):
                    pair_str = f"{qsos}/{mults}"
                    max_qso_mult_width = max(max_qso_mult_width, len(pair_str))
        
        # Also check totals
        for dim in valid_dimensions:
            qsos_list = hourly_data.get(dim, [])
            mults_list = hourly_new_mults.get(dim, [])
            if qsos_list and mults_list:
                total_qsos = sum(qsos_list)
                total_mults = sum(mults_list)
                pair_str = f"{total_qsos}/{total_mults}"
                max_qso_mult_width = max(max_qso_mult_width, len(pair_str))
        
        # Ensure column width is at least as wide as the dimension name
        dim_col_width = max(max_qso_mult_width, max(len(dim) for dim in valid_dimensions) if valid_dimensions else 6)
        dim_col_width = max(dim_col_width, 7)  # Minimum 7 for "Total" and QSO/Mult format
        
        # Pre-calculate CUMM and Score column widths by scanning ALL rows
        max_cumm_width = len("Cumm")  # Minimum width for header
        max_score_width = len("Score")  # Minimum width for header
        
        for hour_idx in range(len(master_index)):
            # Check CUMM width
            cum_qso = cum_qsos[hour_idx] if hour_idx < len(cum_qsos) else 0
            cum_mult = hourly_cum_mults[hour_idx] if hour_idx < len(hourly_cum_mults) else 0
            cum_pair_str = f"{cum_qso}/{cum_mult}"
            max_cumm_width = max(max_cumm_width, len(cum_pair_str))
            
            # Check Score width (with comma formatting)
            score = cum_score[hour_idx] if hour_idx < len(cum_score) else 0
            score_str = f"{score:,}"
            max_score_width = max(max_score_width, len(score_str))
        
        # Add one space padding to CUMM and Score columns for readability
        cumm_col_width = max_cumm_width + 1
        score_col_width = max_score_width + 1
        
        # Build header row
        header_parts = [f"{'Hour':<10}"]
        for dim in valid_dimensions:
            header_parts.append(f"{dim:>{dim_col_width}}")
        header_parts.extend([
            f"{'Total':>{dim_col_width}}", 
            f"{'Cumm':>{cumm_col_width}}", 
            f"{'Score':>{score_col_width}}"
        ])
        header = "  ".join(header_parts)
        table_width = len(header)
        
        report_lines.extend(format_text_header(table_width, title_lines, meta_lines))
        report_lines.append("")
        report_lines.append(header)
        report_lines.append("")
        
        # Data rows
        for hour_idx, hour_ts in enumerate(master_index):
            # Format hour label (D{day}-{HHMM}Z)
            day_num = (hour_ts.date() - master_index[0].date()).days + 1
            hour_label = f"D{day_num}-{hour_ts.strftime('%H%M')}Z"
            
            # Get QSOs and multipliers for each dimension
            row_parts = [f"{hour_label:<10}"]
            total_qsos = 0
            total_mults = 0
            
            for dim in valid_dimensions:
                qsos_list = hourly_data.get(dim, [])
                mults_list = hourly_new_mults.get(dim, [])
                qsos = qsos_list[hour_idx] if hour_idx < len(qsos_list) else 0
                mults = mults_list[hour_idx] if hour_idx < len(mults_list) else 0
                total_qsos += qsos
                total_mults += mults
                
                if qsos == 0 and mults == 0:
                    row_parts.append(f"{'  -  ':>{dim_col_width}}")
                else:
                    pair_str = f"{qsos}/{mults}"
                    row_parts.append(f"{pair_str:>{dim_col_width}}")
            
            # Total for hour
            if total_qsos == 0 and total_mults == 0:
                row_parts.append(f"{'  -  ':>{dim_col_width}}")
            else:
                total_pair_str = f"{total_qsos}/{total_mults}"
                row_parts.append(f"{total_pair_str:>{dim_col_width}}")
            
            # Cumulative
            cum_qso = cum_qsos[hour_idx] if hour_idx < len(cum_qsos) else 0
            cum_mult = hourly_cum_mults[hour_idx] if hour_idx < len(hourly_cum_mults) else 0
            cum_pair_str = f"{cum_qso}/{cum_mult}"
            row_parts.append(f"{cum_pair_str:>{cumm_col_width}}")
            
            # Score
            score = cum_score[hour_idx] if hour_idx < len(cum_score) else 0
            score_str = f"{score:,}"
            row_parts.append(f"{score_str:>{score_col_width}}")
            
            report_lines.append("  ".join(row_parts))
        
        # Footer - Totals by dimension
        report_lines.append("")
        report_lines.append("Totals:")
        total_row_parts = [f"{'':<10}"]
        
        # Calculate totals per dimension
        total_breakdown_mults = 0
        total_qsos_sum = 0
        for dim in valid_dimensions:
            qsos_list = hourly_data.get(dim, [])
            mults_list = hourly_new_mults.get(dim, [])
            dim_qsos = sum(qsos_list) if qsos_list else 0
            dim_mults = sum(mults_list) if mults_list else 0
            total_qsos_sum += dim_qsos
            total_breakdown_mults += dim_mults
            total_pair_str = f"{dim_qsos}/{dim_mults}"
            total_row_parts.append(f"{total_pair_str:>{dim_col_width}}")
        
        # Add Total column (sum of all dimension QSOs/mults)
        total_pair_str = f"{total_qsos_sum}/{total_breakdown_mults}"
        total_row_parts.append(f"{total_pair_str:>{dim_col_width}}")
        
        # Add CUMM column (final cumulative QSOs/mults)
        if cum_qsos and hourly_cum_mults:
            final_cum_qsos = cum_qsos[-1] if len(cum_qsos) > 0 else 0
            final_cum_mults = hourly_cum_mults[-1] if len(hourly_cum_mults) > 0 else 0
            cum_pair_str = f"{final_cum_qsos}/{final_cum_mults}"
            total_row_parts.append(f"{cum_pair_str:>{cumm_col_width}}")
        else:
            total_row_parts.append(f"{'  -  ':>{cumm_col_width}}")
        
        # Add Score column (final cumulative score)
        if cum_score:
            final_score = cum_score[-1] if len(cum_score) > 0 else 0
            score_str = f"{final_score:,}"
            total_row_parts.append(f"{score_str:>{score_col_width}}")
        else:
            total_row_parts.append(f"{'  -  ':>{score_col_width}}")
        
        report_lines.append("  ".join(total_row_parts))
        
        return report_lines
