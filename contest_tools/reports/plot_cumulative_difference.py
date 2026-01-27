# contest_tools/reports/plot_cumulative_difference.py
#
# Purpose: A plot report that generates a cumulative difference graph,
#          comparing two logs, with superimposed lines for Total, Run, S&P, and Unknown.
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

from typing import List
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import logging

from ..contest_log import ContestLog
from .report_interface import ContestReport
from contest_tools.utils.report_utils import create_output_directory, get_valid_dataframe, save_debug_data, _sanitize_filename_part, get_standard_footer, get_standard_title_lines, build_filename
from ..data_aggregators.time_series import TimeSeriesAggregator
from ..styles.plotly_style_manager import PlotlyStyleManager

class Report(ContestReport):
    """
    Generates a single plot showing the cumulative difference in QSOs or Points
    between two logs, with superimposed lines for Total, Run, S&P, and Unknown.
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
        
        # --- Phase 1 Performance Optimization: Use Cached Aggregator Data ---
        get_cached_ts_data = kwargs.get('_get_cached_ts_data')
        if get_cached_ts_data:
            # Use cached time series data (avoids recreating aggregator and recomputing)
            ts_data = get_cached_ts_data(band_filter=band_filter, mode_filter=mode_filter)
        else:
            # Fallback to old behavior for backward compatibility
            agg = TimeSeriesAggregator([log1, log2])
            ts_data = agg.get_time_series_data(band_filter=band_filter, mode_filter=mode_filter)
        
        time_bins = [pd.Timestamp(t) for t in ts_data['time_bins']]

        # Helper to extract series
        def get_series(call_key, field):
            vals = ts_data['logs'][call_key]['cumulative'][field]
            return pd.Series(vals, index=time_bins)
        
        # Helper to extract hourly series
        def get_hourly_series(call_key, field):
            vals = ts_data['logs'][call_key]['hourly'][field]
            return pd.Series(vals, index=time_bins)

        if metric == 'points':
            metric_name = log1.contest_definition.points_header_label or "Points"
            
            run1 = get_series(call1, 'run_points')
            sp1 = get_series(call1, 'sp_points')
            unk1 = get_series(call1, 'unknown_points')
            run2 = get_series(call2, 'run_points')
            sp2 = get_series(call2, 'sp_points')
            unk2 = get_series(call2, 'unknown_points')
            
            run_diff = run1 - run2
            sp_diff = sp1 - sp2
            unk_diff = unk1 - unk2
            overall_diff = (run1 + sp1 + unk1) - (run2 + sp2 + unk2)

            debug_df = pd.DataFrame({
                f'run_{call1}': run1, f'sp_{call1}': sp1, f'unk_{call1}': unk1,
                f'run_{call2}': run2, f'sp_{call2}': sp2, f'unk_{call2}': unk2,
                'run_diff': run_diff, 'sp_diff': sp_diff, 'unk_diff': unk_diff,
                'overall_diff': overall_diff
            })
            
        else: # metric == 'qsos'
            metric_name = "QSOs"
            
            run1 = get_series(call1, 'run_qsos')
            sp1 = get_series(call1, 'sp_qsos')
            unk1 = get_series(call1, 'unknown_qsos')
            run2 = get_series(call2, 'run_qsos')
            sp2 = get_series(call2, 'sp_qsos')
            unk2 = get_series(call2, 'unknown_qsos')
            
            run_diff = run1 - run2
            sp_diff = sp1 - sp2
            unk_diff = unk1 - unk2
            overall_diff = (run1 + sp1 + unk1) - (run2 + sp2 + unk2)
            
            debug_df = pd.DataFrame({
                f'run_{call1}': run1, f'sp_{call1}': sp1, f'unk_{call1}': unk1,
                f'run_{call2}': run2, f'sp_{call2}': sp2, f'unk_{call2}': unk2,
                'run_diff': run_diff, 'sp_diff': sp_diff, 'unk_diff': unk_diff,
                'overall_diff': overall_diff
            })
        
        # --- Plotting Preparation ---
        if overall_diff.abs().sum() == 0:
            logging.info(f"Skipping {band_filter} difference plot: no data available for this band.")
            return []

        # Get Standard Colors
        mode_colors = PlotlyStyleManager.get_qso_mode_colors()
        
        # Get hourly data for differences
        if metric == 'points':
            run1_hourly = get_hourly_series(call1, 'run_points')
            sp1_hourly = get_hourly_series(call1, 'sp_points')
            unk1_hourly = get_hourly_series(call1, 'unknown_points')
            run2_hourly = get_hourly_series(call2, 'run_points')
            sp2_hourly = get_hourly_series(call2, 'sp_points')
            unk2_hourly = get_hourly_series(call2, 'unknown_points')
        else:  # metric == 'qsos'
            run1_hourly = get_hourly_series(call1, 'run_qsos')
            sp1_hourly = get_hourly_series(call1, 'sp_qsos')
            unk1_hourly = get_hourly_series(call1, 'unknown_qsos')
            run2_hourly = get_hourly_series(call2, 'run_qsos')
            sp2_hourly = get_hourly_series(call2, 'sp_qsos')
            unk2_hourly = get_hourly_series(call2, 'unknown_qsos')
        
        # Calculate hourly differences
        run_diff_hourly = run1_hourly - run2_hourly
        sp_diff_hourly = sp1_hourly - sp2_hourly
        unk_diff_hourly = unk1_hourly - unk2_hourly
        
        # Helper function to round axis range
        def round_axis_range(min_val, max_val):
            """Round axis range based on magnitude."""
            range_val = max_val - min_val
            if range_val < 500:
                round_to = 25
            elif range_val < 5000:
                round_to = 100
            else:
                round_to = 1000
            
            min_rounded = (min_val // round_to) * round_to
            max_rounded = ((max_val // round_to) + 1) * round_to
            return min_rounded, max_rounded
        
        # Calculate axis ranges using compromise ratio approach
        # Step 1: Get natural data ranges
        cumul_data_min = overall_diff.min()
        cumul_data_max = overall_diff.max()
        
        # Calculate hourly bar ranges (considering all stacked segments)
        hourly_values = []
        for i in range(len(time_bins)):
            run_val = run_diff_hourly.iloc[i]
            sp_val = sp_diff_hourly.iloc[i]
            unk_val = unk_diff_hourly.iloc[i]
            
            # Calculate stacked positions
            neg_sum = 0
            pos_sum = 0
            if run_val < 0:
                neg_sum += run_val
            elif run_val > 0:
                pos_sum += run_val
            if sp_val < 0:
                neg_sum += sp_val
            elif sp_val > 0:
                pos_sum += sp_val
            if unk_val < 0:
                neg_sum += unk_val
            elif unk_val > 0:
                pos_sum += unk_val
            
            hourly_values.append(neg_sum)
            hourly_values.append(pos_sum)
        
        if hourly_values:
            hourly_data_min = min(hourly_values)
            hourly_data_max = max(hourly_values)
        else:
            hourly_data_min, hourly_data_max = -50, 50
        
        # Step 2: Calculate natural ratios (P/|N|)
        # Handle edge cases where one side might be zero
        cumul_neg = abs(cumul_data_min) if cumul_data_min < 0 else 1
        cumul_pos = cumul_data_max if cumul_data_max > 0 else 1
        cumul_ratio = cumul_pos / cumul_neg if cumul_neg > 0 else float('inf')
        
        hourly_neg = abs(hourly_data_min) if hourly_data_min < 0 else 1
        hourly_pos = hourly_data_max if hourly_data_max > 0 else 1
        hourly_ratio = hourly_pos / hourly_neg if hourly_neg > 0 else float('inf')
        
        # Step 3: Choose compromise ratio
        # Favor the ratio closer to 1:1 (more balanced) to ensure smaller dataset visibility
        if cumul_ratio == float('inf') or hourly_ratio == float('inf'):
            # If one ratio is infinite (all positive or all negative), use the other
            target_ratio = cumul_ratio if hourly_ratio == float('inf') else hourly_ratio
        else:
            # Use the ratio closer to 1:1 (more balanced) as it favors smaller dataset visibility
            # This ensures hourly bars get reasonable vertical space
            if abs(cumul_ratio - 1.0) < abs(hourly_ratio - 1.0):
                target_ratio = cumul_ratio
            else:
                target_ratio = hourly_ratio
        
        # Step 4: Adjust both axes to match target ratio while including all data
        # For cumulative axis
        if cumul_data_min < 0 and cumul_data_max > 0:
            # Adjust to match target ratio
            # Keep the larger of the two sides, adjust the other to match ratio
            cumul_neg_extent = abs(cumul_data_min)
            cumul_pos_extent = cumul_data_max
            
            # Calculate what each side would be with target ratio
            if cumul_neg_extent >= cumul_pos_extent / target_ratio:
                # Negative side is larger, keep it, adjust positive
                cumul_neg_adj = cumul_neg_extent
                cumul_pos_adj = cumul_neg_adj * target_ratio
                # Ensure we include all positive data
                cumul_pos_adj = max(cumul_pos_adj, cumul_pos_extent)
            else:
                # Positive side is larger, keep it, adjust negative
                cumul_pos_adj = cumul_pos_extent
                cumul_neg_adj = cumul_pos_adj / target_ratio
                # Ensure we include all negative data
                cumul_neg_adj = max(cumul_neg_adj, cumul_neg_extent)
            
            cumul_min = -cumul_neg_adj
            cumul_max = cumul_pos_adj
        else:
            # All positive or all negative - use natural range
            cumul_min, cumul_max = cumul_data_min, cumul_data_max
        
        # For hourly axis
        if hourly_data_min < 0 and hourly_data_max > 0:
            # Adjust to match target ratio
            hourly_neg_extent = abs(hourly_data_min)
            hourly_pos_extent = hourly_data_max
            
            # Calculate what each side would be with target ratio
            if hourly_neg_extent >= hourly_pos_extent / target_ratio:
                # Negative side is larger, keep it, adjust positive
                hourly_neg_adj = hourly_neg_extent
                hourly_pos_adj = hourly_neg_adj * target_ratio
                # Ensure we include all positive data
                hourly_pos_adj = max(hourly_pos_adj, hourly_pos_extent)
            else:
                # Positive side is larger, keep it, adjust negative
                hourly_pos_adj = hourly_pos_extent
                hourly_neg_adj = hourly_pos_adj / target_ratio
                # Ensure we include all negative data
                hourly_neg_adj = max(hourly_neg_adj, hourly_neg_extent)
            
            hourly_min = -hourly_neg_adj
            hourly_max = hourly_pos_adj
        else:
            # All positive or all negative - use natural range
            hourly_min, hourly_max = hourly_data_min, hourly_data_max
        
        # Step 5: Round both ranges
        cumul_min, cumul_max = round_axis_range(cumul_min, cumul_max)
        hourly_min, hourly_max = round_axis_range(hourly_min, hourly_max)
        
        # Step 6: Re-adjust after rounding to maintain ratio match
        # Recalculate ratio from one rounded range and apply to the other
        if cumul_min < 0 and cumul_max > 0 and hourly_min < 0 and hourly_max > 0:
            # Use cumulative's rounded ratio as the final target
            final_ratio = cumul_max / abs(cumul_min)
            
            # Adjust hourly to match this ratio
            hourly_neg_final = abs(hourly_min)
            hourly_pos_final = hourly_neg_final * final_ratio
            # Ensure we include all hourly data
            hourly_pos_final = max(hourly_pos_final, hourly_data_max)
            hourly_min = -hourly_neg_final
            hourly_max = hourly_pos_final
            
            # Round again
            hourly_min, hourly_max = round_axis_range(hourly_min, hourly_max)
        
        # Create subplots with secondary Y-axis and table
        # Move table down by increasing vertical spacing and adjusting row heights
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=False,
            vertical_spacing=0.20,  # Increased to push table down toward footer
            row_heights=[0.75, 0.25],  # Reasonable split: 75% plot, 25% table
            specs=[[{"type": "xy", "secondary_y": True}], [{"type": "table"}]]
        )
        
        # --- Trace 1: Overall Difference Line (Black) ---
        fig.add_trace(
            go.Scatter(
                x=overall_diff.index, y=overall_diff.tolist(),
                mode='lines+markers',
                name='Overall',
                line=dict(color='black', width=3),
                marker=dict(size=3)
            ),
            row=1, col=1
        )
        
        # --- Hourly Difference Bars (Stacked) ---
        # Calculate stacked bar positions for each hour
        # Order: Run (closest to axis), S&P (middle), Unknown (furthest)
        # Negative side: stack downward, positive side: stack upward
        
        run_pos_values = []
        run_neg_values = []
        run_pos_bases = []
        run_neg_bases = []
        
        sp_pos_values = []
        sp_neg_values = []
        sp_pos_bases = []
        sp_neg_bases = []
        
        unk_pos_values = []
        unk_neg_values = []
        unk_pos_bases = []
        unk_neg_bases = []
        
        for i in range(len(time_bins)):
            run_val = run_diff_hourly.iloc[i]
            sp_val = sp_diff_hourly.iloc[i]
            unk_val = unk_diff_hourly.iloc[i]
            
            # Separate positive and negative values, maintaining order: Run, S&P, Unknown
            neg_run = run_val if run_val < 0 else 0
            neg_sp = sp_val if sp_val < 0 else 0
            neg_unk = unk_val if unk_val < 0 else 0
            
            pos_run = run_val if run_val > 0 else 0
            pos_sp = sp_val if sp_val > 0 else 0
            pos_unk = unk_val if unk_val > 0 else 0
            
            # Stack negative values (downward from 0)
            # Order from axis outward: Run (closest to 0), S&P (middle), Unknown (furthest)
            # Calculate bases: Run starts closest to 0, S&P stacks below Run, Unknown stacks below S&P
            # Total negative sum for positioning
            total_neg = neg_run + neg_sp + neg_unk
            
            # Run is closest to 0, so starts at neg_run (e.g., -5)
            neg_base_run = neg_run
            # S&P starts where Run ends (neg_run + neg_sp, e.g., -8)
            neg_base_sp = neg_run + neg_sp
            # Unknown starts where S&P ends (total_neg, e.g., -10 if unk=-2)
            neg_base_unk = total_neg
            
            run_neg_values.append(abs(neg_run) if neg_run < 0 else 0)
            run_neg_bases.append(neg_base_run)
            
            sp_neg_values.append(abs(neg_sp) if neg_sp < 0 else 0)
            sp_neg_bases.append(neg_base_sp)
            
            unk_neg_values.append(abs(neg_unk) if neg_unk < 0 else 0)
            unk_neg_bases.append(neg_base_unk)
            
            # Stack positive values (upward from 0)
            # Order from axis outward: Run (closest), S&P (middle), Unknown (furthest)
            pos_base_run = 0
            pos_base_sp = pos_run  # S&P starts where Run ends
            pos_base_unk = pos_run + pos_sp  # Unknown starts where S&P ends
            
            run_pos_values.append(pos_run if pos_run > 0 else 0)
            run_pos_bases.append(pos_base_run)
            
            sp_pos_values.append(pos_sp if pos_sp > 0 else 0)
            sp_pos_bases.append(pos_base_sp)
            
            unk_pos_values.append(pos_unk if pos_unk > 0 else 0)
            unk_pos_bases.append(pos_base_unk)
        
        # Add bar traces (negative values - use negative bases directly)
        # Use offsetgroup to ensure all bars align at the same x position
        bar_offset_group = "hourly_bars"
        
        fig.add_trace(
            go.Bar(
                x=time_bins,
                y=run_neg_values,
                base=run_neg_bases,  # Base is already negative (e.g., -5 for Run)
                name='Run',
                marker=dict(color=mode_colors['Run'], opacity=0.7),
                width=3600000 * 0.8,
                offsetgroup=bar_offset_group,
                showlegend=False
            ),
            row=1, col=1,
            secondary_y=True
        )
        
        fig.add_trace(
            go.Bar(
                x=time_bins,
                y=sp_neg_values,
                base=sp_neg_bases,  # Base is already negative (e.g., -8 for S&P when Run=-5, S&P=-3)
                name='S&P',
                marker=dict(color=mode_colors['S&P'], opacity=0.7),
                width=3600000 * 0.8,
                offsetgroup=bar_offset_group,
                showlegend=False
            ),
            row=1, col=1,
            secondary_y=True
        )
        
        fig.add_trace(
            go.Bar(
                x=time_bins,
                y=unk_neg_values,
                base=unk_neg_bases,  # Base is already negative
                name='Unknown',
                marker=dict(color=mode_colors['Mixed/Unk'], opacity=0.7),
                width=3600000 * 0.8,
                offsetgroup=bar_offset_group,
                showlegend=False
            ),
            row=1, col=1,
            secondary_y=True
        )
        
        fig.add_trace(
            go.Bar(
                x=time_bins,
                y=run_pos_values,
                base=run_pos_bases,
                name='Run',
                marker=dict(color=mode_colors['Run'], opacity=0.7),
                width=3600000 * 0.8,
                offsetgroup=bar_offset_group,
                legendgroup='Run',
                showlegend=True
            ),
            row=1, col=1,
            secondary_y=True
        )
        
        fig.add_trace(
            go.Bar(
                x=time_bins,
                y=sp_pos_values,
                base=sp_pos_bases,
                name='S&P',
                marker=dict(color=mode_colors['S&P'], opacity=0.7),
                width=3600000 * 0.8,
                offsetgroup=bar_offset_group,
                legendgroup='S&P',
                showlegend=True
            ),
            row=1, col=1,
            secondary_y=True
        )
        
        fig.add_trace(
            go.Bar(
                x=time_bins,
                y=unk_pos_values,
                base=unk_pos_bases,
                name='Unknown',
                marker=dict(color=mode_colors['Mixed/Unk'], opacity=0.7),
                width=3600000 * 0.8,
                offsetgroup=bar_offset_group,
                legendgroup='Unknown',
                showlegend=True
            ),
            row=1, col=1,
            secondary_y=True
        )
        
        # --- Zero Reference Line ---
        # Add zero line using hline - this will align with the primary Y-axis
        # Since both axes share the same plot area and zero should align, this single line serves both
        fig.add_hline(
            y=0,
            line_width=2,
            line_color="gray",
            line_dash="dash",
            row=1,
            col=1
        )
        
        # --- Table Data ---
        # Get final cumulative values for table (actual totals, not differences)
        if metric == 'points':
            total1 = (run1 + sp1 + unk1).iloc[-1]
            total2 = (run2 + sp2 + unk2).iloc[-1]
            run1_final = run1.iloc[-1]
            sp1_final = sp1.iloc[-1]
            unk1_final = unk1.iloc[-1]
            run2_final = run2.iloc[-1]
            sp2_final = sp2.iloc[-1]
            unk2_final = unk2.iloc[-1]
        else:
            total1 = (run1 + sp1 + unk1).iloc[-1]
            total2 = (run2 + sp2 + unk2).iloc[-1]
            run1_final = run1.iloc[-1]
            sp1_final = sp1.iloc[-1]
            unk1_final = unk1.iloc[-1]
            run2_final = run2.iloc[-1]
            sp2_final = sp2.iloc[-1]
            unk2_final = unk2.iloc[-1]
        
        table_headers = ['Call', f'Total {metric_name}', 'Run', 'S&P', 'Unknown']
        table_values = [
            [call1, call2],
            [f"{total1:,}", f"{total2:,}"],
            [f"{run1_final:,}", f"{run2_final:,}"],
            [f"{sp1_final:,}", f"{sp2_final:,}"],
            [f"{unk1_final:,}", f"{unk2_final:,}"]
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(
                    values=table_headers,
                    fill_color="#f0f0f0",
                    line_color="darkgray",
                    align='center',
                    font=dict(size=12, weight='bold')
                ),
                cells=dict(
                    values=table_values,
                    fill_color='white',
                    line_color="lightgray",
                    align='center',
                    font=dict(size=11),
                    height=30
                )
            ),
            row=2, col=1
        )

        # --- Metadata & Titles ---
        # Smart Scoping: Collect unique modes from all logs
        modes_present = set()
        for log in self.logs:
            df = get_valid_dataframe(log)
            if 'Mode' in df.columns:
                modes_present.update(df['Mode'].dropna().unique())
        
        title_lines = get_standard_title_lines(f"{self.report_name} ({metric_name})", self.logs, band_filter, mode_filter, modes_present)

        footer_text = get_standard_footer(self.logs)

        # --- Layout Standardization ---
        # Pass list directly to Manager for Annotation Stack generation
        layout = PlotlyStyleManager.get_standard_layout(title_lines, footer_text)
        
        fig.update_layout(layout)
        
        # Configure axes with compromise ratio ranges
        # Both axes now have matching P/|N| ratios, ensuring zero alignment
        fig.update_layout(
            width=1200,
            height=900,
            xaxis_title="Contest Time",
            yaxis_title=f"Cumulative Diff ({metric_name})",
            yaxis=dict(range=[cumul_min, cumul_max]),
            # Configure secondary Y-axis with matching ratio for zero alignment
            yaxis2=dict(
                title=f"Hourly {metric_name} Difference",
                range=[hourly_min, hourly_max],
                overlaying='y',
                side='right',
                anchor='x'  # Anchor to same x-axis
            ),
            # Set barmode to overlay to ensure all bars align at same x positions
            barmode='overlay',
            legend=dict(x=0.01, y=0.99)
        )

        # --- Saving Files (Dual Output) ---
        base_filename = build_filename(f"{self.report_id}_{metric}", self.logs, band_filter, mode_filter)
        
        # Debug Data
        debug_filename = f"{base_filename}.txt"
        save_debug_data(debug_data_flag, output_path, debug_df, custom_filename=debug_filename)
        
        create_output_directory(output_path)
        
        html_filename = f"{base_filename}.html"
        png_filename = f"{base_filename}.png"
        json_filename = f"{base_filename}.json"
        
        html_path = os.path.join(output_path, html_filename)
        png_path = os.path.join(output_path, png_filename)
        
        generated_files = []
        
        # Save HTML
        try:
            # Fixed Height with responsive width (Hard Deck Strategy)
            fig.update_layout(
                autosize=True,
                height=800
            )
            
            config = {'toImageButtonOptions': {'filename': base_filename, 'format': 'png'}}
            fig.write_html(html_path, include_plotlyjs='cdn', config=config)
            generated_files.append(html_path)
        
        except Exception as e:
            logging.error(f"Failed to save HTML report: {e}")

        # Save JSON (Web Component)
        json_path = os.path.join(output_path, json_filename)
        try:
            fig.write_json(json_path)
            generated_files.append(json_path)
        except Exception as e:
            logging.error(f"Failed to save JSON data: {e}")

        # Save PNG (Requires Kaleido)
        # Disabled for Web Architecture
        # try:
        #     # Fixed Layout for PNG
        #     fig.update_layout(
        #         autosize=False,
        #         width=1600,
        #         height=900
        #     )
        #     fig.write_image(png_path, width=1600, height=900)
        #     generated_files.append(png_path)
        # except Exception as e:
        #     logging.warning(f"Failed to generate static PNG (Kaleido missing?): {e}")

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
            # Include all standard modes: CW, PH (SSB), DG (Digital), RY (RTTY)
            for mode in ['CW', 'PH', 'DG', 'RY']:
                if mode in modes_present:
                    sliced_dfs = [df[df['Mode'] == mode] for df in [df1_full, df2_full]]
                    
                    all_created_files.extend(
                        self._orchestrate_plot_generation(sliced_dfs, output_path, mode_filter=mode, **kwargs)
                    )
        
        if not all_created_files:
            return f"No difference plots were generated for metric '{kwargs.get('metric', 'qsos')}'."

        return f"Cumulative difference plots for {kwargs.get('metric', 'qsos')} saved to relevant subdirectories."