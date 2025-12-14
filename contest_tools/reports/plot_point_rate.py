# contest_tools/reports/plot_point_rate.py
#
# Purpose: A plot report that generates a point rate graph for all bands
#          and for each individual band.
#
# Author: Gemini AI
# Date: 2025-12-14
# Version: 0.113.3-Beta
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
# [0.113.3-Beta] - 2025-12-14
# - Fixed HTML layout issue by explicitly setting autosize=True and clearing
#   fixed dimensions before saving the HTML file.
# [0.113.0-Beta] - 2025-12-13
# - Standardized filename generation: removed '_vs_' separator and applied strict sanitization to callsigns.
# [1.1.0] - 2025-12-10
# - Migrated visualization engine from Matplotlib to Plotly.
# - Implemented dual output (PNG + HTML).
# - Replaced embedded text table with Plotly Data Table.
# - Integrated PlotlyStyleManager for consistent styling.
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
from ._report_utils import create_output_directory, get_valid_dataframe, save_debug_data, _sanitize_filename_part
from ..data_aggregators.time_series import TimeSeriesAggregator
from ..styles.plotly_style_manager import PlotlyStyleManager

class Report(ContestReport):
    """
    Generates a series of plots comparing cumulative points: one for all bands
    combined, and one for each individual contest band.
    """
    report_id: str = "point_rate_plots"
    report_name: str = "Point Rate Comparison Plots"
    report_type: str = "plot"
    supports_multi = True
    
    def generate(self, output_path: str, **kwargs) -> str:
        """
        Orchestrates the generation of all point rate plots, including per-mode breakdowns.
        """
        all_created_files = []
        
        # Prepare full dataframes once
        full_dfs = [get_valid_dataframe(log) for log in self.logs]
        if any(df.empty for df in full_dfs):
            return "Skipping report: At least one log has no valid QSO data."

        # 1. Generate plots for "All Modes"
        all_created_files.extend(
            self._orchestrate_plot_generation(full_dfs, output_path, mode_filter=None, **kwargs)
        )

        # 2. Generate plots for each mode if applicable
        modes_present = pd.concat([df['Mode'] for df in full_dfs]).dropna().unique()
        if len(modes_present) > 1:
            for mode in ['CW', 'PH', 'DG']:
                if mode in modes_present:
                    sliced_dfs = [df[df['Mode'] == mode] for df in full_dfs]
                    all_created_files.extend(
                        self._orchestrate_plot_generation(sliced_dfs, output_path, mode_filter=mode, **kwargs)
                    )
        
        if not all_created_files:
            return "No point rate plots were generated."
        return "Point rate plots saved to:\n" + "\n".join([f"  - {fp}" for fp in all_created_files])

    def _orchestrate_plot_generation(self, dfs: List[pd.DataFrame], output_path: str, mode_filter: str, **kwargs) -> List[str]:
        """Helper to generate the full set of plots for a given data slice."""
        bands = self.logs[0].contest_definition.valid_bands
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
                    output_path=save_path,
                    band_filter=band,
                    mode_filter=mode_filter,
                    **kwargs
                )
                if filepath:
                    created_files.append(filepath)
            except Exception as e:
                print(f"  - Failed to generate point rate plot for {band}: {e}")
                logging.error(f"Point rate plot generation failed for {band}: {e}", exc_info=True)
        
        return created_files

    def _create_plot(self, dfs: List[pd.DataFrame], output_path: str, band_filter: str, mode_filter: str, **kwargs) -> str:
        debug_data_flag = kwargs.get("debug_data", False)
        bands = self.logs[0].contest_definition.valid_bands
        
        # --- DAL Integration ---
        agg = TimeSeriesAggregator(self.logs)
        ts_data = agg.get_time_series_data(band_filter=band_filter, mode_filter=mode_filter)
        time_bins = [pd.Timestamp(t) for t in ts_data['time_bins']]

        # Initialize Plotly Figure with Subplots (Graph + Table)
        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.7, 0.3],
            vertical_spacing=0.1,
            specs=[[{"type": "xy"}], [{"type": "table"}]]
        )

        all_calls = []
        summary_rows = []
        all_series = [] # For debug data
        
        metric_name = self.logs[0].contest_definition.points_header_label or "Points"

        # --- Trace 1: Line Graph ---
        for i, log in enumerate(self.logs):
            call = log.get_metadata().get('MyCall', 'Unknown')
            all_calls.append(call)
            
            log_data = ts_data['logs'].get(call)
            if not log_data:
                continue

            cumulative_values = log_data['cumulative']['points']
            scalars = log_data['scalars']

            if scalars['net_qsos'] == 0:
                continue
            
            # Use Style Manager for consistent colors
            color = PlotlyStyleManager._COLOR_PALETTE[i % len(PlotlyStyleManager._COLOR_PALETTE)]

            # Add Line Trace
            fig.add_trace(
                go.Scatter(
                    x=time_bins,
                    y=cumulative_values,
                    mode='lines+markers',
                    name=call,
                    line=dict(color=color),
                    marker=dict(size=6)
                ),
                row=1, col=1
            )
            
            # Store for debug
            series = pd.Series(cumulative_values, index=time_bins, name=call)
            all_series.append(series)

            # Extract Table Data directly from Aggregator (as per Plan)
            # Run QSOs: Last value of cumulative['run_qsos']
            run_val = log_data['cumulative']['run_qsos'][-1] if log_data['cumulative']['run_qsos'] else 0
            # S&P QSOs: Last value of cumulative['sp_unk_qsos']
            sp_val = log_data['cumulative']['sp_unk_qsos'][-1] if log_data['cumulative']['sp_unk_qsos'] else 0
            
            summary_rows.append([
                call,
                f"{scalars.get('points_sum', 0):,}",
                f"{run_val:,}",
                f"{sp_val:,}"
            ])

        # Check if we have data
        if not summary_rows:
            logging.info(f"Skipping {metric_name} plot for {band_filter}: No data available.")
            return None

        # --- Trace 2: Summary Table ---
        # Plotly Table expects columns, not rows. Transpose logic.
        headers = ['Call', f'Total {metric_name}', 'Run QSOs', 'S&P/Unk QSOs']
        
        # Transpose rows to columns
        if summary_rows:
            table_cells = list(map(list, zip(*summary_rows)))
        else:
            table_cells = [[], [], [], []]

        fig.add_trace(
            go.Table(
                header=dict(
                    values=headers,
                    font=dict(size=12, weight='bold'),
                    align="center",
                    fill_color="#f0f0f0",
                    line_color="darkgray"
                ),
                cells=dict(
                    values=table_cells,
                    align="center",
                    font=dict(size=11),
                    height=25,
                    fill_color="white",
                    line_color="lightgray"
                )
            ),
            row=2, col=1
        )

        # --- Layout & Styling ---
        metadata = self.logs[0].get_metadata()
        year = get_valid_dataframe(self.logs[0])['Date'].dropna().iloc[0].split('-')[0] if not get_valid_dataframe(self.logs[0]).empty else "----"
        contest_name = metadata.get('ContestName', '')
        event_id = metadata.get('EventID', '')
        
        is_single_band = len(self.logs[0].contest_definition.valid_bands) == 1
        band_text = self.logs[0].contest_definition.valid_bands[0].replace('M', ' Meters') if is_single_band else band_filter.replace('M', ' Meters')
        mode_text = f" ({mode_filter})" if mode_filter else ""
        callsign_str = ", ".join(all_calls)

        title_line1 = f"{self.report_name}{mode_text}"
        title_line2 = f"{year} {event_id} {contest_name} - {callsign_str}".strip().replace("  ", " ")
        final_title = f"{title_line1}<br>{title_line2}" # Use <br> for Plotly title

        # Apply standard layout
        layout_config = PlotlyStyleManager.get_standard_layout(final_title)
        fig.update_layout(layout_config)
        
        # Additional specific layout overrides
        fig.update_layout(
            width=1200,
            height=900,
            xaxis_title="Contest Time",
            yaxis_title=f"Cumulative {metric_name}",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        create_output_directory(output_path)
        
        filename_band = self.logs[0].contest_definition.valid_bands[0].lower() if is_single_band else band_filter.lower().replace('m', '')
        filename_calls = '_'.join([_sanitize_filename_part(c) for c in sorted(all_calls)])
        mode_suffix = f"_{mode_filter.lower()}" if mode_filter else ""
        
        # --- Save Debug Data ---
        if all_series:
            debug_df = pd.concat(all_series, axis=1).fillna(0).copy()
            # Add multiplier info to debug if available (legacy logic preserved)
            for i, log in enumerate(self.logs):
                call = all_calls[i]
                if hasattr(log, 'time_series_score_df') and log.time_series_score_df is not None:
                    score_ts = log.time_series_score_df
                    if 'total_mults' in score_ts.columns:
                        debug_df[f'mults_{call}'] = score_ts['total_mults']
                    for band in bands:
                        band_col = f'total_mults_{band}'
                        if band_col in score_ts.columns:
                            debug_df[f'mults_{band}_{call}'] = score_ts[band_col]
            
            debug_filename = f"{self.report_id}_{filename_band}{mode_suffix}_{filename_calls}.txt"
            save_debug_data(debug_data_flag, output_path, debug_df, custom_filename=debug_filename)

        # --- Output Generation ---
        base_filename = f"{self.report_id}_{filename_band}{mode_suffix}_{filename_calls}"
        
        # Save HTML (Interactive)
        html_path = os.path.join(output_path, f"{base_filename}.html")
        # FORCE RESPONSIVE FOR HTML
        fig.update_layout(
            autosize=True,
            width=None,
            height=None
        )
        fig.write_html(html_path, include_plotlyjs='cdn')
        
        # Save PNG (Static)
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
            logging.warning(f"Could not generate PNG for point rate plot (likely missing kaleido): {e}")
            # If PNG fails, return HTML path to ensure caller receives a valid file
            return html_path

        return png_path