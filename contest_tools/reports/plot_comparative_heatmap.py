# Contest Log Analyzer/contest_tools/reports/plot_comparative_heatmap.py
#
# Version: 0.57.3-Beta
# Date: 2025-09-03
#
# Purpose: A plot report that generates a comparative, split-cell heatmap to
#          visualize the band activity of two logs side-by-side.
#
# Copyright (c) 2025 Mark Bailey, KD4D
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# --- Revision History ---
## [0.57.3-Beta] - 2025-09-03
### Changed
# - Updated instantiation of the ComparativeHeatmapChart helper to pass
#   the report_name, enabling standardized two-line title formatting.
## [0.40.4-Beta] - 2025-08-19
### Fixed
# - Corrected a TypeError during debug data generation by converting
#   pandas Timestamp keys to strings before JSON serialization.
## [0.40.3-Beta] - 2025-08-19
### Fixed
# - Refactored data preparation to establish a single, timezone-aware
#   master time axis for each log pair, fixing the empty plot and
#   missing debug data bugs.
## [0.40.2-Beta] - 2025-08-19
### Changed
# - Refactored the report into an autonomous, exhaustive analysis tool.
# - It now automatically generates all possible pairwise comparisons.
# - It now automatically generates breakdowns for each band and for each
#   mode within each band if applicable.
## [0.40.1-Beta] - 2025-08-19
### Changed
# - Modified the script to pass the full metadata dictionary to the
#   ComparativeHeatmapChart class to support standard title generation.
## [0.40.0-Beta] - 2025-08-19
# - Initial release of the comparative heatmap report, which uses the
#   ComparativeHeatmapChart helper class.
#
import pandas as pd
import os
import logging
import math
import itertools
from typing import List, Dict, Any

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import get_valid_dataframe, create_output_directory, save_debug_data, ComparativeHeatmapChart

