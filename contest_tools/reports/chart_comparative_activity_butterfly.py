# contest_tools/reports/chart_comparative_activity_butterfly.py
#
# Purpose: Generates a comparative 'Butterfly' chart (stacked diverging bars)
#          visualizing Run vs S&P activity for two stations per band.
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
import os
import logging
import math
from typing import List, Dict, Any, Optional
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ..data_aggregators.matrix_stats import MatrixAggregator
from contest_tools.utils.report_utils import create_output_directory, _sanitize_filename_part, get_standard_footer, get_standard_title_lines, get_valid_dataframe, write_json_ascii
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
    
    def _determine_dimension(self) -> str:
        """
        Determine if chart should use band or mode dimension.
        Returns 'mode' for single-band, multi-mode contests, 'band' otherwise.
        """
        if not self.logs:
            return "band"
        
        try:
            contest_def = self.logs[0].contest_definition
            valid_bands = contest_def.valid_bands
            valid_modes = contest_def.valid_modes
            
            # Single-band, multi-mode -> mode dimension
            if len(valid_bands) == 1 and len(valid_modes) > 1:
                return "mode"
            
            # Check animation_dimension as a hint (if available)
            if hasattr(contest_def, 'animation_dimension'):
                anim_dim = contest_def.animation_dimension
                if anim_dim == "mode" and len(valid_bands) == 1:
                    return "mode"
        except (AttributeError, KeyError) as e:
            logging.debug(f"Could not determine dimension from contest definition: {e}")
        
        # Default: band dimension
        return "band"

    def generate(self, output_path: str, **kwargs) -> str:
        if len(self.logs) != 2:
            return "Skipping: Butterfly chart requires exactly 2 logs."

        call1 = self.logs[0].get_metadata().get('MyCall', 'LOG1')
        call2 = self.logs[1].get_metadata().get('MyCall', 'LOG2')

        # 1. Determine dimension (band or mode)
        dimension = self._determine_dimension()

        # 2. Fetch Data
        # --- Phase 1 Performance Optimization: Use Cached Aggregator Data ---
        get_cached_stacked_matrix_data = kwargs.get('_get_cached_stacked_matrix_data')
        aggregator = MatrixAggregator(self.logs)
        
        if dimension == "mode":
            # Use mode-based stacked matrix data
            data = aggregator.get_mode_stacked_matrix_data(bin_size='60min')
            items = data.get('modes', [])  # Modes instead of bands
        else:
            # Use band-based stacked matrix data
            if get_cached_stacked_matrix_data:
                # Use cached stacked matrix data (avoids recreating aggregator and recomputing)
                data = get_cached_stacked_matrix_data(bin_size='60min', mode_filter=None)
            else:
                # Fallback to old behavior for backward compatibility
                data = aggregator.get_stacked_matrix_data(bin_size='60min')
            items = data.get('bands', [])  # Bands
        
        time_bins = data.get('time_bins', [])
        
        if not items or not time_bins:
            return "No data available to plot."

        # 3. Setup Output
        charts_dir = output_path
        create_output_directory(charts_dir)

        # 4. Generate Plot
        try:
            filename_base = f"chart_comparative_activity_butterfly_{_sanitize_filename_part(call1)}_{_sanitize_filename_part(call2)}"
            
            # Create the figure
            fig = self._create_figure(data, time_bins, items, call1, call2, dimension)
            
            generated_files = []

            # 1. Save JSON (Web Component Artifact) - 7-bit ASCII only
            json_filename = f"{filename_base}.json"
            json_path = os.path.join(charts_dir, json_filename)
            write_json_ascii(fig.to_json(), json_path)
            generated_files.append(json_filename)

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
            items: List[str], call1: str, call2: str, dimension: str = "band") -> go.Figure:
        """
        Create butterfly chart figure.
        
        Args:
            data: Matrix data (either band-based or mode-based)
            time_bins: List of time bin strings
            items: List of items (bands or modes) to plot
            call1: First callsign
            call2: Second callsign
            dimension: "band" or "mode"
        """
        num_items = len(items)
        # [ARCHITECTURE] N+1 Rows: Row 1 = Header, Rows 2..N+1 = Charts
        total_rows = num_items + 1
        
        # Calculate relative heights: Header=15%, Rest distributed evenly
        header_height = 0.15
        chart_height = (1.0 - header_height) / num_items
        row_heights = [header_height] + [chart_height] * num_items

        # Determine subplot titles based on dimension
        if dimension == "mode":
            subplot_titles = [""] + [f"Mode: {m}" for m in items]
        else:
            subplot_titles = [""] + [f"Band: {b}" for b in items]

        fig = make_subplots(
            rows=total_rows, 
            cols=1, 
            shared_xaxes=False,  # Don't share - we'll manually link item rows only
            vertical_spacing=0.02,
            row_heights=row_heights,
            subplot_titles=subplot_titles
        )

        # --- Row 1: Header & Legend Domain ---
        # Add invisible trace to establish grid
        fig.add_trace(go.Scatter(x=[None], y=[None], showlegend=False, hoverinfo='skip'), row=1, col=1)
        
        # Add Dummy Legend Traces (Order: Run, S&P, Unknown)
        for label in ['Run', 'S&P', 'Unknown']:
             color = self.COLORS[label]
             fig.add_trace(
                go.Bar(
                    x=[None], y=[None],
                    name=label,
                    marker_color=color,
                    showlegend=True,
                ),
                row=1, col=1
            )
        
        # Hide axes for Header Row
        fig.update_xaxes(visible=False, row=1, col=1)
        fig.update_yaxes(visible=False, row=1, col=1)

        # --- Rows 2..N+1: Charts ---
        for i, item in enumerate(items):
            row_idx = i + 2
            
            # --- Log 1 (Positive) ---
            # Order: Run, S&P, Unknown
            l1_run = data['logs'][call1][item]['Run']
            l1_sp = data['logs'][call1][item]['S&P']
            l1_unk = data['logs'][call1][item]['Unknown']

            # Run
            fig.add_trace(go.Bar(
                x=time_bins, y=l1_run,
                name='Run', marker_color=self.COLORS['Run'],
                showlegend=False, hoverinfo='x+y+name'
            ), row=row_idx, col=1)

            # S&P
            fig.add_trace(go.Bar(
                x=time_bins, y=l1_sp,
                name='S&P', marker_color=self.COLORS['S&P'],
                showlegend=False, hoverinfo='x+y+name'
            ), row=row_idx, col=1)

            # Unknown
            fig.add_trace(go.Bar(
                x=time_bins, y=l1_unk,
                name='Unknown', marker_color=self.COLORS['Unknown'],
                showlegend=False, hoverinfo='x+y+name'
            ), row=row_idx, col=1)

            # --- Log 2 (Negative) ---
            # Negate values to stack downwards
            l2_run = [-v for v in data['logs'][call2][item]['Run']]
            l2_sp = [-v for v in data['logs'][call2][item]['S&P']]
            l2_unk = [-v for v in data['logs'][call2][item]['Unknown']]

            # Run
            fig.add_trace(go.Bar(
                x=time_bins, y=l2_run,
                name='Run', marker_color=self.COLORS['Run'],
                showlegend=False, hoverinfo='x+y+name',
                customdata=[abs(v) for v in l2_run],
                hovertemplate='%{x}<br>Run: %{customdata}'
            ), row=row_idx, col=1)

            # S&P
            fig.add_trace(go.Bar(
                x=time_bins, y=l2_sp,
                name='S&P', marker_color=self.COLORS['S&P'],
                showlegend=False, hoverinfo='x+y+name',
                customdata=[abs(v) for v in l2_sp],
                hovertemplate='%{x}<br>S&P: %{customdata}'
            ), row=row_idx, col=1)

            # Unknown
            fig.add_trace(go.Bar(
                x=time_bins, y=l2_unk,
                name='Unknown', marker_color=self.COLORS['Unknown'],
                showlegend=False, hoverinfo='x+y+name',
                customdata=[abs(v) for v in l2_unk],
                hovertemplate='%{x}<br>Unk: %{customdata}'
            ), row=row_idx, col=1)
             
            # Add zero line
            fig.add_hline(y=0, line_width=1, line_color="black", row=row_idx, col=1)
            
            # Formatting Y-Axis (Calculated from stacked sum)
            l1_total = [x+y+z for x,y,z in zip(l1_run, l1_sp, l1_unk)]
            l2_total = [abs(x)+abs(y)+abs(z) for x,y,z in zip(l2_run, l2_sp, l2_unk)]
            item_max = max(max(l1_total), max(l2_total)) if l1_total else 0
            rounded_limit = self._get_rounded_axis_limit(item_max)

            fig.update_yaxes(
                title_text=item,
                range=[-rounded_limit, rounded_limit],
                tickmode='array',
                tickvals=[-rounded_limit, -rounded_limit/2, 0, rounded_limit/2, rounded_limit],
                ticktext=[str(int(rounded_limit)), "", "0", "", str(int(rounded_limit))], # Simplified ticks
                row=row_idx, col=1
            )
            
            # X-Axis configuration
            if i == num_items - 1:
                # Bottom chart: show labels and title
                # Increased standoff to 40px to prevent crowding with footer
                fig.update_xaxes(title_text="Time (UTC)", title_standoff=40, row=row_idx, col=1)
            else:
                # Other item charts: hide labels but link to bottom axis
                # This synchronizes all item rows (2-N+1) to share the same x-axis domain
                fig.update_xaxes(matches=f'x{total_rows}', showticklabels=False, row=row_idx, col=1)

        # Layout Updates
        # 3-Line Title Construction
        modes_present = set()
        for log in [self.logs[0], self.logs[1]]:
             df = get_valid_dataframe(log)
             if 'Mode' in df.columns:
                 modes_present.update(df['Mode'].dropna().unique())
        
        # Determine title dimension label
        if dimension == "mode":
            dimension_label = "All Modes"
        else:
            dimension_label = "All Bands"
        
        title_lines = get_standard_title_lines(self.report_name, self.logs, dimension_label, None, modes_present)
        
        footer_text = get_standard_footer(self.logs)
        
        fig.update_layout(
            template="plotly_white",
            barmode='relative', # Fix: Correct stacking for butterfly
            bargap=0, # Histogram look
            margin=dict(t=50, b=180, l=110, r=50), # Increased bottom margin for footer, left for y-axis spacing
            height=max(900, 200 * num_items + 150),
            width=1200,
            # Legend in Header Row (Top Right)
            legend=dict(
                orientation="h",
                yanchor="top", y=1.0, 
                xanchor="right", x=1.0, 
                bgcolor="rgba(255,255,255,0.9)", 
                bordercolor="Black", borderwidth=1
            )
        )
        
        # Add Title Annotation (Row 1 Left)
        fig.add_annotation(
            text=f"<b>{title_lines[0]}</b><br><sup>{title_lines[1]}</sup>",
            xref="paper", yref="paper",
            x=0, y=1.0,
            xanchor="left", yanchor="top",
            showarrow=False,
            font=dict(size=20)
        )
        
        # Add Footer Annotation (Bottom Center) - Using absolute pixel positioning
        fig.add_annotation(
            text=footer_text.replace('\n', '<br>'),
            xref="paper", yref="paper",
            x=0.5, y=0,
            xanchor="center", yanchor="top",
            showarrow=False,
            font=dict(size=10, color="gray"),
            yshift=-80  # Push 80px below plot area (more space from "Time (UTC)")
        )

        return fig

    def _get_rounded_axis_limit(self, value: float) -> int:
        if value <= 0: return 10
        # Add 10% headroom
        target = value * 1.1
        # Round up to nearest 10
        return math.ceil(target / 10) * 10