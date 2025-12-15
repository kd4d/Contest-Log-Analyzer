# contest_tools/reports/chart_point_contribution.py
#
# Purpose: A chart report that generates a breakdown of total points by QSO
#          point value, comparing multiple logs side-by-side.
#
# Author: Gemini AI
# Date: 2025-12-07
# Version: 0.118.0-Beta
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
# [0.118.0-Beta] - 2025-12-15
# - Injected descriptive filename configuration for interactive HTML plot downloads.
# [1.0.0] - 2025-12-07
# - Refactored visualization engine from Matplotlib to Plotly.
# - Added HTML export capability alongside standard PNG export.
# - Integrated PlotlyStyleManager for consistent styling.
# [0.93.7-Beta] - 2025-12-04
# - Fixed runtime crash by ensuring the output directory is created before
#   saving the chart file.

import os
from typing import List, Dict, Any, Optional
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from contest_tools.reports.report_interface import ContestReport
from contest_tools.contest_log import ContestLog
from contest_tools.data_aggregators.categorical_stats import CategoricalAggregator
from contest_tools.styles.plotly_style_manager import PlotlyStyleManager
from contest_tools.reports._report_utils import create_output_directory

class Report(ContestReport):
    """
    Generates a comparative series of pie charts showing the breakdown of QSO points
    (1-point, 3-point, etc.) for each log (Totals).
    """
    report_id = 'chart_point_contribution'
    report_name = 'Point Contribution Breakdown'
    report_type = 'chart'
    supports_multi = True
    supports_pairwise = True

    def __init__(self, logs: List[ContestLog]):
        super().__init__(logs)
        self.aggregator = CategoricalAggregator()

    def _create_trace_for_log(self, log_data: Dict, color_map: Dict[Any, str]) -> Optional[go.Pie]:
        """Creates a single pie chart trace for a specific log's total data."""
        point_breakdown = log_data['breakdown']
        
        if not point_breakdown:
            return None

        # Sort items by count descending
        sorted_items = sorted(point_breakdown.items(), key=lambda item: item[1], reverse=True)
        sizes = [item[1] for item in sorted_items]
        labels = [f"{item[0]} Point" for item in sorted_items]
        
        # Get colors based on the point keys
        sorted_keys = [item[0] for item in sorted_items]
        colors = [color_map.get(k, '#7f7f7f') for k in sorted_keys]
        
        return go.Pie(
            labels=labels,
            values=sizes,
            marker=dict(colors=colors, line=dict(color='#000000', width=1)),
            textinfo='label+percent',
            hoverinfo='label+value+percent',
            hole=0.0 # Full Pie, set > 0 for Donut
        )

    def generate(self, output_path: str, **kwargs) -> List[str]:
        # Get data for ALL logs, no filters (Grand Totals)
        agg_result = self.aggregator.get_points_breakdown(self.logs)
        
        num_logs = len(self.logs)
        cols = num_logs
        rows = 1

        # Calculate subplot titles based on callsigns and total points
        subplot_titles = []
        for i, log in enumerate(self.logs):
            callsign = log.get_metadata().get('MyCall', f'Log{i+1}')
            if callsign in agg_result['logs']:
                total = agg_result['logs'][callsign]['total_points']
                subplot_titles.append(f"{callsign}<br>(Total: {total:.0f})")
            else:
                subplot_titles.append(f"{callsign}<br>(No Data)")

        # Create Subplots
        fig = make_subplots(
            rows=rows, 
            cols=cols, 
            subplot_titles=subplot_titles,
            specs=[[{'type': 'domain'}] * cols]
        )

        # Collect all unique point values across all logs for consistent coloring
        all_point_values = set()
        for log_data in agg_result['logs'].values():
            if log_data['breakdown']:
                all_point_values.update(log_data['breakdown'].keys())
        
        color_map = PlotlyStyleManager.get_point_color_map(list(all_point_values))

        # Add traces
        for i, log in enumerate(self.logs):
            callsign = log.get_metadata().get('MyCall', f'Log{i+1}')
            if callsign in agg_result['logs']:
                trace = self._create_trace_for_log(agg_result['logs'][callsign], color_map)
                if trace:
                    fig.add_trace(trace, row=1, col=i+1)

        # Standard Title Construction
        first_log = self.logs[0]
        year = first_log.get_processed_data()['Date'].iloc[0].split('-')[0]
        contest_name = first_log.get_metadata().get('ContestName', 'Unknown')
        all_calls = sorted([l.get_metadata().get('MyCall') for l in self.logs])
        
        chart_title = f"Comparative Point Contribution: {year} {contest_name} - {', '.join(all_calls)}"
        
        # Apply standard layout
        layout_config = PlotlyStyleManager.get_standard_layout(chart_title)
        fig.update_layout(**layout_config)

        # Ensure output directory exists
        create_output_directory(output_path)
        
        # Define Filenames
        base_filename = f"{self.report_id}_{'_vs_'.join(all_calls)}"
        png_file = os.path.join(output_path, f"{base_filename}.png")
        html_file = os.path.join(output_path, f"{base_filename}.html")
        
        generated_files = []

        # Save PNG (Legacy Requirement)
        try:
            fig.write_image(png_file, width=500 * cols, height=500)
            generated_files.append(png_file)
        except Exception as e:
            print(f"Warning: Could not save PNG (kaleido might be missing): {e}")

        # Save HTML (New Interactive Requirement)
        config = {'toImageButtonOptions': {'filename': base_filename, 'format': 'png'}}
        fig.write_html(html_file, include_plotlyjs='cdn', config=config)
        generated_files.append(html_file)

        return generated_files