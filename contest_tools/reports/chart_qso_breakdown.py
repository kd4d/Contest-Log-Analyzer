# contest_tools/reports/chart_qso_breakdown.py
#
# Purpose: A chart report that generates a stacked bar chart comparing two logs
#          on common/unique QSOs broken down by Run vs. Search & Pounce (S&P) mode.
#
# Author: Gemini AI
# Date: 2025-12-14
# Version: 0.115.2-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# --- Revision History ---
# [0.115.2-Beta] - 2025-12-15
# - Increased top margin to 140px to prevent the two-line header from overlapping subplot titles.
# [0.115.1-Beta] - 2025-12-15
# - Standardized chart header to the two-line format (Report Name + Context).
# - Optimized x-axis labels ("Unique Call" -> "Call", "Common (Both)" -> "Common")
#   to prevent overlapping text in the 3-column layout.
# [1.0.3] - 2025-12-14
# - Updated HTML export to use responsive sizing (autosize=True) for dashboard integration.
# - Maintained fixed resolution for PNG exports.
# [1.0.2] - 2025-12-14
# - Updated file generation to use `_sanitize_filename_part` for strict lowercase naming.
# [1.0.1] - 2025-12-08
# - Updated PNG output to use landscape orientation (width=1600px).
# [1.0.0] - 2025-12-08
# - Migrated visualization engine from Matplotlib to Plotly.
# - Added interactive HTML output support.
# - Applied standard Phase 2 styling via PlotlyStyleManager.
# [0.93.7-Beta] - 2025-12-04
# - Fixed runtime crash by ensuring the output directory is created before
#   saving the chart file.
import os
from typing import List, Dict, Tuple
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from contest_tools.reports.report_interface import ContestReport
from contest_tools.contest_log import ContestLog
from contest_tools.data_aggregators.categorical_stats import CategoricalAggregator
from contest_tools.styles.plotly_style_manager import PlotlyStyleManager
from contest_tools.reports._report_utils import get_valid_dataframe, create_output_directory, _sanitize_filename_part

class Report(ContestReport):
    """
    Generates a stacked bar chart comparing two logs on common/unique QSOs
    broken down by Run vs. Search & Pounce (S&P) mode for each band.
    """
    report_id = 'qso_breakdown_chart' # Aligned with Interpretation Guide
    report_name = 'QSO Breakdown Chart'
    report_type = 'chart'
    
    supports_pairwise = True

    def __init__(self, logs: List[ContestLog]):
        super().__init__(logs)
        if len(logs) != 2:
            raise ValueError("ChartQSOBreakdown requires exactly two logs for comparison.")
        self.log1 = logs[0]
        self.log2 = logs[1]
        self.aggregator = CategoricalAggregator()

    def _prepare_data(self, band: str) -> Dict:
        """
        Aggregates data for a specific band using CategoricalAggregator.
        """
        comparison_data = self.aggregator.compute_comparison_breakdown(
            self.log1, 
            self.log2, 
            band_filter=band
        )
        
        categories = [
            f"{self.log1.get_metadata().get('MyCall')}",
            "Common",
            f"{self.log2.get_metadata().get('MyCall')}"
        ]
        
        modes = ['Run', 'S&P', 'Mixed/Unk']
        
        data = {
            'Run': [
                comparison_data['log1_unique']['run'],
                comparison_data['common']['run_both'],
                comparison_data['log2_unique']['run']
            ],
            'S&P': [
                comparison_data['log1_unique']['sp'],
                comparison_data['common']['sp_both'],
                comparison_data['log2_unique']['sp']
            ],
            'Mixed/Unk': [
                comparison_data['log1_unique']['unk'],
                comparison_data['common']['mixed'],
                comparison_data['log2_unique']['unk']
            ]
        }
         
    
        return {
            'categories': categories,
            'modes': modes,
            'data': data
        }


    def generate(self, output_path: str, **kwargs) -> List[str]:
        """
        Generates the stacked bar chart report and saves it to file(s).
        Returns a list of generated file paths.
        """
        df1 = get_valid_dataframe(self.log1)
        df2 = get_valid_dataframe(self.log2)

        bands = sorted(set(df1['Band'].unique()) | set(df2['Band'].unique()))

        if not bands:
            return []

        # Grid Calculation
        num_bands = len(bands)
        cols = min(3, num_bands)
        rows = (num_bands + cols - 1) // cols
        
        subplot_titles = [f"{band} Band Breakdown" for band in bands]

        fig = make_subplots(
            rows=rows, 
            cols=cols, 
            subplot_titles=subplot_titles, 
            shared_yaxes=True
        )

        colors = PlotlyStyleManager.get_qso_mode_colors()

        for i, band in enumerate(bands):
            # Plotly uses 1-based indexing for rows/cols
            row = (i // cols) + 1
            col = (i % cols) + 1
            
            data_dict = self._prepare_data(band)
            categories = data_dict['categories']
            modes = data_dict['modes']
            data = data_dict['data']
            
            # Show legend only on the first subplot to prevent duplication
            show_legend = (i == 0)

    
            for mode in modes:
                fig.add_trace(
                    go.Bar(
                        name=mode,
                        x=categories,
                        y=data[mode],
                        marker_color=colors[mode],
                        showlegend=show_legend,
                        legendgroup=mode # Groups traces so toggling 'Run' toggles it on all subplots
                    ),
                    row=row, col=col
                )

        # Standard Layout Application
        metadata = self.log1.get_metadata()
        year = df1['Date'].dropna().iloc[0].split('-')[0] if not df1.empty else "----"
        contest_name = metadata.get('ContestName', '')
        event_id = metadata.get('EventID', '')
        call1 = self.log1.get_metadata().get('MyCall')
        call2 = self.log2.get_metadata().get('MyCall')
        
        title_line1 = self.report_name
        title_line2 = f"{year} {event_id} {contest_name} - {call1} vs. {call2}".strip().replace("  ", " ")
        final_title = f"{title_line1}<br>{title_line2}"
        
        layout_config = PlotlyStyleManager.get_standard_layout(final_title)
        fig.update_layout(layout_config)
        
        # Specific Adjustments
        fig.update_layout(
            barmode='stack',
            margin=dict(t=140) # Increased top margin to prevent title overlap
        )

        create_output_directory(output_path)
        c1_safe = _sanitize_filename_part(call1)
        c2_safe = _sanitize_filename_part(call2)
        base_filename = f"{self.report_id}_{c1_safe}_{c2_safe}"
        
        # 1. Save Static Image (PNG)
        # Use specific width=1600 to enforce landscape orientation for standard reports
        png_file = os.path.join(output_path, f"{base_filename}.png")
        try:
            # Fixed sizing for PNG
            fig.update_layout(
                autosize=False,
                width=1600,
                height=400 * rows
            )
            fig.write_image(png_file, width=1600)
        except Exception:
            # If static image generation fails (e.g. missing kaleido), logging would go here.
            # We proceed to save HTML.
            pass

        # 2. Save Interactive HTML
        html_file = os.path.join(output_path, f"{base_filename}.html")
        
        # Responsive sizing for HTML
        fig.update_layout(
            autosize=True,
            width=None,
            height=None
        )
        fig.write_html(html_file, include_plotlyjs='cdn')

        # Return list of successfully created files (checking existence)
        outputs = []
        if os.path.exists(png_file):
            outputs.append(png_file)
        if os.path.exists(html_file):
            outputs.append(html_file)

        return outputs