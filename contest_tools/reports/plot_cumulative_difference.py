# contest_tools/reports/plot_cumulative_difference.py
#
# Purpose: A plot report that generates a cumulative difference graph,
#          comparing two logs.
#
# Author: Gemini AI
# Date: 2025-12-14
# Version: 0.113.0-Beta
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
# [0.113.0-Beta] - 2025-12-13
# - Standardized filename generation: removed '_vs_' separator to match Web Dashboard conventions.
# [1.1.2] - 2025-12-14
# - Updated file generation to use `_sanitize_filename_part` for strict lowercase naming.
# [1.1.1] - 2025-12-10
# - Fixed visualization bug: Increased top margin to prevent Main Title/Subplot Title overlap.
# [1.1.0] - 2025-12-10
# - Migrated visualization engine to Plotly (Dual Output: PNG + HTML).
# - Implemented PlotlyStyleManager for standardized styling.
# [1.0.0] - 2025-11-24
# - Refactored to use Data Abstraction Layer (TimeSeriesAggregator).
# - Enabled Run/S&P plots for Points metric via 'run_points' schema.
# [0.90.0-Beta] - 2025-10-01
# - Set new baseline version for release.

from typing import List
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import logging

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import create_output_directory, get_valid_dataframe, save_debug_data, _sanitize_filename_part
from ..data_aggregators.time_series import TimeSeriesAggregator
from ..styles.plotly_style_manager import PlotlyStyleManager

