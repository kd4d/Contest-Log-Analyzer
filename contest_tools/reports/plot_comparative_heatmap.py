# Contest Log Analyzer/contest_tools/reports/plot_comparative_heatmap.py
#
# Version: 1.1.0-Beta
# Date: 2025-08-19
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
## [1.1.0-Beta] - 2025-08-19
### Changed
# - Modified the script to pass the full metadata dictionary to the
#   ComparativeHeatmapChart class to support standard title generation.
## [1.0.0-Beta] - 2025-08-19
# - Initial release of the comparative heatmap report, which uses the
#   ComparativeHeatmapChart helper class.
#
import pandas as pd
import os
import logging
import math
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
    supports_pairwise = True

    def generate(self, output_path: str, **kwargs) -> str:
        """Generates the report content."""
        if len(self.logs) != 2:
            return f"Error: Report '{self.report_name}' requires exactly two logs."

        log1, log2 = self.logs[0], self.logs[1]
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')
        debug_data_flag = kwargs.get("debug_data", False)

        # --- 1. Data Preparation ---
        dfs = {}
        for call, log in [(call1, log1), (call2, log2)]:
            df = get_valid_dataframe(log, include_dupes=False)
            if df.empty or 'Datetime' not in df.columns or df['Datetime'].isna().all():
                return f"Skipping report: Log for {call} has no valid QSO data with timestamps."
            df['Datetime'] = df['Datetime'].dt.tz_localize('UTC')
            dfs[call] = df

        interval = '15min'
        min_time = min(df['Datetime'].min() for df in dfs.values()).floor('h')
        max_time = max(df['Datetime'].max() for df in dfs.values()).ceil('h')
        time_bins = pd.date_range(start=min_time, end=max_time, freq=interval, tz='UTC')

        all_bands_with_activity = sorted(list(
            set(dfs[call1]['Band'].unique()) | set(dfs[call2]['Band'].unique())
        ))

        pivot_dfs = {}
        for call, df in dfs.items():
            pivot = df.pivot_table(index='Band', columns=pd.Grouper(key='Datetime', freq=interval), aggfunc='size', fill_value=0)
            pivot = pivot.reindex(index=all_bands_with_activity, columns=time_bins, fill_value=0)
            pivot_dfs[call] = pivot

        # --- 2. Handle Multi-Part Plots for Long Contests ---
        intervals_per_day = 96  # 24 hours * 4 intervals/hour
        total_intervals = len(time_bins)
        num_parts = math.ceil(total_intervals / intervals_per_day)
        created_files = []
        
        # Prepare metadata for titles
        metadata = log1.get_metadata()
        df_first_log = get_valid_dataframe(log1)
        metadata['Year'] = df_first_log['Date'].dropna().iloc[0].split('-')[0] if not df_first_log.empty and not df_first_log['Date'].dropna().empty else "----"


        for part_num in range(num_parts):
            start_interval = part_num * intervals_per_day
            end_interval = start_interval + intervals_per_day
            
            data1_part = pivot_dfs[call1].iloc[:, start_interval:end_interval]
            data2_part = pivot_dfs[call2].iloc[:, start_interval:end_interval]

            # --- 3. Visualization ---
            part_suffix_text = f"(Part {part_num + 1} of {num_parts})" if num_parts > 1 else ""
            part_suffix_file = f"_Part_{part_num + 1}_of_{num_parts}" if num_parts > 1 else ""
            
            filename = f"{self.report_id}_{call1}_vs_{call2}{part_suffix_file}.png"
            filepath = os.path.join(output_path, filename)
            
            # --- Save Debug Data for this part ---
            debug_filename = f"{self.report_id}_{call1}_vs_{call2}{part_suffix_file}.txt"
            debug_data = {
                f"pivot_{call1}": data1_part.to_dict(),
                f"pivot_{call2}": data2_part.to_dict()
            }
            save_debug_data(debug_data_flag, output_path, debug_data, custom_filename=debug_filename)

            heatmap_chart = ComparativeHeatmapChart(
                data1=data1_part,
                data2=data2_part,
                call1=call1,
                call2=call2,
                metadata=metadata,
                output_filename=filepath,
                part_info=part_suffix_text
            )
            
            saved_path = heatmap_chart.plot()
            if saved_path:
                created_files.append(saved_path)

        if not created_files:
            return f"Report '{self.report_name}' was generated, but no files were created."

        return f"Plot report(s) saved to:\n" + "\n".join([f"  - {fp}" for fp in created_files])