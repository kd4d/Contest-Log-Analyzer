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
import math
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

        def tick_vals_for_range(min_val, max_val, step):
            """Generate tick values at step spacing; include 0 if in range."""
            low = int((min_val // step) * step)
            high = int(((max_val // step) + 1) * step)
            ticks = list(range(low, high + 1, step))
            if min_val <= 0 <= max_val and 0 not in ticks:
                ticks.append(0)
                ticks.sort()
            return ticks
        
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

        logging.info(
            "Cumulative difference: min=%s, max=%s; Hourly difference: min=%s, max=%s",
            cumul_data_min, cumul_data_max, hourly_data_min, hourly_data_max,
        )

        # Dual-axis scaling (see Docs/CumulativeDifferencePlotScaling.md):
        # 1. Establish cumulative axis first (data-derived, N grid lines).
        # 2. Bar axis: snap bar zero to closest grid line to ideal P/N; expand range so rounding holds exactly.

        cumul_neg = abs(cumul_data_min) if cumul_data_min < 0 else 1
        cumul_pos = cumul_data_max if cumul_data_max > 0 else 1
        cumul_ratio = cumul_pos / cumul_neg if cumul_neg > 0 else float('inf')
        if cumul_data_min < 0 and cumul_data_max > 0:
            target_ratio = cumul_ratio
        elif hourly_data_min < 0 and hourly_data_max > 0:
            hourly_neg = abs(hourly_data_min) if hourly_data_min < 0 else 1
            hourly_pos = hourly_data_max if hourly_data_max > 0 else 1
            target_ratio = hourly_pos / hourly_neg if hourly_neg > 0 else float('inf')
        else:
            hourly_neg = abs(hourly_data_min) if hourly_data_min < 0 else 1
            hourly_pos = hourly_data_max if hourly_data_max > 0 else 1
            target_ratio = cumul_ratio if cumul_ratio != float('inf') else (hourly_pos / hourly_neg if hourly_neg > 0 else float('inf'))

        cumul_data_min_f = float(cumul_data_min)
        cumul_data_max_f = float(cumul_data_max)
        if cumul_data_min < 0 and cumul_data_max > 0:
            M_cumul = max(abs(cumul_data_min_f), cumul_data_max_f / target_ratio)
            cumul_min_raw = -M_cumul
            cumul_max_raw = M_cumul * target_ratio
        else:
            cumul_min_raw = cumul_data_min_f
            cumul_max_raw = cumul_data_max_f
        cumul_range_raw = cumul_max_raw - cumul_min_raw
        # At most 15 horizontal grid lines: step >= range/14; choose smallest "nice" step >= that
        N_MAX = 15
        min_step_for_cap = cumul_range_raw / max(N_MAX - 1, 1)
        nice_steps = [25, 50, 100, 250, 500, 1000, 2000, 5000]
        step_cumul = next((s for s in nice_steps if s >= min_step_for_cap), None)
        if step_cumul is None:
            step_cumul = max(1000, math.ceil(min_step_for_cap / 1000) * 1000)
        cumul_min = math.floor(cumul_min_raw / step_cumul) * step_cumul
        cumul_max_exact = abs(cumul_min) * target_ratio
        cumul_max = math.ceil(max(cumul_max_exact, cumul_data_max_f) / step_cumul) * step_cumul
        cumul_tickvals = list(range(int(cumul_min), int(cumul_max) + 1, step_cumul))
        N = max(len(cumul_tickvals), 2)

        # Bar axis: ideal P/N position -> snap to closest grid line k; expand range for exact ratio + rounding
        hourly_data_min_f = float(hourly_data_min)
        hourly_data_max_f = float(hourly_data_max)
        if hourly_data_min < 0 and hourly_data_max > 0:
            # Ideal bar zero position (0-1 from bottom): |neg|/(|neg|+pos)
            ideal_pos = abs(hourly_data_min_f) / (abs(hourly_data_min_f) + hourly_data_max_f)
            k = round(ideal_pos * (N - 1))
            k = max(0, min(k, N - 1))
        else:
            k = 0 if hourly_data_max > 0 else N - 1

        if k == 0:
            # Bar zero at bottom grid line: bar_min = 0
            bar_max_min = max(hourly_data_max_f, 0)
            step_bar_max = 5
            hourly_max = step_bar_max * math.ceil(bar_max_min / step_bar_max)
            hourly_min = 0
        elif k == N - 1:
            # Bar zero at top grid line: bar_max = 0
            bar_min_max = min(hourly_data_min_f, 0)
            step_bar_min = 5
            hourly_min = step_bar_min * math.floor(bar_min_max / step_bar_min)
            hourly_max = 0
        else:
            # Bar zero at grid line k: ratio bar_max/|bar_min| = (N-1-k)/k; expand range so both endpoints are multiples of 5
            g = math.gcd(k, N - 1 - k)
            step_bar_max = 5 * (N - 1 - k) // g
            if step_bar_max < 5:
                step_bar_max = 5
            bar_max_min = max(hourly_data_max_f, abs(hourly_data_min_f) * (N - 1 - k) / k)
            hourly_max = step_bar_max * math.ceil(bar_max_min / step_bar_max)
            hourly_min = -k * hourly_max / (N - 1 - k)  # exact ratio; hourly_min is multiple of 5 when g|k

        step_bar_actual = (hourly_max - hourly_min) / (N - 1) if N > 1 else 0
        hourly_tickvals = [hourly_min + i * step_bar_actual for i in range(N)]
        hourly_ticktext = [str(int(round(v / 5) * 5)) for v in hourly_tickvals]

        # Slight range padding so top and bottom grid lines are visible inside the plot area
        cumul_span = max(cumul_max - cumul_min, 1)
        hourly_span = max(hourly_max - hourly_min, 1)
        pad_frac = 0.02
        cumul_range_padded = [cumul_min - pad_frac * cumul_span, cumul_max + pad_frac * cumul_span]
        hourly_range_padded = [hourly_min - pad_frac * hourly_span, hourly_max + pad_frac * hourly_span]

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
        cumul_y = [int(round(v)) for v in overall_diff.tolist()]
        fig.add_trace(
            go.Scatter(
                x=overall_diff.index, y=cumul_y,
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
        
        def _to_int(x):
            """Ensure plot values are Python ints (difference counts, not floats)."""
            return int(round(x)) if x == x else 0  # handle NaN

        for i in range(len(time_bins)):
            run_val = run_diff_hourly.iloc[i]
            sp_val = sp_diff_hourly.iloc[i]
            unk_val = unk_diff_hourly.iloc[i]

            # Separate positive and negative values (integers for bar heights)
            neg_run = _to_int(run_val) if run_val < 0 else 0
            neg_sp = _to_int(sp_val) if sp_val < 0 else 0
            neg_unk = _to_int(unk_val) if unk_val < 0 else 0

            pos_run = _to_int(run_val) if run_val > 0 else 0
            pos_sp = _to_int(sp_val) if sp_val > 0 else 0
            pos_unk = _to_int(unk_val) if unk_val > 0 else 0

            # Stack negative values (downward from 0)
            total_neg = neg_run + neg_sp + neg_unk

            neg_base_run = neg_run
            neg_base_sp = neg_run + neg_sp
            neg_base_unk = total_neg

            run_neg_values.append(abs(neg_run) if neg_run < 0 else 0)
            run_neg_bases.append(neg_base_run)

            sp_neg_values.append(abs(neg_sp) if neg_sp < 0 else 0)
            sp_neg_bases.append(neg_base_sp)

            unk_neg_values.append(abs(neg_unk) if neg_unk < 0 else 0)
            unk_neg_bases.append(neg_base_unk)

            # Stack positive values (upward from 0)
            pos_base_run = 0
            pos_base_sp = pos_run
            pos_base_unk = pos_run + pos_sp

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
        
        # Explicit x-axis range so the black zero line can span full plot width (same range used for line)
        x_span = (time_bins[-1] - time_bins[0]).total_seconds() if len(time_bins) > 1 else 86400
        x_pad = max(x_span * 0.02, 3600)  # 2% of span or 1 hour
        x_min = time_bins[0] - pd.Timedelta(seconds=x_pad)
        x_max = time_bins[-1] + pd.Timedelta(seconds=x_pad)

        # --- Zero Reference Lines ---
        # Left (cumulative) axis zero: thicker dashed grey line
        fig.add_hline(
            y=0,
            line_width=2,
            line_color="gray",
            line_dash="dash",
            row=1,
            col=1
        )
        # Right (bar) axis zero: same dashed style but black; x matches axis range so line spans full width
        fig.add_trace(
            go.Scatter(
                x=[x_min, x_max],
                y=[0, 0],
                mode="lines",
                line=dict(dash="dash", color="black", width=2),
                showlegend=False,
            ),
            row=1,
            col=1,
            secondary_y=True,
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
        
        # Header: callsigns with arithmetic minus (e.g. AA1K − K5ZD), callsign part bold
        title_lines = get_standard_title_lines(
            f"{self.report_name} ({metric_name})",
            self.logs,
            band_filter,
            mode_filter,
            modes_present,
            callsign_separator=" \u2212 ",  # arithmetic minus sign
            callsigns_bold=True,
        )

        footer_text = get_standard_footer(self.logs)

        # --- Layout Standardization ---
        # Pass list directly to Manager for Annotation Stack generation
        layout = PlotlyStyleManager.get_standard_layout(title_lines, footer_text)
        
        fig.update_layout(layout)
        
        # Update layout with basic settings (axis config applied after so it is not overwritten)
        fig.update_layout(
            width=1200,
            height=900,
            xaxis_title="Contest Time",
            barmode='overlay',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        # X-axis range matches black zero line so plot width and line span are consistent
        fig.update_xaxes(range=[x_min, x_max], row=1, col=1)

        # Grid: darker than default so lines are more prominent (not full black)
        grid_style = dict(showgrid=True, gridcolor="#555555", gridwidth=1.1)

        # Configure primary Y-axis (cumulative) - row 1, col 1; padded range so top/bottom grid lines visible
        fig.update_yaxes(
            title_text=f"Cumulative Diff ({metric_name})",
            range=cumul_range_padded,
            tickmode='array',
            tickvals=cumul_tickvals,
            ticktext=[str(v) for v in cumul_tickvals],
            row=1,
            col=1,
            **grid_style
        )

        # Configure secondary Y-axis (hourly bars) - same N grid lines, labels multiples of 5
        fig.update_yaxes(
            title_text=f"Hourly {metric_name} Difference",
            range=hourly_range_padded,
            tickmode='array',
            tickvals=hourly_tickvals,
            ticktext=hourly_ticktext,
            secondary_y=True,
            row=1,
            col=1,
            **grid_style
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
            # Re-apply axis config so layout update does not override ranges/ticks
            fig.update_xaxes(range=[x_min, x_max], row=1, col=1)
            fig.update_yaxes(
                range=cumul_range_padded,
                tickmode='array',
                tickvals=cumul_tickvals,
                ticktext=[str(v) for v in cumul_tickvals],
                row=1,
                col=1
            )
            fig.update_yaxes(
                range=hourly_range_padded,
                tickmode='array',
                tickvals=hourly_tickvals,
                ticktext=hourly_ticktext,
                secondary_y=True,
                row=1,
                col=1
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
        Runs both QSOs and Points variants when the contest uses a points-based score (e.g. WPX, CQ WW).
        """
        if len(self.logs) != 2:
            return "Error: The Cumulative Difference Plot report requires exactly two logs."

        log1, log2 = self.logs[0], self.logs[1]
        df1_full = get_valid_dataframe(log1)
        df2_full = get_valid_dataframe(log2)

        if df1_full.empty or df2_full.empty:
            return "Skipping report: At least one log has no valid QSO data."

        # Determine metrics: always QSOs; add Points when contest uses points-based scoring
        contest_def = log1.contest_definition
        score_formula = contest_def.score_formula
        metrics_to_run = ['qsos']
        if score_formula in ('total_points', 'points_times_mults'):
            metrics_to_run.append('points')

        all_created_files = []

        for metric in metrics_to_run:
            metric_kwargs = {**kwargs, 'metric': metric}

            # 1. Generate plots for "All Modes"
            all_created_files.extend(
                self._orchestrate_plot_generation(dfs=[df1_full, df2_full], output_path=output_path, mode_filter=None, **metric_kwargs)
            )

            # 2. Generate plots for each mode if applicable
            modes_present = pd.concat([df1_full['Mode'], df2_full['Mode']]).dropna().unique()
            if len(modes_present) > 1:
                # Include all standard modes: CW, PH (SSB), DG (Digital), RY (RTTY)
                for mode in ['CW', 'PH', 'DG', 'RY']:
                    if mode in modes_present:
                        sliced_dfs = [df[df['Mode'] == mode] for df in [df1_full, df2_full]]

                        all_created_files.extend(
                            self._orchestrate_plot_generation(sliced_dfs, output_path, mode_filter=mode, **metric_kwargs)
                        )

        if not all_created_files:
            return f"No difference plots were generated (metrics tried: {', '.join(metrics_to_run)})."

        return f"Cumulative difference plots for {', '.join(metrics_to_run)} saved to relevant subdirectories."