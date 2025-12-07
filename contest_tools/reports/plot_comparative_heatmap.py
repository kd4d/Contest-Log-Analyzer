# contest_tools/reports/plot_comparative_heatmap.py
#
# Purpose: A plot report that generates a comparative, split-cell heatmap to
#          visualize the band activity of two logs side-by-side.
#
# Copyright (c) 2025 Mark Bailey, KD4D
#
# Author: Gemini AI
# Date: 2025-11-24
# Version: 1.0.0
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
# --- Revision History ---
# [1.0.0] - 2025-11-24
# Refactored to use MatrixAggregator (DAL).
# [0.90.0-Beta] - 2025-10-01
# Set new baseline version for release.
import pandas as pd
import os
import logging
import math
import itertools
from typing import List, Dict, Any

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import get_valid_dataframe, create_output_directory, save_debug_data, ComparativeHeatmapChart
from ..data_aggregators.matrix_stats import MatrixAggregator

class Report(ContestReport):
    """
    Generates a comparative, split-cell heatmap of band activity for two logs.
    """
    report_id: str = "comparative_band_activity_heatmap"
    report_name: str = "Comparative Band Activity Heatmap"
    report_type: str = "plot"
    supports_multi = True

    def _generate_plot_for_slice(self, matrix_data: Dict, log1: ContestLog, log2: ContestLog, output_path: str, part_info_str: str, filename_suffix: str, **kwargs):
        """Helper function to generate a single heatmap plot for a given data slice (DAL-based)."""
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')
        debug_data_flag = kwargs.get("debug_data", False)
        
        # --- Data Reconstitution ---
        time_bins_str = matrix_data['time_bins']
        all_bands = matrix_data['bands']
        
        if not time_bins_str or not all_bands:
            return None

        time_bins = pd.to_datetime(time_bins_str)
        
        # Reconstruct Pandas DataFrames for slicing and Chart helper
        pivot_dfs = {}
        for call in [call1, call2]:
            qso_grid = matrix_data['logs'][call]['qso_counts']
            pivot_dfs[call] = pd.DataFrame(qso_grid, index=all_bands, columns=time_bins)

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
            
            # --- Save Debug Data (Modified for JSON compatibility) ---
            debug_filename = f"{self.report_id}_{call1}_vs_{call2}{filename_suffix}{part_suffix_file}.txt"
            
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
            aggregator = MatrixAggregator([log1, log2])
            
            # A. Get Full Data to determine bands present
            matrix_data_full = aggregator.get_matrix_data(bin_size='15min')
            all_bands_in_pair = matrix_data_full['bands']

            for band in all_bands_in_pair:
                band_output_path = os.path.join(output_path, band)
                create_output_directory(band_output_path)
                
                # Note: The Aggregator gets the whole log. We need to filter by Band HERE? 
                # No, the MatrixAggregator returns a grid for ALL bands. 
                # We need to slice the 2D grid for just this band.
                # However, the generic slicer `_generate_plot_for_slice` expects a matrix_data object.
                # Construct a single-band matrix_data subset manually?
                # Or better: Just pass the full matrix and let the helper slice? 
                # Actually, the original code looped bands and modes. 
                # To maintain parity, we should filter the raw DFs or use the Aggregator cleverly.
                
                # Strategy: 
                # 1. Band-Level: Filter DFs by Band, then pass to Aggregator?
                # The Aggregator takes Logs. 
                # Simplest: Modify `_generate_plot_for_slice` to accept the *Full* matrix and the *Band Name*.
                # But we also have "Mode" loop below.
                
                # Let's perform the filtering at the Log/DF level before calling the aggregator 
                # is not possible because Aggregator takes Logs.
                # We will instantiate temporary Logs or just rely on the fact that `get_matrix_data` returns 
                # a grid where we can select the index for 'band'.
                
                # BUT: `_generate_plot_for_slice` reconstructs the DF from `qso_counts`.
                # If we pass the full `qso_counts`, the DF has all bands.
                # We can filter that DF inside `_generate_plot_for_slice`? 
                # No, `_generate_plot_for_slice` expects to plot what it is given.
                
                # REVISED STRATEGY: 
                # We will construct a synthetic "Matrix Data" dict that only contains the rows for the current band.
                
                # 1. Generate "Band Overall" Plot
                # Extract the row for 'band' from `matrix_data_full`
                
                # (Refactoring `_generate_plot_for_slice` to accept filtered data is cleanest)
                # Let's manually construct the filtered matrix data dict
                
                def filter_matrix_by_band(m_data, target_band):
                    if target_band not in m_data['bands']: return None
                    idx = m_data['bands'].index(target_band)
                    new_data = {
                        "time_bins": m_data['time_bins'],
                        "bands": [target_band],
                        "logs": {}
                    }
                    for c, d in m_data['logs'].items():
                        new_data['logs'][c] = {
                            "qso_counts": [d['qso_counts'][idx]],
                            "activity_status": [d['activity_status'][idx]]
                        }
                    return new_data

                band_matrix_data = filter_matrix_by_band(matrix_data_full, band)
                if band_matrix_data:
                    filepath = self._generate_plot_for_slice(
                        matrix_data=band_matrix_data, log1=log1, log2=log2,
                        output_path=band_output_path, part_info_str=f"({band})",
                        filename_suffix=f"_{band.lower()}", **kwargs
                    )
                    if filepath: created_files.append(filepath)

                # 2. Generate "Band-Mode" Plots
                # We need to ask the Aggregator for specific modes.
                # We can't use `matrix_data_full` because that merges modes.
                
                # Check which modes exist in raw logs to save time
                df1 = get_valid_dataframe(log1, include_dupes=False)
                df2 = get_valid_dataframe(log2, include_dupes=False)
                modes_in_band = sorted(list(set(df1[df1['Band']==band]['Mode'].unique()) | set(df2[df2['Band']==band]['Mode'].unique())))
                
                if len(modes_in_band) > 1:
                    for mode in modes_in_band:
                        # Get Matrix for this Mode specifically
                        matrix_data_mode = aggregator.get_matrix_data(bin_size='15min', mode_filter=mode)
                        
                        # Now filter for the band
                        band_mode_matrix = filter_matrix_by_band(matrix_data_mode, band)
                        
                        if band_mode_matrix:
                            filepath = self._generate_plot_for_slice(
                                matrix_data=band_mode_matrix, log1=log1, log2=log2,
                                output_path=band_output_path, part_info_str=f"({band} - {mode})",
                                filename_suffix=f"_{band.lower()}_{mode.lower()}", **kwargs
                            )
                            if filepath: created_files.append(filepath)

        if not created_files:
            return f"Report '{self.report_name}' was generated, but no files were created."
        return f"Plot report(s) saved to relevant subdirectories in:\n  - {output_path}"