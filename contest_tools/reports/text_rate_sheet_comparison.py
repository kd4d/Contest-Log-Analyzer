# contest_tools/reports/text_rate_sheet_comparison.py
#
# Purpose: A text report that generates a comparative hourly rate sheet for two or more logs.
#
# Author: Gemini AI
# Date: 2025-10-01
# Version: 0.90.0-Beta
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
# [0.90.0-Beta] - 2025-10-01
# Set new baseline version for release.
from typing import List
import pandas as pd
import os
from ..contest_log import ContestLog
from .report_interface import ContestReport
from ..data_aggregators.time_series import TimeSeriesAggregator

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
       
        Generates the report content, saves it to a file, and returns a summary.
        """
        include_dupes = kwargs.get('include_dupes', False)

        if len(self.logs) < 2:
            return "Error: The Comparative Rate Sheet report requires at least two logs."
        
        all_calls = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in self.logs])
        first_log = self.logs[0]
        contest_def = first_log.contest_definition
        bands = contest_def.valid_bands
        is_single_band = len(bands) == 1
        
        # --- Formatting ---
        prefix_width = 11
        band_width = 6
        hourly_width = 8
  
        cum_width = 12
        
        header1_parts = [f"{'':<{prefix_width}}"] + [f"{b.replace('M',''):>{band_width}}" for b in bands]
        header1 = "".join(header1_parts)
        if not is_single_band:
            header1 += f"{'Hourly':>{hourly_width}}"
        header1 += f"{'Cumulative':>{cum_width}}"

        header2_parts = [f"{'':<{prefix_width}}"] + [f"{'':>{band_width}}" for _ in bands]
        
        header2 = "".join(header2_parts)
        if not is_single_band:
            header2 += f"{'Total':>{hourly_width}}"
        header2 += f"{'Total':>{cum_width}}"

        table_width = len(header1)
        separator = " " * prefix_width + "-" * (len(header2) - prefix_width)
        
        contest_name = first_log.get_metadata().get('ContestName', 'UnknownContest')
        year = first_log.get_processed_data()['Date'].dropna().iloc[0].split('-')[0] if not first_log.get_processed_data().empty else "----"
 
        
        title1 = f"--- {self.report_name} ---"
        title2 = f"{year} {contest_name} - {', '.join(all_calls)}"
        
        report_lines = []
        header_width = max(table_width, len(title1), len(title2))
        if len(title1) > table_width or len(title2) > table_width:
             report_lines.append(f"{title1.ljust(header_width)}")
         
             report_lines.append(f"{title2.center(header_width)}")
        else:
             report_lines.append(title1.center(header_width))
             report_lines.append(title2.center(header_width))
        report_lines.append("")
        
        report_lines.append(header1)
        report_lines.append(header2)
        report_lines.append(separator)

        # --- Data Aggregation (via Aggregator) ---
        agg = TimeSeriesAggregator(self.logs)
        ts_data = agg.get_time_series_data()
        time_bins = ts_data['time_bins']
        
        cumulative_totals = {call: 0 for call in all_calls}
        grand_totals_by_band = {call: {band: 0 for band in bands} for call in all_calls}

        # --- Report Body ---
        # Legacy behavior: `master_time_index = all_datetimes.dt.floor('h').dropna().unique()`
        # Aggregator provides `time_bins` which is exactly this.
        
        for i, time_iso in enumerate(time_bins):
            # Format: YYYY-MM-DDTHH:MM:SS -> HHMM
            hour_str = time_iso[11:13] + time_iso[14:16]
            report_lines.append(hour_str)

            for callsign in all_calls:
                log_entry = ts_data['logs'].get(callsign)
                hourly_total = 0
                
                if log_entry:
                    by_band = log_entry['hourly']['by_band']
                    
                    # Check if this hour has any data (to mimic legacy row behavior? 
                    # No, legacy comparison report iterates master_time_index and prints lines for EVERY timestamp
                    # regardless of whether a specific call has data, filling 0s. 
                    # See legacy: `if log_data is not None and timestamp in log_data.index: ... else: ... fill 0`
                    
                    line_parts = [f"  {callsign:<7}: "]
                    
                    for band in bands:
                        val = by_band.get(band, [])[i] if i < len(by_band.get(band, [])) else 0
                        hourly_total += val
                        grand_totals_by_band[callsign][band] += val
                        line_parts.append(f"{val:>{band_width}}")
                    
                    cumulative_totals[callsign] += hourly_total
                    
                    line = "".join(line_parts)
                    if not is_single_band:
                        line += f"{hourly_total:>{hourly_width}}"
   
                    line += f"{cumulative_totals[callsign]:>{cum_width}}"
                else:
                    # No data for this call at all (e.g. log missing)
                    line_parts = [f"  {callsign:<7}: "]
                    for band in bands:
                        line_parts.append(f"{0:>{band_width}}")
                    line = "".join(line_parts)
                    if not is_single_band:
                        line += f"{0:>{hourly_width}}"
                    line += f"{cumulative_totals[callsign]:>{cum_width}}"
 
                
                report_lines.append(line)
        
        # --- Totals Section ---
        report_lines.append(separator)
        report_lines.append("TOTALS")
        for callsign in all_calls:
            log_entry = ts_data['logs'].get(callsign)
        
            if log_entry:
                total_line_parts = [f"  {callsign:<7}: "]
                grand_total = 0
                for band in bands:
                    band_total = grand_totals_by_band[callsign][band]
            
                    total_line_parts.append(f"{band_total:>{band_width}}")
                    grand_total += band_total
                total_line = "".join(total_line_parts)
                if not is_single_band:
                    total_line += f"{grand_total:>{hourly_width}}"
            
                report_lines.append(total_line)

        report_content = "\n".join(report_lines) + "\n"
        os.makedirs(output_path, exist_ok=True)
        
        filename_calls = '_vs_'.join(sorted(all_calls))
        filename = f"{self.report_id}_{filename_calls}.txt"
        filepath = os.path.join(output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
   
      
        return f"Text report saved to: {filepath}"