# contest_tools/reports/plot_comparative_band_activity_heatmap.py
#
# Purpose: A plot report that generates a comparative, split-cell heatmap to
#          visualize the band activity of two logs side-by-side.
#
# Copyright (c) 2025 Mark Bailey, KD4D
#
# Author: Gemini AI
# Date: 2025-12-10
# Version: 1.2.0
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
# [1.2.0] - 2025-12-10
# - Removed pagination logic to generate a single continuous plot.
# - Implemented dynamic chart width based on contest duration (10px per bin).
# - Fixed early exit bug in file generation.
# [1.1.0] - 2025-12-10
# - Migrated visualization engine from Matplotlib to Plotly (Phase 2).
# - Implemented stacked subplots with synchronized color scaling.
# - Added dual output (PNG + HTML).
# [1.0.0] - 2025-11-24
# Refactored to use MatrixAggregator (DAL).
# [0.90.0-Beta] - 2025-10-01
# Set new baseline version for release.
import pandas as pd
import os
import logging
import math
import itertools
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Any

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import get_valid_dataframe, create_output_directory, save_debug_data
from ..data_aggregators.matrix_stats import MatrixAggregator
from ..styles.plotly_style_manager import PlotlyStyleManager

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
        
        # Reconstruct Pandas DataFrames for slicing
        pivot_dfs = {}
        for call in [call1, call2]:
            qso_grid = matrix_data['logs'][call]['qso_counts']
            pivot_dfs[call] = pd.DataFrame(qso_grid, index=all_bands, columns=time_bins)

        # --- Metadata Extraction ---
        metadata = log1.get_metadata()
        df_first_log = get_valid_dataframe(log1)
        year = df_first_log['Date'].dropna().iloc[0].split('-')[0] if not df_first_log.empty and not df_first_log['Date'].dropna().empty else "----"
        metadata['Year'] = year
        
        contest_name = metadata.get('ContestName', '')
        event_id = metadata.get('EventID', '')

        # --- Data Preparation (Full Duration - No Pagination) ---
        data1 = pivot_dfs[call1]
        data2 = pivot_dfs[call2]
        
        # Determine base filename
        base_filename = f"{self.report_id}_{call1}_vs_{call2}{filename_suffix}"
        png_filepath = os.path.join(output_path, f"{base_filename}.png")
        html_filepath = os.path.join(output_path, f"{base_filename}.html")
        
        # --- Save Debug Data ---
        debug_filename = f"{base_filename}.txt"
        
        debug_data1 = data1.copy()
        debug_data2 = data2.copy()
        debug_data1.columns = debug_data1.columns.map(lambda ts: ts.isoformat())
        debug_data2.columns = debug_data2.columns.map(lambda ts: ts.isoformat())
        
        debug_data = {f"pivot_{call1}": debug_data1.to_dict(), f"pivot_{call2}": debug_data2.to_dict()}
        save_debug_data(debug_data_flag, output_path, debug_data, custom_filename=debug_filename)

        # --- Plotly Visualization Logic ---
        
        # 1. Calculate Global Max for Consistent Scaling
        max1 = data1.max().max()
        max2 = data2.max().max()
        global_max = max(max1, max2) if not (np.isnan(max1) and np.isnan(max2)) else 10
        
        # 2. Data Prep: Convert 0 to NaN for transparency
        z1 = data1.replace(0, np.nan)
        z2 = data2.replace(0, np.nan)

        # 3. Setup Subplots
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=[f"{call1}", f"{call2}"]
        )

        # 4. Trace Construction
        # Trace 1 (Top) - Log 1
        fig.add_trace(
            go.Heatmap(
                z=z1.values,
                x=z1.columns,
                y=z1.index,
                colorscale='Hot',
                zmin=0,
                zmax=global_max,
                xgap=1,
                ygap=1,
                colorbar=dict(title='QSOs / 15 min', len=0.9, y=0.5),
                showscale=True # Show colorbar on this trace
            ),
            row=1, col=1
        )

        # Trace 2 (Bottom) - Log 2
        fig.add_trace(
            go.Heatmap(
                z=z2.values,
                x=z2.columns,
                y=z2.index,
                colorscale='Hot',
                zmin=0,
                zmax=global_max,
                xgap=1,
                ygap=1,
                showscale=False # Share colorbar reference from trace 1
            ),
            row=2, col=1
        )

        # 5. Styling and Layout
        
        # Dynamic Width Calculation
        # Minimum width 1200px, or 10px per time bin to ensure readability
        num_time_bins = len(time_bins)
        calculated_width = max(1200, num_time_bins * 10)

        # Construct Title
        title_line1 = f"{self.report_name} {part_info_str}".strip()
        title_line2 = f"{year} {event_id} {contest_name} - {call1} vs. {call2}".strip().replace("  ", " ")
        full_title = f"{title_line1}<br>{title_line2}"

        # Apply Standard Styles
        layout_config = PlotlyStyleManager.get_standard_layout(full_title)
        
        # Override/Extend Layout
        layout_config.update({
            "width": calculated_width,
            "height": 800,
            "margin": dict(t=140, l=50, r=50, b=50), # Increased top margin per ADR-008
        })
        
        fig.update_layout(**layout_config)
        
        # Ensure Y-Axes are categorical (Bands)
        fig.update_yaxes(type='category', categoryorder='array', categoryarray=all_bands)

        # 6. Save Outputs
        try:
            fig.write_image(png_filepath)
            fig.write_html(html_filepath, include_plotlyjs='cdn')
            return png_filepath
        except Exception as e:
            logging.error(f"Error saving split heatmap: {e}")
            return None


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
                
                # Manual construction of filtered matrix data dict
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