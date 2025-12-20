# contest_tools/reports/plot_qso_rate.py
#
# Purpose: A plot report that generates a QSO rate graph for all bands
#          and for each individual band.
#
# Author: Gemini AI
# Date: 2025-12-20
# Version: 0.133.0-Beta
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
# [0.133.0-Beta] - 2025-12-20
# - Refactored `_create_plot` to use centralized `build_filename` utility.
# - Resolved NameError crash caused by missing `is_single_band` variable.
# [0.132.0-Beta] - 2025-12-20
# - Refactored `generate` to filter for valid logs only, preventing crashes on partial data.
# - Updated helper methods (`_orchestrate_plot_generation`, `_create_plot`) to accept explicit log lists.
# [0.131.0-Beta] - 2025-12-20
# - Refactored to use `get_standard_title_lines` for standardized 3-line headers.
# - Implemented explicit "Smart Scoping" for title generation.
# [0.130.2-Beta] - 2025-12-20
# - Implemented "Smart Scoping": "(All Modes)" label is now suppressed if the
#   underlying data contains only a single mode.
# [0.130.1-Beta] - 2025-12-20
# - Refined scope labeling logic to explicitly display "All Bands" and "(All Modes)"
#   instead of relying on implicit defaults.
# [0.130.0-Beta] - 2025-12-20
# - Implemented 3-Line Title standard (Name / Context / Scope).
# - Added footer metadata via `get_cty_metadata`.
# [0.118.0-Beta] - 2025-12-15
# - Injected descriptive filename configuration for interactive HTML plot downloads.
# [0.117.0-Beta] - 2025-12-15
# - Updated table styling to match Point Rate Plot (gray grid theme).
# [0.113.3-Beta] - 2025-12-14
# - Fixed HTML layout issue by explicitly setting autosize=True and clearing
#   fixed dimensions before saving the HTML file.
# [0.113.0-Beta] - 2025-12-13
# - Standardized filename generation: removed '_vs_' separator and applied strict sanitization to callsigns.
# [1.1.0] - 2025-12-07
# - Migrated visualization engine from Matplotlib to Plotly.
# - Implemented dual output (PNG/HTML).
# - Replaced manual table stats with TimeSeriesAggregator cumulative data.
# [1.0.0] - 2025-11-24
# - Refactored to use Data Abstraction Layer (TimeSeriesAggregator).
# [0.90.0-Beta] - 2025-10-01
# Set new baseline version for release.
from typing import List
import os
import pandas as pd
import logging
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import create_output_directory, get_valid_dataframe, save_debug_data, _sanitize_filename_part, get_cty_metadata, get_standard_title_lines, build_filename
from ..data_aggregators.time_series import TimeSeriesAggregator
from ..styles.plotly_style_manager import PlotlyStyleManager

