# contest_tools/reports/base_rate_report.py
#
# Purpose: Abstract base class for rate-based plot reports (QSO Rate, Point Rate).
#          Consolidates visualization logic, layout fixes, and JSON artifact generation.
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
from typing import List, Optional
import os
import pandas as pd
import logging
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..contest_log import ContestLog
from .report_interface import ContestReport
from contest_tools.utils.report_utils import create_output_directory, get_valid_dataframe, save_debug_data, get_standard_footer, get_standard_title_lines, build_filename
from ..data_aggregators.time_series import TimeSeriesAggregator
from ..styles.plotly_style_manager import PlotlyStyleManager

class BaseRateReport(ContestReport):
    """
    Base class for generating rate comparison plots.
    Supports both single-log and multi-log scenarios.
    Subclasses must define metric_key and metric_label.
    """
    report_type: str = "plot"
    supports_multi = True
    supports_single = True
    
    # Defaults to be overridden
    metric_key: str = "qsos"
    metric_label: str = "QSOs"

    def _get_metric_name(self) -> str:
        """Hook for dynamic metric naming (e.g. from contest def)."""
        return self.metric_label

    def generate(self, output_path: str, **kwargs) -> str:
        all_created_files = []

        # Filter for valid logs only
        valid_logs = []
        valid_dfs = []
    
        for log in self.logs:
            df = get_valid_dataframe(log)
            if not df.empty:
                valid_logs.append(log)
                valid_dfs.append(df)
        
        if not valid_logs:
            return f"Skipping {self.report_name}: No logs have valid QSO data."

        # 1. Generate plots for "All Modes"
        all_created_files.extend(
            self._orchestrate_plot_generation(valid_dfs, valid_logs, output_path, mode_filter=None, **kwargs)
        )

        # 2. Generate plots for each mode if applicable (use JSON-defined valid_modes)
        modes_present = pd.concat([df['Mode'] for df in valid_dfs]).dropna().unique()
        valid_modes = valid_logs[0].contest_definition.valid_modes if valid_logs else []
        
        if valid_modes and len(valid_modes) > 1:
            # Use JSON-defined modes instead of hardcoded list
            for mode in valid_modes:
                if mode in modes_present:
                    sliced_dfs = [df[df['Mode'] == mode] for df in valid_dfs]
                    all_created_files.extend(
                        self._orchestrate_plot_generation(sliced_dfs, valid_logs, output_path, mode_filter=mode, **kwargs)
                    )
        elif len(modes_present) > 1:
            # Fallback: If valid_modes not defined but multiple modes present, use modes_present
            logging.warning(
                f"valid_modes not defined in JSON for {valid_logs[0].contest_definition.contest_name}. "
                f"Using modes found in data: {sorted(modes_present)}. Consider adding 'valid_modes' to contest definition."
            )
            for mode in sorted(modes_present):
                sliced_dfs = [df[df['Mode'] == mode] for df in valid_dfs]
                all_created_files.extend(
                    self._orchestrate_plot_generation(sliced_dfs, valid_logs, output_path, mode_filter=mode, **kwargs)
                )
        
        if not all_created_files:
            return f"No {self.metric_label} rate plots were generated."
        return f"{self.metric_label} rate plots saved to:\n" + "\n".join([f"  - {fp}" for fp in all_created_files])

    def _orchestrate_plot_generation(self, dfs: List[pd.DataFrame], logs: List[ContestLog], output_path: str, mode_filter: str, **kwargs) -> List[str]:
        bands = logs[0].contest_definition.valid_bands
        is_single_band = len(bands) == 1
        bands_to_plot = ['All'] if is_single_band else ['All'] + bands
        
        created_files = []
        
        for band in bands_to_plot:
            try:
                save_path = output_path
                if not is_single_band and band != 'All':
                    if mode_filter:
                        save_path = os.path.join(output_path, mode_filter.lower(), band)
                    else:
                        save_path = os.path.join(output_path, band)

                filepath = self._create_plot(
                    dfs=dfs,
                    logs=logs,
                    output_path=save_path,
                    band_filter=band,
                    mode_filter=mode_filter,
                    **kwargs
                )
                if filepath:
                    created_files.append(filepath)
            except Exception as e:
                logging.error(f"Failed to generate {self.metric_label} rate plot for {band}: {e}", exc_info=True)
        
        return created_files

    def _create_plot(self, dfs: List[pd.DataFrame], logs: List[ContestLog], output_path: str, band_filter: str, mode_filter: str, **kwargs) -> str:
        debug_data_flag = kwargs.get("debug_data", False)
        metric_name = self._get_metric_name()
        
        # --- Phase 1 Performance Optimization: Use Cached Aggregator Data ---
        get_cached_ts_data = kwargs.get('_get_cached_ts_data')
        if get_cached_ts_data:
            # Use cached time series data (avoids recreating aggregator and recomputing)
            ts_data = get_cached_ts_data(band_filter=band_filter if band_filter != 'All' else None, mode_filter=mode_filter)
        else:
            # Fallback to old behavior for backward compatibility
            agg = TimeSeriesAggregator(logs)
            ts_data = agg.get_time_series_data(band_filter=band_filter if band_filter != 'All' else None, mode_filter=mode_filter)
        time_bins = [pd.Timestamp(t) for t in ts_data['time_bins']]

        # Detect single-log case for dual-axis plot
        is_single_log = len(logs) == 1

        # Initialize Plotly Subplots
        # Fix: Increased vertical_spacing to 0.15 to prevent overlap
        # For single-log: enable secondary_y in specs for row 1 to support dual-axis
        if is_single_log:
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=False,
                vertical_spacing=0.15,
                row_heights=[0.7, 0.3],
                specs=[[{"type": "xy", "secondary_y": True}], [{"type": "table"}]]
            )
        else:
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=False,
                vertical_spacing=0.15,
                row_heights=[0.7, 0.3],
                specs=[[{"type": "xy"}], [{"type": "table"}]]
            )

        all_calls = []
        summary_rows = []
        all_series = []

        for i, log in enumerate(logs):
            call = log.get_metadata().get('MyCall', 'Unknown')
            all_calls.append(call)
            
            log_data = ts_data['logs'].get(call)
            if not log_data:
                continue
            
            # Dynamic Metric Lookup
            if self.metric_key not in log_data['cumulative']:
                 logging.warning(f"Metric key '{self.metric_key}' not found in cumulative data for {call}.")
                 continue

            cumulative_values = log_data['cumulative'][self.metric_key]
            scalars = log_data['scalars']
            
            if scalars['net_qsos'] == 0:
                continue
            
            color = PlotlyStyleManager._COLOR_PALETTE[i % len(PlotlyStyleManager._COLOR_PALETTE)]

            # 1. Add Line Trace (Cumulative)
            fig.add_trace(
                go.Scatter(
                    x=time_bins,
                    y=cumulative_values,
                    mode='lines+markers',
                    name=call,
                    line=dict(color=color, width=2),
                    marker=dict(size=4)
                ),
                row=1, col=1
            )
            
            # For single-log case, add hourly rate bar chart on secondary Y-axis
            if is_single_log:
                # Get hourly rate data
                hourly_key = self.metric_key  # 'qsos' or 'points'
                if hourly_key not in log_data['hourly']:
                    logging.warning(f"Hourly key '{hourly_key}' not found in hourly data for {call}.")
                else:
                    hourly_values = log_data['hourly'][hourly_key]
                    # Use second color from palette for bars
                    bar_color = PlotlyStyleManager._COLOR_PALETTE[1 % len(PlotlyStyleManager._COLOR_PALETTE)]
                    
                    # Add bar trace - will configure secondary axis using update_yaxes
                    fig.add_trace(
                        go.Bar(
                            x=time_bins,
                            y=hourly_values,
                            name=f"{metric_name} per Hour",
                            marker=dict(color=bar_color, opacity=0.7),
                            width=3600000 * 0.8,  # 80% of hour width for spacing between bars
                        ),
                        row=1, col=1,
                        secondary_y=True
                    )
            
            series = pd.Series(cumulative_values, index=time_bins, name=call)
            all_series.append(series)
            
            # 2. Prepare Table Data
            # Constraint: Run/S&P always display QSOs
            run_qsos_final = log_data['cumulative']['run_qsos'][-1] if log_data['cumulative']['run_qsos'] else 0
            sp_qsos_final = log_data['cumulative']['sp_unk_qsos'][-1] if log_data['cumulative']['sp_unk_qsos'] else 0
            
            # Col 1 is the Metric Total (e.g. Total Points or Total QSOs)
            total_val = 0
            if self.metric_key == 'qsos':
                total_val = scalars.get('net_qsos', 0)
            elif self.metric_key == 'points':
                total_val = scalars.get('points_sum', 0)
            else:
                 # Fallback/Generic
                 total_val = cumulative_values[-1] if cumulative_values else 0

            summary_rows.append([
                call,
                f"{total_val:,}",
                f"{run_qsos_final:,}",
                f"{sp_qsos_final:,}"
            ])

        if not summary_rows:
            return None

        # 3. Add Summary Table
        headers = ['Call', f'Total {metric_name}', 'Run QSOs', 'S&P/Unk QSOs']
        table_columns = list(map(list, zip(*summary_rows))) if summary_rows else [[], [], [], []]
        
        fig.add_trace(
            go.Table(
                header=dict(
                    values=headers,
                    fill_color="#f0f0f0",
                    line_color="darkgray",
                    align='center',
                    font=dict(size=12, weight='bold')
                ),
                cells=dict(
                    values=table_columns,
                    fill_color='white',
                    line_color="lightgray",
                    align='center',
                    font=dict(size=11),
                    height=30
                )
            ),
            row=2, col=1
        )

        # 4. Styling & Layout
        modes_present = set()
        for df in dfs:
            if 'Mode' in df.columns:
                modes_present.update(df['Mode'].dropna().unique())
        
        title_lines = get_standard_title_lines(self.report_name, logs, band_filter, mode_filter, modes_present)
        final_title = f"{title_lines[0]}<br><sub>{title_lines[1]}<br>{title_lines[2]}</sub>"
        footer_text = get_standard_footer(logs)

        layout_cfg = PlotlyStyleManager.get_standard_layout(final_title, footer_text)
        fig.update_layout(**layout_cfg)
        
        # Configure axes based on single-log vs multi-log
        if is_single_log:
            # Dual-axis configuration for single-log case
            fig.update_layout(
                width=1200,
                height=900,
                xaxis_title="Contest Time",
                yaxis_title=f"Cumulative {metric_name}",
                legend=dict(x=0.01, y=0.99)
            )
            # Configure secondary Y-axis using update_yaxes (Option 3)
            fig.update_yaxes(
                title_text=f"{metric_name} per Hour",
                secondary_y=True,
                row=1,
                col=1
            )
        else:
            # Standard single-axis configuration for multi-log case
            fig.update_layout(
                width=1200,
                height=900,
                xaxis_title="Contest Time",
                yaxis_title=f"Cumulative {metric_name}",
                legend=dict(x=0.01, y=0.99)
            )

        create_output_directory(output_path)
        base_filename = build_filename(self.report_id, logs, band_filter, mode_filter)
        
        # --- Save Debug Data ---
        if all_series:
            debug_df = pd.concat(all_series, axis=1).fillna(0)
            save_debug_data(debug_data_flag, output_path, debug_df, custom_filename=f"{base_filename}.txt")
        
        # --- Save Outputs ---
        
        # 1. JSON (New Artifact)
        json_path = os.path.join(output_path, f"{base_filename}.json")
        try:
             # Ensure responsive layout in JSON for Web App
             fig.update_layout(autosize=True, width=None, height=None)
             fig.write_json(json_path)
             # Revert for PNG (Disabled for Web Architecture)
             # fig.update_layout(autosize=False, width=1200, height=900)
        except Exception as e:
             logging.warning(f"JSON artifact generation failed: {e}")

        # 2. HTML (Interactive)
        html_path = os.path.join(output_path, f"{base_filename}.html")
        fig.update_layout(autosize=True, width=None, height=None)
        config = {'toImageButtonOptions': {'filename': base_filename, 'format': 'png'}}
        fig.write_html(html_path, include_plotlyjs='cdn', config=config)
        
        # PNG Generation (Kaleido) disabled for Web Architecture
        # fig.write_image(png_file)
        
        return html_path