# contest_tools/reports/plot_correlation_analysis.py
#
# Purpose: Generates scatter plots correlating Run % with QSO Rate and Multiplier Yield.
#
# Author: Gemini AI
# Date: 2025-12-18
# Version: 0.126.0-Beta
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
# [0.126.0-Beta] - 2025-12-18
# - Initial creation for Solo Audit.

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from typing import List

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import create_output_directory, _sanitize_filename_part, save_debug_data
from ..data_aggregators.time_series import TimeSeriesAggregator
from ..styles.plotly_style_manager import PlotlyStyleManager

class Report(ContestReport):
    report_id = "plot_correlation_analysis"
    report_name = "Correlation Analysis"
    report_type = "plot"
    supports_single = True
    supports_multi = True
    
    def generate(self, output_path: str, **kwargs) -> str:
        agg = TimeSeriesAggregator(self.logs)
        ts_data = agg.get_time_series_data()
        
        # Grid: 1 Row per Log, 2 Cols (Rate vs Run%, Mults vs Run%)
        num_logs = len(self.logs)
        fig = make_subplots(
            rows=num_logs, cols=2,
            subplot_titles=["Rate vs Run %", "New Mults vs Run %"] * num_logs,
            vertical_spacing=0.1
        )
        
        all_calls = sorted(list(ts_data['logs'].keys()))
        
        for i, call in enumerate(all_calls):
            row = i + 1
            log_entry = ts_data['logs'][call]
            
            # Extract Cumulative Series
            # We need to re-create the Series to use .diff()
            idx = pd.to_datetime(ts_data['time_bins'])
            s_run = pd.Series(log_entry['cumulative']['run_qsos'], index=idx)
            s_sp = pd.Series(log_entry['cumulative']['sp_unk_qsos'], index=idx)
            s_mults = pd.Series(log_entry['cumulative']['mults'], index=idx)
            
            # Calculate Hourly Deltas
            h_run = s_run.diff().fillna(s_run.iloc[0])
            h_sp = s_sp.diff().fillna(s_sp.iloc[0])
            h_mults = s_mults.diff().fillna(s_mults.iloc[0])
            h_total = h_run + h_sp
            
            # Calculate Run % (Safe Division)
            # Avoid division by zero
            h_run_pct = (h_run / h_total).fillna(0) * 100
            
            # Color by Rate Intensity? Or just standard color
            color = PlotlyStyleManager._COLOR_PALETTE[i % len(PlotlyStyleManager._COLOR_PALETTE)]
            
            # Trace 1: Rate vs Run %
            fig.add_trace(
                go.Scatter(
                    x=h_run_pct,
                    y=h_total,
                    mode='markers',
                    name=f"{call} Rate",
                    marker=dict(color=color, size=8, opacity=0.7),
                    hovertemplate="Run: %{x:.1f}%<br>Rate: %{y}<extra></extra>",
                    legendgroup=call
                ),
                row=row, col=1
            )
            
            # Trace 2: Mults vs Run %
            fig.add_trace(
                go.Scatter(
                    x=h_run_pct,
                    y=h_mults,
                    mode='markers',
                    name=f"{call} Mults",
                    marker=dict(color=color, size=8, symbol='diamond', opacity=0.7),
                    hovertemplate="Run: %{x:.1f}%<br>New Mults: %{y}<extra></extra>",
                    legendgroup=call,
                    showlegend=False
                ),
                row=row, col=2
            )
            
            # Update Axes Titles
            fig.update_xaxes(title_text=f"{call} Run %", range=[-5, 105], row=row, col=1)
            fig.update_xaxes(title_text=f"{call} Run %", range=[-5, 105], row=row, col=2)
            fig.update_yaxes(title_text="Hourly Rate", row=row, col=1)
            fig.update_yaxes(title_text="Hourly Mults", row=row, col=2)

        # Layout
        title = "Correlation Analysis: Operational Efficiency"
        layout = PlotlyStyleManager.get_standard_layout(title)
        fig.update_layout(layout)
        fig.update_layout(
            height=400 * num_logs,
            width=1200,
            showlegend=True
        )
        
        create_output_directory(output_path)
        filename_calls = '_'.join([_sanitize_filename_part(c) for c in all_calls])
        base_filename = f"{self.report_id}_{filename_calls}"
        
        html_path = os.path.join(output_path, f"{base_filename}.html")
        png_path = os.path.join(output_path, f"{base_filename}.png")
        
        # Save
        config = {'toImageButtonOptions': {'filename': base_filename, 'format': 'png'}}
        fig.write_html(html_path, include_plotlyjs='cdn', config=config)
        
        try:
            fig.write_image(png_path)
        except:
            pass
            
        return html_path