class Report(ContestReport):
    """
    Generates a three-subplot plot showing the cumulative difference in
    QSOs or Points between two logs.
    """
    report_id: str = "cumulative_difference_plots"
    report_name: str = "Cumulative Difference Plots"
    report_type: str = "plot"
    supports_pairwise = True
    
    def _generate_single_plot(self, output_path: str, band_filter: str, mode_filter: str, **kwargs):
        """
        Helper function to generate a single cumulative difference plot.
        Returns a list of generated file paths (PNG and HTML).
        """
        debug_data_flag = kwargs.get("debug_data", False)
        metric = kwargs.get('metric', 'qsos')
        log1, log2 = self.logs[0], self.logs[1]
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')
        
        # --- DAL Integration (v1.3.1) ---
        agg = TimeSeriesAggregator([log1, log2])
        ts_data = agg.get_time_series_data(band_filter=band_filter, mode_filter=mode_filter)
        time_bins = [pd.Timestamp(t) for t in ts_data['time_bins']]

        # Helper to extract series
        def get_series(call_key, field):
            vals = ts_data['logs'][call_key]['cumulative'][field]
            return pd.Series(vals, index=time_bins)

        if metric == 'points':
            metric_name = log1.contest_definition.points_header_label or "Points"
            
            run1 = get_series(call1, 'run_points')
            sp1 = get_series(call1, 'sp_unk_points')
            run2 = get_series(call2, 'run_points')
            sp2 = get_series(call2, 'sp_unk_points')
            
            run_diff = run1 - run2
            sp_unk_diff = sp1 - sp2
            overall_diff = (run1 + sp1) - (run2 + sp2)

            debug_df = pd.DataFrame({
                f'run_pts_{call1}': run1, f'sp_pts_{call1}': sp1,
                f'run_pts_{call2}': run2, f'sp_pts_{call2}': sp2,
                'run_diff': run_diff, 'sp_unk_diff': sp_unk_diff, 'overall_diff': overall_diff
            })
            
        else: # metric == 'qsos'
            metric_name = "QSOs"
            
            run1 = get_series(call1, 'run_qsos')
            sp1 = get_series(call1, 'sp_unk_qsos')
            run2 = get_series(call2, 'run_qsos')
            sp2 = get_series(call2, 'sp_unk_qsos')
            
            run_diff = run1 - run2
            sp_unk_diff = sp1 - sp2
            overall_diff = (run1 + sp1) - (run2 + sp2)
            
            debug_df = pd.DataFrame({
                f'run_qso_{call1}': run1, f'sp_qso_{call1}': sp1,
                f'run_qso_{call2}': run2, f'sp_qso_{call2}': sp2,
                'run_diff': run_diff, 'sp_unk_diff': sp_unk_diff, 'overall_diff': overall_diff
            })
        
        # --- Plotting Preparation ---
        if overall_diff.abs().sum() == 0 and run_diff.abs().sum() == 0 and sp_unk_diff.abs().sum() == 0:
            logging.info(f"Skipping {band_filter} difference plot: no data available for this band.")
            return []

        # Get Standard Colors
        mode_colors = PlotlyStyleManager.get_qso_mode_colors()
        
        # Create Subplots
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            subplot_titles=(f"Overall Diff ({metric_name})", "Run Diff", "S&P+Unk Diff")
        )

        # --- Row 1: Overall Difference (Black) ---
        fig.add_trace(
            go.Scatter(
                x=overall_diff.index, y=overall_diff,
                mode='lines+markers',
                name='Overall',
                line=dict(color='black', width=2),
                marker=dict(size=4)
            ),
            row=1, col=1
        )

        # --- Row 2: Run Difference (Green) ---
        fig.add_trace(
            go.Scatter(
                x=run_diff.index, y=run_diff,
                mode='lines+markers',
                name='Run',
                line=dict(color=mode_colors['Run'], width=2),
                marker=dict(size=4)
            ),
            row=2, col=1
        )

        # --- Row 3: S&P Difference (Blue) ---
        fig.add_trace(
            go.Scatter(
                x=sp_unk_diff.index, y=sp_unk_diff,
                mode='lines+markers',
                name='S&P',
                line=dict(color=mode_colors['S&P'], width=2),
                marker=dict(size=4)
            ),
            row=3, col=1
        )

        # --- Zero Reference Lines ---
        for i in range(1, 4):
            fig.add_hline(y=0, line_width=1, line_color="black", row=i, col=1)

        # --- Metadata & Titles ---
        metadata = log1.get_metadata()
        year = get_valid_dataframe(log1)['Date'].dropna().iloc[0].split('-')[0] if not get_valid_dataframe(log1).empty else "----"
        contest_name = metadata.get('ContestName', '')
        event_id = metadata.get('EventID', '')
        
        is_single_band = len(log1.contest_definition.valid_bands) == 1
        band_text = log1.contest_definition.valid_bands[0].replace('M', ' Meters') if is_single_band else band_filter.replace('M', ' Meters')
        mode_text = f" ({mode_filter})" if mode_filter else ""
        callsign_str = f"{call1} vs. {call2}"

        title_line1 = f"{self.report_name} - {metric_name}{mode_text}"
        title_line2 = f"{year} {event_id} {contest_name} - {callsign_str}".strip().replace("  ", " ")
        final_title = f"{title_line1}<br>{title_line2}" # Use <br> for Plotly title break

        # --- Layout Standardization ---
        layout = PlotlyStyleManager.get_standard_layout(final_title)
        fig.update_layout(layout)
        fig.update_layout(
            height=900, 
            width=1600,
            showlegend=False, # Legend redundant given subplot titles
            margin=dict(t=140) # FIX: Increase top margin to prevent title overlap
        )
        # Update Axis Labels
        fig.update_yaxes(title_text="Diff", row=1, col=1)
        fig.update_yaxes(title_text="Diff", row=2, col=1)
        fig.update_yaxes(title_text="Diff", row=3, col=1)
        fig.update_xaxes(title_text="Contest Time", row=3, col=1)

        # --- Saving Files (Dual Output) ---
        filename_band = log1.contest_definition.valid_bands[0].lower() if is_single_band else band_filter.lower().replace('m', '')
        mode_suffix = f"_{mode_filter.lower()}" if mode_filter else ""
        
        # Debug Data
        c1_safe = _sanitize_filename_part(call1)
        c2_safe = _sanitize_filename_part(call2)
        debug_filename = f"{self.report_id}_{metric}{mode_suffix}_{filename_band}_{c1_safe}_{c2_safe}.txt"
        save_debug_data(debug_data_flag, output_path, debug_df, custom_filename=debug_filename)
        
        create_output_directory(output_path)
        
        base_filename = f"{self.report_id}_{metric}{mode_suffix}_{filename_band}_{c1_safe}_{c2_safe}"
        html_filename = f"{base_filename}.html"
        png_filename = f"{base_filename}.png"
        
        html_path = os.path.join(output_path, html_filename)
        png_path = os.path.join(output_path, png_filename)
        
        generated_files = []
        
        # Save HTML
        try:
            fig.write_html(html_path, include_plotlyjs='cdn')
            generated_files.append(html_path)
        except Exception as e:
            logging.error(f"Failed to save HTML report: {e}")

        # Save PNG (Requires Kaleido)
        try:
            fig.write_image(png_path, width=1600, height=900)
            generated_files.append(png_path)
        except Exception as e:
            logging.warning(f"Failed to generate static PNG (Kaleido missing?): {e}")

        return generated_files

    def _orchestrate_plot_generation(self, dfs: List[pd.DataFrame], output_path: str, mode_filter: str, **kwargs):
        """Helper to generate the full set of plots for a given data slice."""
        if any(df.empty for df in dfs):
            return []

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
                
                new_files = self._generate_single_plot(
                    output_path=save_path,
                    band_filter=band,
                    mode_filter=mode_filter,
                    **kwargs
                )
                if new_files:
                    created_files.extend(new_files)
            except Exception as e:
                print(f"  - Failed to generate difference plot for {band} (Mode: {mode_filter or 'All'}): {e}")
        
        return created_files

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Orchestrates the generation of all cumulative difference plots, including per-mode breakdowns.
        """
        if len(self.logs) != 2:
            return "Error: The Cumulative Difference Plot report requires exactly two logs."

        log1, log2 = self.logs[0], self.logs[1]
        df1_full = get_valid_dataframe(log1)
        df2_full = get_valid_dataframe(log2)

        if df1_full.empty or df2_full.empty:
            return "Skipping report: At least one log has no valid QSO data."

        all_created_files = []

        # 1. Generate plots for "All Modes"
        all_created_files.extend(
            self._orchestrate_plot_generation(dfs=[df1_full, df2_full], output_path=output_path, mode_filter=None, **kwargs)
        )

        # 2. Generate plots for each mode if applicable
        modes_present = pd.concat([df1_full['Mode'], df2_full['Mode']]).dropna().unique()
        if len(modes_present) > 1:
            for mode in ['CW', 'PH', 'DG']:
                if mode in modes_present:
                    sliced_dfs = [df[df['Mode'] == mode] for df in [df1_full, df2_full]]
                    
                    all_created_files.extend(
                        self._orchestrate_plot_generation(sliced_dfs, output_path, mode_filter=mode, **kwargs)
                    )
        
        if not all_created_files:
            return f"No difference plots were generated for metric '{kwargs.get('metric', 'qsos')}'."

        return f"Cumulative difference plots for {kwargs.get('metric', 'qsos')} saved to relevant subdirectories."