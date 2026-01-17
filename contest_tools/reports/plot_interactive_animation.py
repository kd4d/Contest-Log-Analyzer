# contest_tools/reports/plot_interactive_animation.py
#
# Purpose: Generates an interactive HTML animation dashboard.
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
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from datetime import datetime

from .report_interface import ContestReport
from contest_tools.utils.report_utils import create_output_directory, _sanitize_filename_part, get_standard_footer, get_standard_title_lines, get_valid_dataframe
from contest_tools.utils.callsign_utils import build_callsigns_filename_part
from ..data_aggregators.time_series import TimeSeriesAggregator
from ..data_aggregators.matrix_stats import MatrixAggregator
from ..styles.plotly_style_manager import PlotlyStyleManager

class Report(ContestReport):
    """
    Generates an interactive HTML animation dashboard.
    
    Layout:
    - Top (Row 1, Col 1-2): Racing Bar Chart (Cumulative Score/QSOs).
    - Bottom Left (Row 2, Col 1): Hourly QSO Rate (Grouped by Station, Stacked by Mode).
    - Bottom Right (Row 2, Col 2): Cumulative QSO Rate (Grouped by Station, Stacked by Mode).
    """
    
    report_id: str = "interactive_animation"
    report_name: str = "Interactive Contest Animation"
    report_type: str = "animation"
    is_specialized: bool = False
    supports_multi: bool = True
    supports_single: bool = True  # Generate single-log files for individual analysis

    def _get_mode_color(self, base_hex: str, mode: str) -> str:
        """Calculates color based on mode: Run=Solid, S&P=50% Opacity, Unknown=Light Gray."""
        if mode == 'Unknown':
            return '#d3d3d3'  # Neutral Light Gray
        
        if mode == 'Run':
            return base_hex
            
        # S&P: Manual Hex to RGBA (No matplotlib dependency)
        hex_clean = base_hex.lstrip('#')
        if len(hex_clean) == 3:
            hex_clean = ''.join([c*2 for c in hex_clean])
            
        r = int(hex_clean[0:2], 16)
        g = int(hex_clean[2:4], 16)
        b = int(hex_clean[4:6], 16)
        return f"rgba({r},{g},{b},0.5)"
    
    def _format_time_display(self, iso_string: str) -> Tuple[str, str]:
        """
        Formats ISO time string for display.
        
        Args:
            iso_string: ISO format string like "2024-09-28T00:00:00"
        
        Returns:
            Tuple of (full_format, compact_format):
            - full_format: "2024-09-28 00:00 UTC" (for currentvalue)
            - compact_format: "Sep 28, 00:00" (for slider labels)
        """
        try:
            # Parse ISO format: "2024-09-28T00:00:00" or "2024-09-28T00:00:00+00:00"
            dt = pd.to_datetime(iso_string)
            
            # Full format: "2024-09-28 00:00 UTC"
            full_format = dt.strftime("%Y-%m-%d %H:%M UTC")
            
            # Compact format: "Sep 28, 00:00"
            compact_format = dt.strftime("%b %d, %H:%M")
            
            return full_format, compact_format
        except Exception as e:
            logging.warning(f"Error formatting time string '{iso_string}': {e}")
            # Fallback: try to extract what we can
            if 'T' in iso_string:
                date_part = iso_string.split('T')[0]
                time_part = iso_string.split('T')[1][:5] if len(iso_string.split('T')) > 1 else "00:00"
                return f"{date_part} {time_part} UTC", f"{date_part} {time_part}"
            return iso_string, iso_string

    def _determine_dimension(self) -> str:
        """
        Determines visualization dimension from contest definition.
        Reads JSON configuration (animation_dimension field) or auto-detects for mode-divided contests.
        
        Returns:
            'band' or 'mode' - the primary dimension for visualization
        """
        if not self.logs:
            return "band"  # Default fallback
        
        contest_def = self.logs[0].contest_definition
        
        # Explicit JSON config wins
        if contest_def.animation_dimension:
            return contest_def.animation_dimension
        
        # Auto-detect: Mode-divided JSON (contest name ends with mode suffix)
        contest_name = contest_def.contest_name
        if contest_name.endswith(('-CW', '-SSB', '-RTTY', '-PH')):
            # Mode-divided JSON → single mode per instance → band dimension
            return "band"
        
        # Default: band dimension (mode-divided contests)
        # Multi-mode contests without explicit config will use this (may log warning in future)
        return "band"

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the HTML animation.
        """
        create_output_directory(output_path)
        
        # Determine visualization dimension
        dimension = self._determine_dimension()
        
        # 1. Prepare Data
        if dimension == 'mode':
            data = self._prepare_data_mode(**kwargs)
        else:
            data = self._prepare_data_band(**kwargs)
        
        time_bins = data['time_bins']
        callsigns = data['callsigns']
        
        if not time_bins:
            return "No data available to generate animation."
        
        # Verify all callsigns have data in matrix
        if dimension == 'mode':
            for call in callsigns:
                if call not in data['matrix_hourly']:
                    logging.error(f"ERROR: Missing callsign {call} in matrix_hourly for mode dimension")
                elif data['modes'] and data['modes'][0] not in data['matrix_hourly'][call]:
                    logging.error(f"ERROR: Missing mode data for callsign {call} in matrix_hourly")
        elif dimension == 'band':
            for call in callsigns:
                if call not in data['matrix_hourly']:
                    logging.error(f"ERROR: Missing callsign {call} in matrix_hourly for band dimension")

        # Determine dimension label and subplot titles based on dimension
        if dimension == 'mode':
            dimension_label = "Mode"
            subplot_title_2 = "Hourly Rate (By Mode)"
            subplot_title_3 = "Cumulative QSOs (By Mode)"
        else:
            dimension_label = "Band"
            subplot_title_2 = "Hourly Rate (By Band & Mode)"
            subplot_title_3 = "Cumulative QSOs (By Band & Mode)"

        # 2. Setup Figure Layout
        fig = make_subplots(
            rows=2, cols=2,
            specs=[[{"colspan": 2}, None], [{}, {}]],
            subplot_titles=("Cumulative Score Progression", subplot_title_2, subplot_title_3),
            vertical_spacing=0.15,
            horizontal_spacing=0.1
        )

        # 3. Initialize Base Traces (Frame 0)
        # We create empty traces that will be updated by frames
        
        # --- Pane 1: Racing Bars (Top) ---
        # Initialize with zeros
        fig.add_trace(
            go.Bar(
                x=[0] * len(callsigns),
                y=callsigns,
                orientation='h',
                name='Score',
                marker=dict(color=PlotlyStyleManager._COLOR_PALETTE[:len(callsigns)]),
                text=[0] * len(callsigns),
                textposition='auto',
                showlegend=False
            ),
            row=1, col=1
        )

        # --- Pane 2 & 3: Stacked/Grouped Bars (Bottom) ---
        # Logic: For each Station, we add 3 traces (Run, S&P, Unk) to EACH subplot.
        # They share the X-axis (Bands or Modes depending on dimension).
        # We use 'offsetgroup' to group by Call, but stack by RunStatus within that group.
        x_axis_items = data['bands'] if dimension == 'band' else data['modes']
        base_palette = PlotlyStyleManager._COLOR_PALETTE
        run_statuses = ['Run', 'S&P', 'Unknown']
        
        for i, call in enumerate(callsigns):
            # Calculate offset to group bars side-by-side
            # This is handled automatically if we assign unique offsetgroups per call
            
            # Assign base color cyclically based on station index
            base_color = base_palette[i % len(base_palette)]
            
            for run_status in run_statuses:
                color = self._get_mode_color(base_color, run_status)
                
                # Bottom Left: Hourly
                fig.add_trace(
                    go.Bar(
                        name=call,
                        x=x_axis_items,
                        y=[0] * len(x_axis_items),
                        marker_color=color,
                        legendgroup=call,
                        offsetgroup=call, # Group by Call
                        showlegend=(run_status == 'Run'), # Only show legend once per call
                        textposition='none'
                    ),
                    row=2, col=1
                )
                
                # Bottom Right: Cumulative
                fig.add_trace(
                    go.Bar(
                        name=call,
                        x=x_axis_items,
                        y=[0] * len(x_axis_items),
                        marker_color=color,
                        legendgroup=call,
                        offsetgroup=call,
                        showlegend=False,
                        textposition='none'
                    ),
                    row=2, col=2
                )
        
        trace_count_after = len(fig.data)
        expected_traces = 1 + (len(callsigns) * len(run_statuses) * 2)  # racing bar + (calls × statuses × 2 subplots)
        if trace_count_after != expected_traces:
            logging.error(f"ERROR: Trace count mismatch! Expected {expected_traces} but got {trace_count_after}")

        # --- Legend Decoder (Representative Keys) ---
        # Add dummy traces to explain the Color Intensity/Gray logic.
        # We use the first color in the palette (Blue) as the example.
        example_blue = base_palette[0]
        
        decoder_items = [
            ("Mode: Run", self._get_mode_color(example_blue, 'Run')),
            ("Mode: S&P", self._get_mode_color(example_blue, 'S&P')),
            ("Mode: Unknown", self._get_mode_color(example_blue, 'Unknown'))
        ]

        for label, color in decoder_items:
            fig.add_trace(
                go.Bar(
                    x=[None], y=[None],
                    name=label,
                    marker_color=color,
                    showlegend=True,
                ),
                row=1, col=1 # Assign to any subplot, it won't render data
            )

        # 4. Generate Frames with Time Formatting
        frames = []
        time_formats = {}  # Cache formatted times
        
        # Prepare footer text for frame annotations (needed since frame layouts replace all annotations)
        # Define footer_text early so it can be used in frames
        footer_text = get_standard_footer(self.logs)
        footer_annotation = {
            "x": 0.5,
            "y": -0.25,
            "xref": "paper",
            "yref": "paper",
            "text": footer_text.replace('\n', '<br>'),
            "showarrow": False,
            "font": {"size": 12, "color": "#7f7f7f"},
            "align": "center",
            "valign": "top"
        }
        
        for t_idx, t_label in enumerate(time_bins):
            frame_data = []
            
            # Format time for this frame
            full_format, compact_format = self._format_time_display(t_label)
            time_formats[t_label] = (full_format, compact_format)
            
            # Update Pane 1: Racing Bars
            scores = [data['ts_data'][call]['score'][t_idx] for call in callsigns]
            # Plotly expects data in order of traces added
            frame_data.append(go.Bar(x=scores, text=scores))
            
            # Update Pane 2 & 3
            x_axis_items = data['bands'] if dimension == 'band' else data['modes']
            frame_bars_count = 0
            
            # Track trace index for positioning (skip index 0 which is racing bar)
            trace_idx = 1
            
            for i, call in enumerate(callsigns):
                base_color = base_palette[i % len(base_palette)]
                
                for run_status in run_statuses:
                    color = self._get_mode_color(base_color, run_status)
                    
                    # Hourly Data (row=2, col=1)
                    if dimension == 'band':
                        y_hourly = [data['matrix_hourly'][call][band][run_status][t_idx] for band in x_axis_items]
                    else:
                        y_hourly = [data['matrix_hourly'][call][mode][run_status][t_idx] for mode in x_axis_items]
                    
                    # CRITICAL: Explicitly set offsetgroup, legendgroup, and color to match initial traces
                    frame_data.append(go.Bar(
                        x=x_axis_items,
                        y=y_hourly,
                        name=call,
                        offsetgroup=call,  # Group by Call for side-by-side positioning
                        legendgroup=call,
                        marker_color=color,
                        textposition='none'
                    ))
                    trace_idx += 1
                    frame_bars_count += 1
                    
                    # Cumulative Data (row=2, col=2)
                    if dimension == 'band':
                        y_cumul = [data['matrix_cumulative'][call][band][run_status][t_idx] for band in x_axis_items]
                    else:
                        y_cumul = [data['matrix_cumulative'][call][mode][run_status][t_idx] for mode in x_axis_items]
                    
                    # CRITICAL: Explicitly set offsetgroup, legendgroup, and color to match initial traces
                    frame_data.append(go.Bar(
                        x=x_axis_items,
                        y=y_cumul,
                        name=call,
                        offsetgroup=call,  # Group by Call for side-by-side positioning
                        legendgroup=call,
                        marker_color=color,
                        textposition='none'
                    ))
                    trace_idx += 1
                    frame_bars_count += 1

            # Include layout update for annotations in frame
            # Note: Frame layout annotations replace ALL annotations, so we must include both
            frame_layout = {
                "annotations": [
                    {
                        "text": f"<b>Current Time: {full_format}</b>",
                        "x": 0.5,
                        "y": 1.02,
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {"size": 16, "color": "#2c3e50"},
                        "xanchor": "center",
                        "yanchor": "bottom"
                    },
                    footer_annotation.copy()  # Include footer in each frame
                ]
            }
            
            frames.append(go.Frame(data=frame_data, name=t_label, layout=frame_layout))

        fig.frames = frames

        # 5. Configure Axes and Layout
        
        # Top Pane: Fixed Range based on Max Score
        max_score = max([max(data['ts_data'][c]['score']) for c in callsigns]) if callsigns else 10
        fig.update_xaxes(range=[0, max_score * 1.1], row=1, col=1)
        
        # Bottom Left: Max Hourly Rate
        max_hourly = data['max_stats']['hourly_qsos']
        fig.update_yaxes(title_text="QSOs / Hour", range=[0, max_hourly * 1.1], row=2, col=1)
        
        # Bottom Right: Max Cumulative
        max_cumul = data['max_stats']['cumulative_qsos']
        fig.update_yaxes(title_text="Total QSOs", range=[0, max_cumul * 1.1], row=2, col=2)
        
        # Common X-Axis properties
        x_axis_label = dimension_label  # "Band" or "Mode"
        fig.update_xaxes(title_text=x_axis_label, row=2, col=1)
        fig.update_xaxes(title_text=x_axis_label, row=2, col=2)

        # Construct Standard Title
        # Use the same callsigns list that was used for the filename to ensure consistency
        # The aggregator data (data['callsigns']) is the source of truth for which callsigns have data
        modes_present = set()
        for log in self.logs:
            df = get_valid_dataframe(log)
            if 'Mode' in df.columns:
                modes_present.update(df['Mode'].dropna().unique())
        
        # Pass callsigns_override to ensure title matches what's actually displayed (from aggregator)
        title_lines = get_standard_title_lines(self.report_name, self.logs, "All Bands", None, modes_present, callsigns_override=callsigns)
        
        # For animation, we can add help text to the title
        final_title = f"{title_lines[0]}<br><sub>{title_lines[1]}<br>{title_lines[2]}</sub>"

        # Animation Settings
        fig.update_layout(
            template="plotly_white",
            height=900,
            # Initial placeholder title, will be updated below
            title_text=final_title,
            barmode='stack', # Enables stacking within offsetgroups
            margin=dict(t=100, b=180, l=100, r=50), # Bottom margin for footer, top for title
            updatemenus=[{
                "type": "buttons",
                "showactive": False,
                "x": 0.98,
                "y": 1.08,
                "xanchor": "right",
                "yanchor": "bottom",
                "buttons": [{
                    "label": "Play",
                    "method": "animate",
                    "args": [None, {"frame": {"duration": 1000, "redraw": True}, "fromcurrent": True}]
                }, {
                    "label": "Pause",
                    "method": "animate",
                    "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}]
                }]
            }, {
                "type": "dropdown",
                "direction": "down",
                "showactive": True,
                "x": 0.88,
                "y": 1.08,
                "xanchor": "right",
                "yanchor": "bottom",
                "active": 1,
                "buttons": [
                    {"label": "FPS: 0.5", "method": "animate", "args": [None, {"frame": {"duration": 2000, "redraw": True}, "mode": "immediate", "transition": {"duration": 2000}}]},
                    {"label": "FPS: 1",   "method": "animate", "args": [None, {"frame": {"duration": 1000, "redraw": True}, "mode": "immediate", "transition": {"duration": 1000}}]},
                    {"label": "FPS: 2",   "method": "animate", "args": [None, {"frame": {"duration": 500, "redraw": True}, "mode": "immediate", "transition": {"duration": 500}}]},
                    {"label": "FPS: 5",   "method": "animate", "args": [None, {"frame": {"duration": 200, "redraw": True}, "mode": "immediate", "transition": {"duration": 200}}]}
                ]
            }],
            sliders=[{
                "currentvalue": {
                    "prefix": "Time: ",
                    "visible": True,
                    "offset": 20,
                    "font": {"size": 14},
                    "xanchor": "left"
                },
                "steps": [
                    {
                        "args": [[f.name], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
                        "label": time_formats.get(f.name, ("", ""))[1],  # Compact format for slider labels (e.g., "Sep 28, 00:00")
                        "method": "animate"
                    }
                    for f in frames
                ],
                "active": 0
            }]
        )

        # Merge with existing layout properties (since animation has complex layout)
        # We inject footer as annotation manually because we aren't using get_standard_layout here
        # IMPORTANT: Do NOT include the time annotation in base layout - only in frames
        # This prevents overlay issues. Base layout only has static footer.
        fig.update_layout(
            title_text=final_title,
            annotations=[
                {
                    "x": 0.5,
                    "y": -0.25,
                    "xref": "paper",
                    "yref": "paper",
                    "text": footer_text.replace('\n', '<br>'),
                    "showarrow": False,
                    "font": {"size": 12, "color": "#7f7f7f"},
                    "align": "center",
                    "valign": "top"
                }
            ]
        )

        # 6. Save
        callsigns_part = build_callsigns_filename_part(callsigns)
        filename = f"interactive_animation--{callsigns_part}.html"
        full_path = os.path.join(output_path, filename)
        
        # Config for Download Filename
        download_filename = f"contest_progress_{callsigns_part}"
        config = {'toImageButtonOptions': {'filename': download_filename, 'format': 'png'}}
        
        fig.write_html(full_path, auto_play=False, config=config)
        
        if not os.path.exists(full_path):
            logging.error(f"ERROR: Animation file was NOT created: {full_path}")
        
        logging.info(f"Generated interactive animation: {full_path}")

        return f"Interactive animation generated: {filename}"

    def _prepare_data_band(self, **kwargs) -> Dict[str, Any]:
        """
        Aggregates and aligns data for band dimension (band -> RunStatus structure).
        Matrix Structure: logs -> call -> band -> RunStatus -> [list of ints]
        """
        # --- 1. Get Raw Data ---
        # Retrieve authoritative time index from the LogManager of the first log
        # (All logs share the same LogManager instance and time index)
        master_index = None
        if self.logs and hasattr(self.logs[0], '_log_manager_ref'):
            log_manager = self.logs[0]._log_manager_ref
            if log_manager:
                master_index = log_manager.master_time_index

        # --- Phase 1 Performance Optimization: Use Cached Aggregator Data ---
        get_cached_ts_data = kwargs.get('_get_cached_ts_data')
        get_cached_matrix_data = kwargs.get('_get_cached_matrix_data')
        
        if get_cached_ts_data:
            # Use cached time series data (avoids recreating aggregator and recomputing)
            ts_raw = get_cached_ts_data()
        else:
            # Fallback to old behavior for backward compatibility
            ts_agg = TimeSeriesAggregator(self.logs)
            ts_raw = ts_agg.get_time_series_data()
        
        get_cached_stacked_matrix_data = kwargs.get('_get_cached_stacked_matrix_data')
        if get_cached_stacked_matrix_data:
            # Use cached stacked matrix data (avoids recreating aggregator and recomputing)
            matrix_raw = get_cached_stacked_matrix_data(bin_size='60min', mode_filter=None, time_index=master_index)
        else:
            # Fallback to old behavior for backward compatibility
            matrix_agg = MatrixAggregator(self.logs)
            matrix_raw = matrix_agg.get_stacked_matrix_data(bin_size='60min', time_index=master_index)

        # Extract callsigns from actual logs being processed (not cached data)
        # This ensures filename matches the data being generated (fixes single-log overwriting issue)
        callsigns = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in self.logs])
        time_bins = ts_raw['time_bins']
        bands = matrix_raw['bands']

        # --- 2. Process Time Series (Score) ---
        ts_data = {}
        for call in callsigns:
            log_entry = ts_raw['logs'][call]
            # Prefer Score, fallback to Points, then QSOs
            if any(log_entry['cumulative']['score']):
                metric = log_entry['cumulative']['score']
            elif any(log_entry['cumulative']['points']):
                metric = log_entry['cumulative']['points']
            else:
                metric = log_entry['cumulative']['qsos']
            ts_data[call] = {'score': metric}

        # --- 3. Process Matrix Data (Hourly & Cumulative) ---
        # Matrix Structure: logs -> call -> band -> mode -> [list of ints]
        matrix_hourly = {}
        matrix_cumulative = {}
        
        global_max_hourly = 0
        global_max_cumul = 0

        for call in callsigns:
            matrix_hourly[call] = {}
            matrix_cumulative[call] = {}
            
            # Temporary storage to sum per-band for global max calc
            hourly_sums_per_bin = np.zeros(len(time_bins))
            cumul_sums_per_bin = np.zeros(len(time_bins))

            for band in bands:
                matrix_hourly[call][band] = {}
                matrix_cumulative[call][band] = {}
                
                band_hourly_total = np.zeros(len(time_bins))
                band_cumul_total = np.zeros(len(time_bins))

                for mode in ['Run', 'S&P', 'Unknown']:
                    # Get hourly list (ensure alignment/length matching if necessary, 
                    # but aggregators should share master index logic)
                    
                    raw_list = matrix_raw['logs'][call].get(band, {}).get(mode, [0]*len(time_bins))
                    
                    # Convert to numpy for cumsum
                    arr_hourly = np.array(raw_list)
                    arr_cumul = np.cumsum(arr_hourly)
                    
                    matrix_hourly[call][band][mode] = arr_hourly.tolist()
                    matrix_cumulative[call][band][mode] = arr_cumul.tolist()
                    
                    # Update max trackers
                    band_hourly_total += arr_hourly
                    band_cumul_total += arr_cumul

                # Track global maxes (Stacked height per band)
                global_max_hourly = max(global_max_hourly, np.max(band_hourly_total))
                global_max_cumul = max(global_max_cumul, np.max(band_cumul_total))

        return {
            'time_bins': time_bins,
            'callsigns': callsigns,
            'bands': bands,
            'modes': None,  # Not used for band dimension
            'ts_data': ts_data,
            'matrix_hourly': matrix_hourly,
            'matrix_cumulative': matrix_cumulative,
            'max_stats': {
                'hourly_qsos': int(global_max_hourly),
                'cumulative_qsos': int(global_max_cumul)
            }
        }
    
    def _prepare_data_mode(self, **kwargs) -> Dict[str, Any]:
        """
        Aggregates and aligns data for mode dimension (mode -> RunStatus structure).
        Matrix Structure: logs -> call -> mode (radio mode) -> RunStatus -> [list of ints]
        """
        # --- 1. Get Raw Data ---
        # Retrieve authoritative time index from the LogManager of the first log
        master_index = None
        if self.logs and hasattr(self.logs[0], '_log_manager_ref'):
            log_manager = self.logs[0]._log_manager_ref
            if log_manager:
                master_index = log_manager.master_time_index

        # --- Phase 1 Performance Optimization: Use Cached Aggregator Data ---
        get_cached_ts_data = kwargs.get('_get_cached_ts_data')
        
        if get_cached_ts_data:
            ts_raw = get_cached_ts_data()
        else:
            ts_agg = TimeSeriesAggregator(self.logs)
            ts_raw = ts_agg.get_time_series_data()

        # Extract callsigns from actual logs being processed (not cached data)
        # This ensures filename matches the data being generated (fixes single-log overwriting issue)
        callsigns = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in self.logs])

        # --- 2. Process Matrix Data (Mode Dimension) ---
        # Use MatrixAggregator for consistent data structure (like band dimension)
        # CRITICAL: Use master_index to ensure time alignment across all logs
        # The aggregator will reindex all data to this master index
        if master_index is None:
            # Fallback: create from time_bins (but prefer log_manager's master_index)
            time_bins = ts_raw['time_bins']
            master_index = pd.to_datetime(time_bins)
        
        matrix_agg = MatrixAggregator(self.logs)
        matrix_raw = matrix_agg.get_mode_stacked_matrix_data(bin_size='60min', time_index=master_index)
        
        # Use time_bins from aggregator to ensure consistency
        time_bins = matrix_raw['time_bins']
        num_time_bins = len(time_bins)
        
        modes = matrix_raw['modes']
        
        if not modes:
            modes = []

        # --- 3. Process Time Series (Score) ---
        ts_data = {}
        for call in callsigns:
            log_entry = ts_raw['logs'][call]
            if any(log_entry['cumulative']['score']):
                metric = log_entry['cumulative']['score']
            elif any(log_entry['cumulative']['points']):
                metric = log_entry['cumulative']['points']
            else:
                metric = log_entry['cumulative']['qsos']
            ts_data[call] = {'score': metric}

        # Convert aggregator structure to our internal format: call -> mode -> RunStatus -> [values]
        # Aggregator returns: logs[call][mode][run_status] = [values]
        # We need: matrix_hourly[call][mode][run_status] = [values] (same structure!)
        matrix_hourly = {}
        matrix_cumulative = {}
        
        global_max_hourly = 0
        global_max_cumul = 0

        for call in callsigns:
            matrix_hourly[call] = {}
            matrix_cumulative[call] = {}
            
            # Check if callsign exists in aggregator output
            if call not in matrix_raw['logs']:
                logging.warning(f"WARNING: callsign {call} NOT in aggregator output!")
                # Initialize empty structure for missing callsign
                for mode in modes:
                    matrix_hourly[call][mode] = {
                        'Run': [0] * num_time_bins,
                        'S&P': [0] * num_time_bins,
                        'Unknown': [0] * num_time_bins
                    }
                    matrix_cumulative[call][mode] = {
                        'Run': [0] * num_time_bins,
                        'S&P': [0] * num_time_bins,
                        'Unknown': [0] * num_time_bins
                    }
                continue
            
            for mode in modes:
                # Get data from aggregator (already in correct format)
                mode_data = matrix_raw['logs'][call].get(mode, {
                    'Run': [0] * num_time_bins,
                    'S&P': [0] * num_time_bins,
                    'Unknown': [0] * num_time_bins
                })
                
                # Hourly data (from aggregator)
                mode_hourly = {
                    'Run': list(mode_data.get('Run', [0] * num_time_bins)),
                    'S&P': list(mode_data.get('S&P', [0] * num_time_bins)),
                    'Unknown': list(mode_data.get('Unknown', [0] * num_time_bins))
                }
                
                # Calculate cumulative
                mode_cumulative = {}
                for rs in ['Run', 'S&P', 'Unknown']:
                    cumulative = 0
                    cumul_list = []
                    for val in mode_hourly[rs]:
                        cumulative += val
                        cumul_list.append(cumulative)
                    mode_cumulative[rs] = cumul_list
                
                matrix_hourly[call][mode] = mode_hourly
                matrix_cumulative[call][mode] = mode_cumulative
                
                # Update global max
                mode_total_hourly = [sum(mode_hourly[rs][t] for rs in ['Run', 'S&P', 'Unknown']) for t in range(num_time_bins)]
                mode_total_cumul = [sum(mode_cumulative[rs][t] for rs in ['Run', 'S&P', 'Unknown']) for t in range(num_time_bins)]
                if mode_total_hourly:
                    global_max_hourly = max(global_max_hourly, max(mode_total_hourly))
                if mode_total_cumul:
                    global_max_cumul = max(global_max_cumul, max(mode_total_cumul))
        
        return {
            'time_bins': time_bins,
            'callsigns': callsigns,
            'bands': None,  # Not used for mode dimension
            'modes': modes,
            'ts_data': ts_data,
            'matrix_hourly': matrix_hourly,
            'matrix_cumulative': matrix_cumulative,
            'max_stats': {
                'hourly_qsos': int(global_max_hourly),
                'cumulative_qsos': int(global_max_cumul)
            }
        }