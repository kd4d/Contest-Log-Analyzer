# contest_tools/reports/chart_qso_breakdown.py
#
# Purpose: A chart report that generates a stacked bar chart comparing two logs
#          on common/unique QSOs broken down by Run vs. Search & Pounce (S&P) mode.
#
# Author: Gemini AI
# Date: 2025-12-29
# Version: 0.145.0-Beta
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
# [0.145.0-Beta] - 2025-12-29
# - Removed manual layout overrides (margins) to allow PlotlyStyleManager authoritative control.
# [0.144.1-Beta] - 2025-12-29
# - Implemented "Hard Deck" strategy: Fixed height (800px), autosize=True, disabled 'responsive' config.
# [0.143.3-Beta] - 2025-12-28
# - Implemented "Safety Gap" strategy: Reduced HTML height to 800px to prevent scrollbars.
# [0.143.2-Beta] - 2025-12-28
# - Fixed HTML viewport issue by enforcing fixed height (850px).
# [0.143.1-Beta] - 2025-12-28
# - Updated layout configuration to use the "Legend Belt" strategy (Protocol 1.2.0).
# - Migrated title generation to pass List[str] for Annotation Stack rendering.
# [0.143.0-Beta] - 2025-12-28
# - Migrated title generation to PlotlyStyleManager annotation stack ("Pixel-Locked Margins").
# - Relocated legend to inside the plot area to reclaim vertical space.
# - Removed manual top margin override to fix scrollbar overflow regression.
# [0.142.0-Beta] - 2025-12-27
# - Increased subplot vertical_spacing to 0.15 to prevent label overlap.
# - Reduced X-axis title_standoff to 5 to tighten Band Label placement.
# - Increased bottom margin to 60px to accommodate labels.
# [0.141.0-Beta] - 2025-12-25
# - Removed floating subplot titles to eliminate overlap.
# - Added x-axis titles to subplots for clearer band identification.
# - Reduced vertical spacing to 0.05 and adjusted margins (t=100, b=40).
# [0.140.0-Beta] - 2025-12-25
# - Optimized layout margins (t=90, b=70) to balance title clearance vs footer visibility.
# - Increased subplot vertical spacing to 0.08 to prevent title collision.
# [0.137.0-Beta] - 2025-12-25
# - Implemented "Safe Zone" layout strategy with increased margins (t=120, b=50, l=50, r=50)
#   for dashboard integration to prevent overlap.
# [0.136.0-Beta] - 2025-12-25
# - Optimized layout for dashboard integration ("Fill the Viewport"):
#   - Migrated band labels to subplot titles for better association.
#   - Reduced vertical spacing between subplots to 0.05.
#   - Tightened HTML layout margins (t=60, b=30, l=10, r=10).
# [0.135.0-Beta] - 2025-12-25
# - Forced removal of fixed dimensions for HTML output using direct attribute assignment.
# - Optimized margins (t=100, b=40) for dashboard integration.
# [0.134.0-Beta] - 2025-12-25
# - Reverted vertical spacing to 0.12 to accommodate X-axis labels.
# - Restored standard X-axis labels (Band Name) and removed in-chart badges.
# [0.133.0-Beta] - 2025-12-25
# - Replaced external subplot titles with in-chart badges to save vertical space.
# - Reduced subplot vertical spacing.
# [0.132.0-Beta] - 2025-12-25
# - Increased subplot vertical spacing to 0.15.
# - Added explicit X-axis labels (Band Name) to each subplot.
# - Enabled responsive resizing for HTML dashboard integration.
# [0.131.1-Beta] - 2025-12-25
# - Updated band sorting logic to use canonical frequency order via ContestLog._HAM_BANDS.
# [0.131.0-Beta] - 2025-12-20
# - Refactored to use `get_standard_title_lines` for standardized 3-line headers.
# - Implemented explicit "Smart Scoping" for title generation.
# - Added footer metadata via `get_cty_metadata`.
# [0.118.0-Beta] - 2025-12-15
# - Injected descriptive filename configuration for interactive HTML plot downloads.
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
from contest_tools.reports._report_utils import get_valid_dataframe, create_output_directory, _sanitize_filename_part, get_cty_metadata, get_standard_title_lines

class Report(ContestReport):
    """
    Generates a stacked bar chart comparing two logs on common/unique QSOs
    broken down by Run vs. Search & Pounce (S&P) mode.
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

        raw_bands = set(df1['Band'].unique()) | set(df2['Band'].unique())
        canonical_band_order = [b[1] for b in ContestLog._HAM_BANDS]
        bands = sorted(raw_bands, key=lambda b: canonical_band_order.index(b) if b in canonical_band_order else -1)

        if not bands:
            return []

        # Grid Calculation
        num_bands = len(bands)
        cols = min(3, num_bands)
        rows = (num_bands + cols - 1) // cols

        fig = make_subplots(
            rows=rows, 
            cols=cols, 
            shared_yaxes=True,
            vertical_spacing=0.15
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
            fig.update_xaxes(title_text=band, title_standoff=5, row=row, col=col)

        # Standard Layout Application
        modes_present = set(df1['Mode'].dropna().unique()) | set(df2['Mode'].dropna().unique())
        
        title_lines = get_standard_title_lines(self.report_name, self.logs, "All Bands", None, modes_present)

        footer_text = f"Contest Log Analytics by KD4D\n{get_cty_metadata(self.logs)}"
        
        # Use Annotation Stack (List) for precise title spacing control
        layout_config = PlotlyStyleManager.get_standard_layout(title_lines, footer_text)
        fig.update_layout(layout_config)
        
        # Specific Adjustments
        fig.update_layout(
            barmode='stack',
            showlegend=True,
            # Legend Belt: Horizontal, Centered, Just above grid (y=1.02)
            legend=dict(orientation="h", x=0.5, y=1.02, xanchor="center", yanchor="bottom", bgcolor="rgba(255,255,255,0.8)", bordercolor="Black", borderwidth=1)
        )

        create_output_directory(output_path)
        call1 = self.log1.get_metadata().get('MyCall')
        call2 = self.log2.get_metadata().get('MyCall')
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
        
        # Force fixed height with responsive width (Hard Deck Strategy)
        fig.update_layout(autosize=True, height=800)
        
        config = {
            'toImageButtonOptions': {'filename': base_filename, 'format': 'png'},
        }
        fig.write_html(html_file, include_plotlyjs='cdn', config=config)

        # Return list of successfully created files (checking existence)
        outputs = []
        if os.path.exists(png_file):
            outputs.append(png_file)
        if os.path.exists(html_file):
            outputs.append(html_file)

        return outputs