class Report(ContestReport):
    """
    Generates a series of plots comparing QSO rate: one for all bands
    combined, and for each individual contest band.
    """
    report_id: str = "qso_rate_plots"
    report_name: str = "QSO Rate Comparison Plots"
    report_type: str = "plot"
    supports_multi = True
    
    def generate(self, output_path: str, **kwargs) -> str:
        """
        Orchestrates the generation of all QSO rate plots, including per-mode breakdowns.
        """
        all_created_files = []

        # Filter for valid logs only (Partial Failure Resilience)
        valid_logs = []
        valid_dfs = []
        for log in self.logs:
            df = get_valid_dataframe(log)
            if not df.empty:
                valid_logs.append(log)
                valid_dfs.append(df)
        
        if not valid_logs:
            return "Skipping report: No logs have valid QSO data."
        
        # 1. Generate plots for "All Modes"
        all_created_files.extend(
            self._orchestrate_plot_generation(valid_dfs, valid_logs, output_path, mode_filter=None, **kwargs)
        )

        # 2. Generate plots for each mode if applicable
        modes_present = pd.concat([df['Mode'] for df in valid_dfs]).dropna().unique()
        if len(modes_present) > 1:
            for mode in ['CW', 'PH', 'DG']:
                if mode in modes_present:
                    sliced_dfs = [df[df['Mode'] == mode] for df in valid_dfs]
                    all_created_files.extend(
                        self._orchestrate_plot_generation(sliced_dfs, valid_logs, output_path, mode_filter=mode, **kwargs)
                    )
        
        if not all_created_files:
            return "No QSO rate plots were generated."
        
        return "QSO rate plots saved to:\n" + "\n".join([f"  - {fp}" for fp in all_created_files])

    def _orchestrate_plot_generation(self, dfs: List[pd.DataFrame], logs: List[ContestLog], output_path: str, mode_filter: str, **kwargs) -> List[str]:
        """Helper to generate the full set of plots for a given data slice."""
        bands = logs[0].contest_definition.valid_bands
        is_single_band = len(bands) == 1
        bands_to_plot = ['All'] if is_single_band else ['All'] + bands
        
        created_files = []
        
        for band in bands_to_plot:
            try:
                save_path = output_path
                if not is_single_band and band != 'All':
                    # For per-mode plots, create a subdirectory for the mode
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
                print(f"  - Failed to generate QSO rate plot for {band}: {e}")
        
        return created_files

    def _create_plot(self, dfs: List[pd.DataFrame], logs: List[ContestLog], output_path: str, band_filter: str, mode_filter: str, **kwargs) -> str:
        debug_data_flag = kwargs.get("debug_data", False)
        metric_name = "QSOs"
        
        # --- DAL Integration ---
        # Initialize Aggregator with all logs
        agg = TimeSeriesAggregator(logs)
        # Fetch Data with filters
        ts_data = agg.get_time_series_data(band_filter=band_filter, mode_filter=mode_filter)
        
        time_bins = [pd.Timestamp(t) for t in ts_data['time_bins']]

        # Initialize Plotly Subplots
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=False,
            vertical_spacing=0.1,
            row_heights=[0.7, 0.3],
            specs=[[{"type": "xy"}], [{"type": "table"}]]
        )

        all_calls = []
        summary_rows = []
        all_series = [] # For debug export

        for i, log in enumerate(logs):
            call = log.get_metadata().get('MyCall', 'Unknown')
            all_calls.append(call)
            
            # Get log-specific data from DAL structure
            log_data = ts_data['logs'].get(call)
            if not log_data:
                continue
            
            cumulative_values = log_data['cumulative']['qsos']
            scalars = log_data['scalars']
            
            # Check if we have data to plot
            if scalars['net_qsos'] == 0:
                continue
            
            # Color Management
            color = PlotlyStyleManager._COLOR_PALETTE[i % len(PlotlyStyleManager._COLOR_PALETTE)]

            # 1. Add Line Trace
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
            
            # Store for debug
            series = pd.Series(cumulative_values, index=time_bins, name=call)
            all_series.append(series)
            
            # 2. Prepare Table Data (from DAL accumulators)
            # Safe retrieval of last values for cumulative breakdown
            run_qsos_final = log_data['cumulative']['run_qsos'][-1] if log_data['cumulative']['run_qsos'] else 0
            sp_qsos_final = log_data['cumulative']['sp_unk_qsos'][-1] if log_data['cumulative']['sp_unk_qsos'] else 0
            
            summary_rows.append([
                call,
                f"{scalars['net_qsos']:,}",
                f"{run_qsos_final:,}",
                f"{sp_qsos_final:,}"
            ])

        # If no data plotted, return None
        if not summary_rows:
            logging.info(f"Skipping {metric_name} plot for {band_filter}: No data available.")
            return None

        # 3. Add Summary Table
        headers = ['Call', 'Total QSOs', 'Run QSOs', 'S&P/Unk QSOs']
        # Transpose rows for Plotly Table (it expects Column-major lists)
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
        # Smart Scoping: Collect unique modes from all dfs
        modes_present = set()
        for df in dfs:
            if 'Mode' in df.columns:
                modes_present.update(df['Mode'].dropna().unique())
        
        title_lines = get_standard_title_lines(self.report_name, logs, band_filter, mode_filter, modes_present)
        final_title = f"{title_lines[0]}<br><sub>{title_lines[1]}<br>{title_lines[2]}</sub>"

        footer_text = f"Contest Log Analytics by KD4D\n{get_cty_metadata(logs)}"

        # Apply Standard Layout
        layout_cfg = PlotlyStyleManager.get_standard_layout(final_title, footer_text)
        fig.update_layout(**layout_cfg)
        
        # Additional specific layout overrides
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
        # 1. HTML (Interactive)
        html_path = os.path.join(output_path, f"{base_filename}.html")
        # FORCE RESPONSIVE FOR HTML
        fig.update_layout(
            autosize=True,
            width=None,
            height=None
        )
        
        config = {'toImageButtonOptions': {'filename': base_filename, 'format': 'png'}}
        fig.write_html(html_path, include_plotlyjs='cdn', config=config)
        
        # 2. PNG (Static) - Return this path for consistency with report list
        png_path = os.path.join(output_path, f"{base_filename}.png")
        try:
            # FORCE FIXED SIZE FOR PNG
            fig.update_layout(
                autosize=False,
                width=1200,
                height=900
            )
            fig.write_image(png_path)
            return png_path
        except Exception as e:
            logging.warning(f"Static image generation failed (Kaleido missing?): {e}")
            return html_path # Fallback to HTML if PNG fails

        return png_path