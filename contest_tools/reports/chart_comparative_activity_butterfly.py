# contest_tools/reports/chart_comparative_activity_butterfly.py
#
# Purpose: Generates a comparative 'Butterfly' chart (stacked diverging bars)
#          visualizing Run vs S&P activity for two stations per band.
#
# Author: Gemini AI
# Date: 2026-01-05
# Version: 0.159.2-Beta
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
# [0.159.2-Beta] - 2026-01-05
# - Standardized filename generation: removed '_vs_' separator to match Web Dashboard conventions
#   and alignment with other comparative reports.
# [0.159.1-Beta] - 2026-01-05
# - Configured Plotly ModeBar 'Camera' button to download PNGs with descriptive filenames.
# [0.158.0-Beta] - 2026-01-05
# - Removed PNG generation (fig.write_image) to resolve Kaleido dependency issues in web container.
# [0.157.0-Beta] - 2026-01-04
# - Refactored to use Plotly for visualization, removing Matplotlib dependency.
# [0.151.1-Beta] - 2026-01-01
# - Repair import path for report_utils to fix circular dependency.
# [0.151.0-Beta] - 2026-01-01
# - Refactored imports to use `contest_tools.utils.report_utils` to break circular dependency.
# [1.0.2] - 2025-12-06
# - Fixed output directory pathing issue where charts were saved to a nested
#   'charts/charts' directory.
#   Now saves directly to the provided output_path.
# [1.0.1] - 2025-12-06
# - Updated color palette to Blue (S&P) / Green (Run) / Grey (Unknown) to match
#   standard breakdown charts.
# [1.0.0] - 2025-12-06
# - Initial creation implementing the Stacked Butterfly Chart.

import os
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ..data_aggregators.matrix_stats import MatrixAggregator
from contest_tools.utils.report_utils import create_output_directory, _sanitize_filename_part
from ..styles.plotly_style_manager import PlotlyStyleManager

