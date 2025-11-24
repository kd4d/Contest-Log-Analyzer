# contest_tools/reports/text_rate_sheet.py
#
# Purpose: A text report that generates a detailed hourly rate sheet.
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
    Generates a detailed hourly rate sheet for each log.
    """
    report_id: str = "rate_sheet"
    report_name: str = "Hourly Rate Sheet"
    report_type: str = "text"
    supports_single = True
    
    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content.
    
        """
        include_dupes = kwargs.get('include_dupes', False)
        final_report_messages = []

        # Initialize Aggregator
        agg = TimeSeriesAggregator(self.logs)
        ts_data = agg.get_time_series_data()
        time_bins = ts_data['time_bins']

        for log in self.logs:
            callsign = log.get_metadata().get('MyCall', 'UnknownCall')
            
            # Check for data existence in aggregator output
            if callsign not in ts_data['logs']:
                print(f"Skipping rate sheet for {callsign}: No valid QSOs to report.")
                continue

            log_data = ts_data['logs'][callsign]
            scalars = log_data['scalars']
            
            # Use scalars for basic check (matching legacy behavior of skipping empty)
            if scalars['gross_qsos'] == 0:
                 print(f"Skipping rate sheet for {callsign}: No valid QSOs to report.")
                 continue

            year = scalars.get('year', "UnknownYear")
            contest_name = scalars.get('contest_name', 'UnknownContest')
            bands = log.contest_definition.valid_bands
            is_single_band = len(bands) == 1

            # --- Formatting ---
            header1_parts = [f"{'Hour':<5}"] + [f"{b.replace('M',''):>5}" for b in bands]
    
            header1 = " ".join(header1_parts)
            if not is_single_band:
                header1 += f" {'Hourly':>7}"
            header1 += f" {'Cumulative':>11}"
            
            header2_parts = [f"{'':<5}"] + [f"{'':>5}" for _ in bands]
         
            header2 = " ".join(header2_parts)
            if not is_single_band:
                header2 += f" {'Total':>7}"
            header2 += f" {'Total':>11}"
            
            table_width = len(header1)
            separator = "-" * table_width
    
         
            title1 = f"--- {self.report_name} ---"
            title2 = f"{year} {contest_name} - {callsign}"

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
            # Note: The Aggregator calculates hourly counts based on include_dupes=False (net) 
            # as requested in the implementation plan.
            
            hourly_data = log_data['hourly']
            by_band = hourly_data['by_band']
            
            cumulative_total = 0
            grand_total_by_band = {band: 0 for band in bands}
            
            for i, time_iso in enumerate(time_bins):
                # ISO: YYYY-MM-DDTHH:MM:SS
                # We need HHMM. Slicing strictly assuming ISO format.
                hour_str = time_iso[11:13] + time_iso[14:16]
                
                row_band_vals = {}
                row_hourly_total = 0
                
                for band in bands:
                    # Safely get value for this time bin index
                    val = by_band.get(band, [])[i] if i < len(by_band.get(band, [])) else 0
                    row_band_vals[band] = val
                    row_hourly_total += val
                    grand_total_by_band[band] += val
                
                # Filter rows where nothing happened (to match legacy groupby behavior which only shows valid rows)?
                # Legacy code: df_cleaned.groupby(...).unstack(fill_value=0)
                # Groupby only creates keys for existing data. The reindex in legacy filled 0s?
                # Actually, legacy code:
                # rate_data = df_cleaned.groupby(...).unstack(fill_value=0)
                # It does NOT reindex against a master clock in single report mode.
                # However, the Aggregator DOES reindex against master clock.
                # This causes rows with 0s to appear where they might not have before.
                # To match legacy visual exactness: if row_hourly_total == 0, we might want to skip?
                # Legacy: `for timestamp, row in rate_data.iterrows():`
                # If rate_data was formed by groupby on `df`, it only contains hours present in `df`.
                # So we MUST skip rows with 0 activity to preserve regression output.
                
                if row_hourly_total == 0:
                    continue

                cumulative_total += row_hourly_total
                
                line_parts = [f"{hour_str:<5}"]
                for band in bands:
                    line_parts.append(f"{row_band_vals[band]:>5}")
                
                line = " ".join(line_parts)
                if not is_single_band:
                    line += f" {row_hourly_total:>7} "
          
                line += f" {cumulative_total:>11}"
                report_lines.append(line)

            report_lines.append(separator)
            
            total_line_parts = [f"{'Total':<5}"]
            grand_total = 0
            for band in bands:
       
                band_total = grand_total_by_band[band]
                total_line_parts.append(f"{band_total:>5}")
                grand_total += band_total
            total_line = " ".join(total_line_parts)
            if not is_single_band:
                total_line += f" {grand_total:>7}"
       
            report_lines.append(total_line)
            report_lines.append("")

            gross_qsos = scalars['gross_qsos']
            dupes = scalars['dupes']
            # Logic from legacy: net_qsos = gross_qsos - dupes
            net_qsos = scalars['net_qsos']
            
            # Logic for footer display string based on include_dupes flag
            display_net = gross_qsos if include_dupes else net_qsos
            
            report_lines.append(f"Gross QSOs={gross_qsos}     Dupes={dupes}     Net QSOs={display_net}")
          
   
            report_content = "\n".join(report_lines) + "\n"
            os.makedirs(output_path, exist_ok=True)
            filename = f"{self.report_id}_{callsign}.txt"
            filepath = os.path.join(output_path, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
       
      
            final_report_messages.append(f"Text report saved to: {filepath}")

        return "\n".join(final_report_messages)