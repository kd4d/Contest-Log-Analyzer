# contest_tools/styles/plotly_style_manager.py
#
# Purpose: Centralized management of Plotly styles and color schemes
#          to ensure consistency across all interactive visual reports.
#
# Author: Gemini AI
# Date: 2025-12-20
# Version: 1.1.0
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
# [1.1.0] - 2025-12-20
# - Added footer_text support to `get_standard_layout` for branding/metadata.
# [1.0.0] - 2025-12-07
# - Initial creation to support Phase 2 Visualization Standardization.
# - Implemented color map generators and standard layout factories.

from typing import Dict, List, Any
import plotly.graph_objects as go

class PlotlyStyleManager:
    """
    Provides standardized color maps and style configurations for
    Plotly-based reports.
    """

    # Standard Tableau 10 Color Palette (Hex)
    # Copied to avoid dependency on matplotlib.colors
    _COLOR_PALETTE = [
        '#1f77b4', # Blue
        '#ff7f0e', # Orange
        '#2ca02c', # Green
        '#d62728', # Red
        '#9467bd', # Purple
        '#8c564b', # Brown
        '#e377c2', # Pink
        '#7f7f7f', # Gray
        '#bcbd22', # Olive
        '#17becf'  # Cyan
    ]

    @staticmethod
    def get_point_color_map(point_values: List[Any]) -> Dict[Any, str]:
        """
        Generates a consistent color map for QSO point values.
        
        Args:
            point_values: A list of unique point values (e.g., [1, 2, 4]).
            
        Returns:
            A dictionary mapping point values to hex color strings.
        """
        # Sort to ensure deterministic color assignment
        sorted_vals = sorted(point_values, key=lambda x: str(x))
        color_map = {}
        
        for i, val in enumerate(sorted_vals):
            # Cycle through palette if more values than colors
            color = PlotlyStyleManager._COLOR_PALETTE[i % len(PlotlyStyleManager._COLOR_PALETTE)]
            color_map[val] = color
            
        return color_map

    @staticmethod
    def get_qso_mode_colors() -> Dict[str, str]:
        """
        Returns the standard color scheme for QSO breakdown modes.

        Returns:
            Dictionary mapping modes ('Run', 'S&P', 'Mixed/Unk') to colors.
        """
        return {
            'Run': '#2ca02c',       # Green
            'S&P': '#1f77b4',       # Blue
            'Mixed/Unk': '#7f7f7f'  # Gray
        }

    @staticmethod
    def get_standard_layout(title: str, footer_text: str = None) -> Dict[str, Any]:
        """
        Returns a standard Plotly layout dictionary.
        
        Args:
            title: The main chart title.
            footer_text: Optional text to display as a footer (e.g., Branding/CTY info).
            
        Returns:
            A dictionary suitable for passing to fig.update_layout().
        """
        layout = {
            "title": {
                "text": title,
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 20, "family": "Arial, sans-serif", "weight": "bold"}
            },
            "font": {"family": "Arial, sans-serif"},
            "template": "plotly_white",
            "margin": {"l": 50, "r": 50, "t": 100, "b": 100}, # Increased t/b for headers/footers
            "showlegend": True
        }

        if footer_text:
            layout["annotations"] = [
                dict(
                    x=0.5,
                    y=-0.15, # Position below X-axis
                    xref="paper",
                    yref="paper",
                    text=footer_text.replace('\n', '<br>'), # Convert newlines for Plotly
                    showarrow=False,
                    font=dict(size=12, color="#7f7f7f"),
                    align="center",
                    valign="top"
                )
            ]
            
        return layout