class Report(ContestReport):
    report_id = "chart_comparative_activity_butterfly"
    report_name = "Comparative Activity Butterfly Chart"
    report_type = "chart"
    supports_single = False
    supports_pairwise = True
    supports_multi = False

    def __init__(self, logs: List[ContestLog]):
        super().__init__(logs)
        
        # Load authoritative colors from StyleManager
        style_colors = PlotlyStyleManager.get_qso_mode_colors()
        self.COLORS = {
            'Run': style_colors.get('Run', '#2ca02c'),
            'S&P': style_colors.get('S&P', '#1f77b4'),
            'Unknown': style_colors.get('Mixed/Unk', '#7f7f7f')
        }

    def generate(self, output_path: str, **kwargs) -> str:
        if len(self.logs) != 2:
            return "Skipping: Butterfly chart requires exactly 2 logs."

        call1 = self.logs[0].get_metadata().get('MyCall', 'LOG1')
        call2 = self.logs[1].get_metadata().get('MyCall', 'LOG2')

        # 1. Fetch Data
        aggregator = MatrixAggregator(self.logs)
        data = aggregator.get_stacked_matrix_data(bin_size='60min')
        
        bands = data.get('bands', [])
        time_bins = data.get('time_bins', [])
        
        if not bands or not time_bins:
            return "No data available to plot."

        # 2. Setup Output
        charts_dir = output_path
        create_output_directory(charts_dir)

        # 3. Generate Plot
        try:
            filename_base = f"chart_comparative_activity_butterfly_{_sanitize_filename_part(call1)}_{_sanitize_filename_part(call2)}"
            
            # Create the figure
            fig = self._create_figure(data, time_bins, bands, call1, call2)
            
            generated_files = []

            # Save HTML (Interactive)
            html_filename = f"{filename_base}.html"
            html_path = os.path.join(charts_dir, html_filename)
            config = {'toImageButtonOptions': {'filename': filename_base, 'format': 'png'}}
            fig.write_html(html_path, config=config)
            generated_files.append(html_filename)

            # PNG Generation disabled for Web Architecture (Phase 3)

            return f"Generated {len(generated_files)} butterfly chart(s) in {charts_dir}"

        except Exception as e:
            logging.error(f"Error generating butterfly chart: {e}")
            return f"Failed to generate butterfly chart: {e}"

    def _create_figure(self, data: Dict[str, Any], time_bins: List[Any], 
            bands: List[str], call1: str, call2: str) -> go.Figure:
        
        num_plots = len(bands)
        # Create subplots: One row per band, shared X axis
        fig = make_subplots(
            rows=num_plots, 
            cols=1, 
            shared_xaxes=True,
            subplot_titles=[f"Band {b}" for b in bands],
            vertical_spacing=0.05
        )

        meta = self.logs[0].get_metadata()
        year = meta.get('Year', '')
        contest = meta.get('ContestName', '')

        for i, band in enumerate(bands):
            row_idx = i + 1
            
            # --- Log 1 (Positive) ---
            # Order: Run, S&P, Unknown
            l1_run = data['logs'][call1][band]['Run']
            l1_sp = data['logs'][call1][band]['S&P']
            l1_unk = data['logs'][call1][band]['Unknown']

            fig.add_trace(go.Bar(
                x=time_bins, y=l1_run,
                name='Run', legendgroup='Run', showlegend=(i==0),
                marker_color=self.COLORS['Run'],
                hoverinfo='x+y+name'
            ), row=row_idx, col=1)

            fig.add_trace(go.Bar(
                x=time_bins, y=l1_sp,
                name='S&P', legendgroup='S&P', showlegend=(i==0),
                marker_color=self.COLORS['S&P'],
                hoverinfo='x+y+name'
            ), row=row_idx, col=1)

            fig.add_trace(go.Bar(
                x=time_bins, y=l1_unk,
                name='Unknown', legendgroup='Unknown', showlegend=(i==0),
                marker_color=self.COLORS['Unknown'],
                hoverinfo='x+y+name'
            ), row=row_idx, col=1)

            # --- Log 2 (Negative) ---
            # Negate values to stack downwards
            l2_run = [-v for v in data['logs'][call2][band]['Run']]
            l2_sp = [-v for v in data['logs'][call2][band]['S&P']]
            l2_unk = [-v for v in data['logs'][call2][band]['Unknown']]

            fig.add_trace(go.Bar(
                x=time_bins, y=l2_run,
                name='Run', legendgroup='Run', showlegend=False,
                marker_color=self.COLORS['Run'],
                hoverinfo='x+y+name',
                customdata=[abs(v) for v in l2_run],
                hovertemplate='%{x}<br>Run: %{customdata}'
            ), row=row_idx, col=1)

            fig.add_trace(go.Bar(
                x=time_bins, y=l2_sp,
                name='S&P', legendgroup='S&P', showlegend=False,
                marker_color=self.COLORS['S&P'],
                hoverinfo='x+y+name',
                customdata=[abs(v) for v in l2_sp],
                hovertemplate='%{x}<br>S&P: %{customdata}'
            ), row=row_idx, col=1)

            fig.add_trace(go.Bar(
                x=time_bins, y=l2_unk,
                name='Unknown', legendgroup='Unknown', showlegend=False,
                marker_color=self.COLORS['Unknown'],
                hoverinfo='x+y+name',
                customdata=[abs(v) for v in l2_unk],
                hovertemplate='%{x}<br>Unk: %{customdata}'
            ), row=row_idx, col=1)
            
            # Add zero line
            fig.add_shape(type="line",
                x0=time_bins[0], y0=0, x1=time_bins[-1], y1=0,
                line=dict(color="black", width=1),
                row=row_idx, col=1
            )
            
            # Update Y-axis to show absolute values
            fig.update_yaxes(
                title_text="QSOs", 
                tickmode='auto',
                tickformat='s', # Remove negative signs visually not easy in standard simple format, but 's' helps
                row=row_idx, col=1
            )

        # Layout Updates
        fig.update_layout(
            title_text=f"Comparative Activity Breakdown (Hrly)<br>{year} {contest} - {call1} (Top/Pos) vs {call2} (Bottom/Neg)",
            barmode='relative', # Allows stacking positive and negative values
            height=300 * num_plots,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return fig