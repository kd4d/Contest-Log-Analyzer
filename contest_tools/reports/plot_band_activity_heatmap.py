# contest_tools/reports/plot_band_activity_heatmap.py
#
# Purpose: A plot report that generates a heatmap of band activity over time.
#
# Author: Gemini AI
# Date: 2025-11-24
# Version: 1.1.1
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
# [1.1.1] - 2025-12-10
# - Updated heatmap logic to render zero values as transparent (blank) instead of colored.
# [1.1.0] - 2025-12-10
# - Migrated visualization engine to Plotly.
# [1.0.0] - 2025-11-24
# - Refactored to use MatrixAggregator (DAL) for data generation.
# [0.90.0-Beta] - 2025-10-01
# - Set new baseline version for release.
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import logging
from typing import List, Dict, Any

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import get_valid_dataframe, create_output_directory, save_debug_data
from ..data_aggregators.matrix_stats import MatrixAggregator
from ..styles.plotly_style_manager import PlotlyStyleManager

class Report(ContestReport):
    """
    Generates a heatmap of band activity over the duration of the contest.
    """
    report_id: str = "band_activity_heatmap"
    report_name: str = "Band Activity Heatmap"
    report_type: str = "plot"
    supports_single = True

    def generate(self, output_path: str, **kwargs) -> str:
        """Generates the report content."""
        final_report_messages = []
        debug_data_flag = kwargs.get("debug_data", False)

        for log in self.logs:
            metadata = log.get_metadata()
            callsign = metadata.get('MyCall', 'UnknownCall')
            
            df = get_valid_dataframe(log, include_dupes=False)
            
            if df.empty or 'Datetime' not in df.columns or df['Datetime'].isna().all():
                msg = f"Skipping report for {callsign}: No valid QSOs with timestamps to report."
                final_report_messages.append(msg)
                continue

            # --- 1. Data Aggregation (DAL) ---
            aggregator = MatrixAggregator([log])
            matrix_data = aggregator.get_matrix_data(bin_size='15min')
            
            # --- Save Debug Data ---
            debug_filename = f"{self.report_id}_{callsign}.txt"
            save_debug_data(debug_data_flag, output_path, matrix_data, custom_filename=debug_filename)

            # Unpack DAL data
            if not matrix_data['time_bins'] or not matrix_data['bands']:
                 msg = f"Skipping report for {callsign}: No matrix data generated."
                 final_report_messages.append(msg)
                 continue

            try:
                # --- 2. Create Chart ---
                fig = self._create_chart(matrix_data, metadata)

                # --- 3. Save Files ---
                create_output_directory(output_path)
                
                # Save PNG
                filename_png = f"{self.report_id}_{callsign}.png"
                filepath_png = os.path.join(output_path, filename_png)
                fig.write_image(filepath_png, width=1200, height=600)
                
                # Save HTML
                filename_html = f"{self.report_id}_{callsign}.html"
                filepath_html = os.path.join(output_path, filename_html)
                fig.write_html(filepath_html, include_plotlyjs='cdn')
            
                final_report_messages.append(f"Plot report saved to: {filepath_png} and {filepath_html}")

            except Exception as e:
                logging.error(f"Error saving heatmap for {callsign}: {e}")
                final_report_messages.append(f"Error generating report '{self.report_name}' for {callsign}")

        return "\n".join(final_report_messages)

    def _create_chart(self, matrix_data: Dict[str, Any], metadata: Dict[str, Any]) -> go.Figure:
        """
        Internal helper to create the Plotly Figure for the heatmap.
        """
        # Unpack data
        time_bins_str = matrix_data['time_bins']
        sorted_bands = matrix_data['bands']
        callsign = metadata.get('MyCall', 'UnknownCall')
        qso_grid = matrix_data['logs'][callsign]['qso_counts']

        # --- Data Transformation for Visualization ---
        # Convert to float and replace 0 with NaN to make them transparent (blank)
        # Plotly ignores NaNs in heatmaps, effectively masking them.
        qso_grid = np.array(qso_grid, dtype=float)
        qso_grid[qso_grid == 0] = np.nan

        # Construct Title
        year = metadata.get('Year', '----')
        contest_name = metadata.get('ContestName', 'UnknownContest')
        event_id = metadata.get('EventID', '')
        
        title_line1 = self.report_name
        title_line2 = f"{year} {contest_name} {event_id} - {callsign}".strip()
        final_title = f"{title_line1}<br>{title_line2}"

        # Initialize Figure
        fig = go.Figure()

        # Add Heatmap Trace
        # Note: xgap and ygap simulate grid lines
        fig.add_trace(go.Heatmap(
            z=qso_grid,
            x=time_bins_str,
            y=sorted_bands,
            colorscale='Hot',
            zmin=0,
            xgap=1,
            ygap=1,
            colorbar=dict(title='QSOs / 15 min')
        ))

        # Apply Standard Layout
        layout = PlotlyStyleManager.get_standard_layout(final_title)
        
        # Apply Report-Specific Layout Overrides
        fig.update_layout(layout)
        fig.update_layout(
            xaxis_title="Contest Time (UTC)",
            yaxis_title="Band",
            width=1200,
            height=600,
            # Ensure background is white so transparency shows correctly
            plot_bgcolor='white'
        )

        return fig