# contest_tools/reports/qso_chart_helpers.py
#
# Purpose: Shared module-level helper functions for QSO breakdown chart generation.
#          Provides common utilities for chart styling, file operations, and data preparation.
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

import os
from typing import List
import plotly.graph_objects as go
from ..contest_log import ContestLog
from ..utils.callsign_utils import build_callsigns_filename_part
from ..utils.report_utils import create_output_directory, get_standard_footer, get_standard_title_lines
from ..styles.plotly_style_manager import PlotlyStyleManager


def build_qso_chart_filename(report_id: str, logs: List[ContestLog], suffix: str = "") -> str:
    """
    Builds standardized filename for QSO breakdown charts.
    
    Args:
        report_id: The report identifier (e.g., 'qso_breakdown_chart_contest_wide')
        logs: List of ContestLog objects
        suffix: Optional suffix to append (e.g., 'band_distribution')
    
    Returns:
        Filename string following convention: {report_id}--{callsigns}.{ext}
        If suffix provided: {report_id}_{suffix}--{callsigns}.{ext}
    """
    all_calls = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in logs])
    callsigns_part = build_callsigns_filename_part(all_calls)
    
    if suffix:
        base = f"{report_id}_{suffix}--{callsigns_part}"
    else:
        base = f"{report_id}--{callsigns_part}"
    
    return base


def apply_qso_chart_styling(fig: go.Figure, title_lines: List[str], footer_text: str, 
                            barmode: str = 'stack', show_legend: bool = True) -> None:
    """
    Applies standard styling to QSO breakdown charts.
    
    Args:
        fig: Plotly figure object to style
        title_lines: List of title lines (from get_standard_title_lines)
        footer_text: Footer text (from get_standard_footer)
        barmode: Bar mode ('stack' or 'group')
        show_legend: Whether to show legend
    """
    # Detect if this is a subplot chart (has _grid_ref attribute)
    is_subplot = hasattr(fig, '_grid_ref') and fig._grid_ref is not None
    
    # Apply standard layout
    layout_config = PlotlyStyleManager.get_standard_layout(title_lines, footer_text, is_subplot=is_subplot)
    fig.update_layout(layout_config)
    
    # QSO-specific adjustments
    # Adjust legend position for subplot charts to account for larger title area
    # Higher y values move legend further up (away from plot area)
    # For regular charts (like contest-wide breakdown), use lower position to avoid title overlap
    # For subplot charts (like band distribution), use higher position for better spacing
    legend_y = 1.05 if is_subplot else 1.025
    
    fig.update_layout(
        barmode=barmode,
        showlegend=show_legend,
        # Legend Belt: Horizontal, Centered, Positioned below title area
        legend=dict(
            orientation="h",
            x=0.5,
            y=legend_y,
            xanchor="center",
            yanchor="bottom",
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="Black",
            borderwidth=1
        )
    )


def save_qso_chart_files(fig: go.Figure, output_path: str, base_filename: str) -> List[str]:
    """
    Saves QSO chart as HTML and JSON files.
    
    Args:
        fig: Plotly figure object
        output_path: Directory to save files
        base_filename: Base filename (without extension)
    
    Returns:
        List of successfully created file paths
    """
    create_output_directory(output_path)
    
    filepath_html = os.path.join(output_path, f"{base_filename}.html")
    filepath_json = os.path.join(output_path, f"{base_filename}.json")
    
    outputs = []
    
    try:
        # 1. Save HTML (Interactive - Fluid)
        fig.update_layout(
            autosize=True,
            height=None,
            width=None
        )
        config = {'toImageButtonOptions': {'filename': base_filename, 'format': 'png'}}
        fig.write_html(filepath_html, include_plotlyjs='cdn', config=config)
        
        # 2. Save JSON (Component Data)
        fig.write_json(filepath_json)
        
    except Exception as e:
        # Log error but don't fail completely
        pass
    
    # Return list of successfully created files (checking existence)
    if os.path.exists(filepath_html):
        outputs.append(filepath_html)
    if os.path.exists(filepath_json):
        outputs.append(filepath_json)
    
    return outputs


def prepare_qso_chart_title(report_name: str, logs: List[ContestLog], 
                           scope: str = "All Bands", mode_filter: str = None) -> List[str]:
    """
    Prepares title lines for QSO breakdown charts.
    
    Args:
        report_name: Name of the report
        logs: List of ContestLog objects
        scope: Scope description (e.g., "All Bands", "Contest Total")
        mode_filter: Optional mode filter
    
    Returns:
        List of title lines (compatible with get_standard_title_lines)
    """
    modes_present = set()
    for log in logs:
        df = log.get_processed_data()
        if 'Mode' in df.columns:
            modes_present.update(df['Mode'].dropna().unique())
    
    return get_standard_title_lines(report_name, logs, scope, mode_filter, modes_present)
