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
from contest_tools.utils.callsign_utils import callsign_to_filename_part

logger = logging.getLogger(__name__)

def _calculate_inactive_time_per_hour(
    log: ContestLog, 
    master_index: pd.DatetimeIndex
) -> Dict[pd.Timestamp, int]:
    """
    Calculate inactive time (15+ minutes without QSOs) per hour.
    
    Returns a dictionary mapping hour timestamps to minutes of inactive time.
    Only includes hours with inactive time > 0.
    """
    from contest_tools.utils.report_utils import get_valid_dataframe
    
    # Get all QSO datetimes (non-dupes only for inactive time calculation)
    df = get_valid_dataframe(log, include_dupes=False)
    if df.empty or 'Datetime' not in df.columns:
        return {}
    
    # Get contest period
    contest_def = log.contest_definition
    contest_period = contest_def.contest_period if contest_def else None
    
    # Determine contest start and end times
    if contest_period and not df.empty:
        # Use same logic as _filter_by_contest_period
        DAY_NAME_TO_INT = {'MONDAY': 0, 'TUESDAY': 1, 'WEDNESDAY': 2, 'THURSDAY': 3,
                          'FRIDAY': 4, 'SATURDAY': 5, 'SUNDAY': 6}
        
        log_date = df['Datetime'].min().date()
        start_time_str = contest_period['start_time']
        end_time_str = contest_period['end_time']
        start_weekday = DAY_NAME_TO_INT[contest_period['start_day'].upper()]
        end_weekday = DAY_NAME_TO_INT[contest_period['end_day'].upper()]
        
        # Find the actual start date
        days_to_subtract = (log_date.weekday() - start_weekday + 7) % 7
        start_date = log_date - pd.to_timedelta(days_to_subtract, unit='d')
        contest_start = pd.to_datetime(start_date.strftime('%Y-%m-%d') + ' ' + start_time_str, utc=True)
        
        days_to_add = (end_weekday - start_weekday + 7) % 7
        end_date = start_date + pd.to_timedelta(days_to_add, unit='d')
        contest_end = pd.to_datetime(end_date.strftime('%Y-%m-%d') + ' ' + end_time_str, utc=True)
    else:
        # Fallback: use first and last QSO times
        contest_start = df['Datetime'].min()
        contest_end = df['Datetime'].max()
    
    # Get sorted QSO datetimes
    qso_times = df['Datetime'].sort_values().tolist()
    
    if not qso_times:
        return {}
    
    # Initialize inactive time per hour
    inactive_per_hour: Dict[pd.Timestamp, int] = {}
    
    # Helper function to allocate minutes to hours
    def allocate_minutes_to_hours(start_time: pd.Timestamp, end_time: pd.Timestamp):
        """Allocate minutes from a time range to the hours it spans."""
        if start_time >= end_time:
            return
        
        # Round start_time down to minute precision (Cabrillo is hhmm)
        start_min = start_time.replace(second=0, microsecond=0)
        # Round end_time up to minute precision
        end_min = end_time.replace(second=0, microsecond=0)
        if end_time.second > 0 or end_time.microsecond > 0:
            end_min += pd.Timedelta(minutes=1)
        
        current = start_min
        while current < end_min:
            # Find the hour this minute belongs to
            hour_start = current.floor('h')
            
            # Calculate minutes in this hour
            hour_end = hour_start + pd.Timedelta(hours=1)
            range_start = max(current, hour_start)
            range_end = min(end_min, hour_end)
            
            minutes_in_hour = int((range_end - range_start).total_seconds() / 60)
            
            if minutes_in_hour > 0:
                inactive_per_hour[hour_start] = inactive_per_hour.get(hour_start, 0) + minutes_in_hour
            
            current = hour_end
    
    # Check gap before first QSO
    first_qso = qso_times[0]
    if contest_start < first_qso:
        gap_minutes = (first_qso - contest_start).total_seconds() / 60
        if gap_minutes >= 15:
            allocate_minutes_to_hours(contest_start, first_qso)
    
    # Check gaps between consecutive QSOs
    for i in range(len(qso_times) - 1):
        current_qso = qso_times[i]
        next_qso = qso_times[i + 1]
        gap_minutes = (next_qso - current_qso).total_seconds() / 60
        if gap_minutes >= 15:
            allocate_minutes_to_hours(current_qso, next_qso)
    
    # Check gap after last QSO
    last_qso = qso_times[-1]
    if last_qso < contest_end:
        gap_minutes = (contest_end - last_qso).total_seconds() / 60
        if gap_minutes >= 15:
            allocate_minutes_to_hours(last_qso, contest_end)
    
    return inactive_per_hour

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
            
            # Calculate inactive time per hour
            inactive_time_per_hour = _calculate_inactive_time_per_hour(log, master_index)
            
            # Build report
            report_lines = self._build_report_lines(
                year, contest_name, callsign, mult_label, dimension, valid_dimensions,
                master_index, hourly_data, hourly_new_mults, hourly_cum_mults,
                cum_qsos, cum_score, inactive_time_per_hour, log=log
            )
            
            # Write file
            standard_footer = get_standard_footer([log])
            report_content = "\n".join(report_lines) + "\n\n" + standard_footer + "\n"
            os.makedirs(output_path, exist_ok=True)
            filename = f"{self.report_id}_{callsign_to_filename_part(callsign)}.txt"
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
        inactive_time_per_hour: Dict[pd.Timestamp, int], log: ContestLog = None
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
        
        # Calculate InactiveTime column width
        max_inactive_width = len("InactiveTime")  # Minimum width for header
        for hour_ts in master_index:
            inactive_minutes = inactive_time_per_hour.get(hour_ts, 0)
            if inactive_minutes > 0:
                inactive_str = f"{inactive_minutes} minutes"
                max_inactive_width = max(max_inactive_width, len(inactive_str))
        inactive_col_width = max_inactive_width + 1
        
        # Build header row
        header_parts = [f"{'Hour':<10}"]
        for dim in valid_dimensions:
            header_parts.append(f"{dim:>{dim_col_width}}")
        header_parts.extend([
            f"{'Total':>{dim_col_width}}", 
            f"{'Cumm':>{cumm_col_width}}", 
            f"{'Score':>{score_col_width}}",
            f"{'InactiveTime':>{inactive_col_width}}"
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
            
            # InactiveTime
            inactive_minutes = inactive_time_per_hour.get(hour_ts, 0)
            if inactive_minutes > 0:
                inactive_str = f"{inactive_minutes} minutes"
                row_parts.append(f"{inactive_str:>{inactive_col_width}}")
            else:
                row_parts.append(f"{'':>{inactive_col_width}}")
            
            report_lines.append("  ".join(row_parts))
        
        # Footer - Totals by dimension
        report_lines.append("")
        total_row_parts = [f"{'Totals:':<10}"]
        
        # Calculate totals per dimension
        # For once_per_mode: use cumulative multipliers per mode from scalars (matches score summary)
        # For other methods: sum new multipliers per hour
        total_breakdown_mults = 0
        total_qsos_sum = 0
        
        # Check if contest uses once_per_mode
        has_once_per_mode = False
        if log and log.contest_definition:
            has_once_per_mode = any(
                rule.get('totaling_method') == 'once_per_mode' 
                for rule in log.contest_definition.multiplier_rules
            )
        
        # For once_per_mode, get cumulative multipliers per mode from scalars
        # This matches the score summary calculation (once_per_mode sums unique per mode)
        mode_cumulative_mults = {}
        if has_once_per_mode and dimension == 'mode' and log:
            # Get cumulative multipliers per mode from score summary calculation
            # Use ScoreStatsAggregator to get accurate per-mode totals
            from contest_tools.data_aggregators.score_stats import ScoreStatsAggregator
            from contest_tools.utils.report_utils import get_valid_dataframe
            df_net = get_valid_dataframe(log, include_dupes=False)
            if not df_net.empty:
                contest_def = log.contest_definition
                multiplier_rules = contest_def.multiplier_rules
                log_location_type = getattr(log, '_my_location_type', None)
                
                # Filter out zero-point QSOs if contest rules require it
                if not contest_def.mults_from_zero_point_qsos:
                    df_net = df_net[df_net['QSOPoints'] > 0].copy()
                
                for mode in valid_dimensions:
                    mode_df = df_net[df_net['Mode'] == mode]
                    mode_total_mults = 0
                    for rule in multiplier_rules:
                        mult_col = rule['value_column']
                        applies_to = rule.get('applies_to')
                        if applies_to and log_location_type and applies_to != log_location_type:
                            continue
                        if mult_col in mode_df.columns:
                            df_valid_mults = mode_df[mode_df[mult_col].notna() & (mode_df[mult_col] != 'Unknown')]
                            mode_total_mults += df_valid_mults[mult_col].nunique()
                    mode_cumulative_mults[mode] = mode_total_mults
        
        for dim in valid_dimensions:
            qsos_list = hourly_data.get(dim, [])
            mults_list = hourly_new_mults.get(dim, [])
            dim_qsos = sum(qsos_list) if qsos_list else 0
            
            if has_once_per_mode and dimension == 'mode' and dim in mode_cumulative_mults:
                # For once_per_mode: use cumulative unique multipliers per mode (matches score summary)
                dim_mults = mode_cumulative_mults[dim]
            else:
                # For other methods: sum new multipliers per hour
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
        
        # Add InactiveTime total
        total_inactive_minutes = sum(inactive_time_per_hour.values())
        if total_inactive_minutes > 0:
            inactive_total_str = f"{total_inactive_minutes} minutes"
            total_row_parts.append(f"{inactive_total_str:>{inactive_col_width}}")
        else:
            total_row_parts.append(f"{'':>{inactive_col_width}}")
        
        report_lines.append("  ".join(total_row_parts))
        
        # Add footnote
        report_lines.append("")
        report_lines.append("InactiveTime is defined as at least 15 minutes without a QSO and does not depend on contest rules.")
        
        return report_lines