class Report(ContestReport):
    """
    Generates a comparative, split-cell heatmap of band activity for two logs.
    """
    report_id: str = "comparative_band_activity_heatmap"
    report_name: str = "Comparative Band Activity Heatmap"
    report_type: str = "plot"
    supports_multi = True

    def _generate_plot_for_slice(self, df1_slice: pd.DataFrame, df2_slice: pd.DataFrame, time_bins: pd.DatetimeIndex, log1: ContestLog, log2: ContestLog, output_path: str, part_info_str: str, filename_suffix: str, **kwargs):
        """Helper function to generate a single heatmap plot for a given data slice."""
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')
        debug_data_flag = kwargs.get("debug_data", False)
        
        if df1_slice.empty and df2_slice.empty:
            return None # Skip plot generation if no data for this slice

        # --- Data Preparation for the slice ---
        dfs = {call1: df1_slice, call2: df2_slice}
        
        all_bands_with_activity = sorted(list(
            set(dfs[call1]['Band'].unique()) | set(dfs[call2]['Band'].unique())
        ))
        if not all_bands_with_activity:
            return None

        pivot_dfs = {}
        for call, df in dfs.items():
            if df.empty:
                pivot = pd.DataFrame(0, index=all_bands_with_activity, columns=time_bins)
            else:
                pivot = df.pivot_table(index='Band', columns=pd.Grouper(key='Datetime', freq='15min'), aggfunc='size', fill_value=0)
            
            pivot = pivot.reindex(index=all_bands_with_activity, columns=time_bins, fill_value=0)
            pivot_dfs[call] = pivot

        # --- Handle Multi-Part Plots for Long Contests ---
        intervals_per_day = 96
        total_intervals = len(time_bins)
        num_parts = math.ceil(total_intervals / intervals_per_day)
        
        metadata = log1.get_metadata()
        df_first_log = get_valid_dataframe(log1)
        metadata['Year'] = df_first_log['Date'].dropna().iloc[0].split('-')[0] if not df_first_log.empty and not df_first_log['Date'].dropna().empty else "----"

        for part_num in range(num_parts):
            start_interval = part_num * intervals_per_day
            end_interval = start_interval + intervals_per_day
            
            data1_part = pivot_dfs[call1].iloc[:, start_interval:end_interval]
            data2_part = pivot_dfs[call2].iloc[:, start_interval:end_interval]

            part_suffix_text = f"(Part {part_num + 1} of {num_parts})" if num_parts > 1 else ""
            part_suffix_file = f"_Part_{part_num + 1}_of_{num_parts}" if num_parts > 1 else ""
            
            final_part_info = f"{part_info_str} {part_suffix_text}".strip()
            
            filename = f"{self.report_id}_{call1}_vs_{call2}{filename_suffix}{part_suffix_file}.png"
            filepath = os.path.join(output_path, filename)
            
            # --- Save Debug Data ---
            debug_filename = f"{self.report_id}_{call1}_vs_{call2}{filename_suffix}{part_suffix_file}.txt"
            
            # Create copies and convert Timestamp columns to strings for JSON compatibility
            debug_data1 = data1_part.copy()
            debug_data2 = data2_part.copy()
            debug_data1.columns = debug_data1.columns.map(lambda ts: ts.isoformat())
            debug_data2.columns = debug_data2.columns.map(lambda ts: ts.isoformat())
            
            debug_data = {f"pivot_{call1}": debug_data1.to_dict(), f"pivot_{call2}": debug_data2.to_dict()}
            save_debug_data(debug_data_flag, output_path, debug_data, custom_filename=debug_filename)

            heatmap_chart = ComparativeHeatmapChart(
                data1=data1_part, data2=data2_part, call1=call1, call2=call2,
                metadata=metadata, output_filename=filepath, report_name=self.report_name, part_info=final_part_info
            )
            
            return heatmap_chart.plot()


    def generate(self, output_path: str, **kwargs) -> str:
        """Orchestrates the generation of all pairwise, per-band, and per-mode plots."""
        if len(self.logs) < 2:
            return f"Report '{self.report_name}' requires at least two logs for comparison."

        created_files = []
        
        for log1, log2 in itertools.combinations(self.logs, 2):
            df1 = get_valid_dataframe(log1, include_dupes=False)
            df2 = get_valid_dataframe(log2, include_dupes=False)
            
            if df1.empty and df2.empty: continue

            df1['Datetime'] = df1['Datetime'].dt.tz_localize('UTC')
            df2['Datetime'] = df2['Datetime'].dt.tz_localize('UTC')
            
            all_datetimes = pd.concat([df1['Datetime'], df2['Datetime']])
            min_time = all_datetimes.min().floor('h')
            max_time = all_datetimes.max().ceil('h')
            time_bins = pd.date_range(start=min_time, end=max_time, freq='15min', tz='UTC')

            all_bands_in_pair = sorted(list(set(df1['Band'].unique()) | set(df2['Band'].unique())))
            for band in all_bands_in_pair:
                band_output_path = os.path.join(output_path, band)
                create_output_directory(band_output_path)
                
                df1_band = df1[df1['Band'] == band]
                df2_band = df2[df2['Band'] == band]

                # 1. Generate "Band Overall" Plot
                filepath = self._generate_plot_for_slice(
                    df1_slice=df1_band, df2_slice=df2_band, time_bins=time_bins, log1=log1, log2=log2,
                    output_path=band_output_path, part_info_str=f"({band})",
                    filename_suffix=f"_{band.lower()}", **kwargs
                )
                if filepath: created_files.append(filepath)

                # 2. Generate "Band-Mode" Plots
                modes_in_band = sorted(list(set(df1_band['Mode'].unique()) | set(df2_band['Mode'].unique())))
                if len(modes_in_band) > 1:
                    for mode in modes_in_band:
                        df1_mode = df1_band[df1_band['Mode'] == mode]
                        df2_mode = df2_band[df2_band['Mode'] == mode]
                        
                        filepath = self._generate_plot_for_slice(
                            df1_slice=df1_mode, df2_slice=df2_mode, time_bins=time_bins, log1=log1, log2=log2,
                            output_path=band_output_path, part_info_str=f"({band} - {mode})",
                            filename_suffix=f"_{band.lower()}_{mode.lower()}", **kwargs
                        )
                        if filepath: created_files.append(filepath)

        if not created_files:
            return f"Report '{self.report_name}' was generated, but no files were created."

        return f"Plot report(s) saved to relevant subdirectories in:\n  - {output_path}"