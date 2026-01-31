# contest_tools/reports/chart_rate.py
#
# Purpose: Side-by-side bar chart of stations' hourly rates (QSO or points per hour)
#          for 1–3 logs. All bands, all modes. Single color per station.
#          Time segmentation: 1 log up to 48h; 2 logs 24h/segment (30h → 2×15h);
#          3 logs 12h/segment (30h → 2×15h). Produces "QSO Rate Chart" and
#          "Point Rate Chart" (points only when contest uses points).
#
# Copyright (c) 2025 Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import math
import os
import logging
from typing import List, Tuple

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..contest_log import ContestLog
from .report_interface import ContestReport
from contest_tools.utils.report_utils import (
    create_output_directory,
    get_valid_dataframe,
    get_standard_footer,
    get_standard_title_lines,
    build_filename,
)
from ..data_aggregators.time_series import TimeSeriesAggregator
from ..styles.plotly_style_manager import PlotlyStyleManager


def _compute_segments(
    n_bins: int, n_logs: int
) -> List[Tuple[int, int]]:
    """
    Return list of (start_idx, end_idx) for time segments.
    - 1 log: max 48h per chart → one segment if n_bins <= 48, else 48h segments.
    - 2 logs: max 24h per chart; 30h contest → 2 segments of 15h.
    - 3 logs: max 12h per chart; 30h contest → 2 segments of 15h.
    """
    if n_bins <= 0:
        return []
    max_per_segment = {1: 48, 2: 24, 3: 12}.get(n_logs, 24)
    if n_bins <= max_per_segment:
        return [(0, n_bins)]
    # 30-hour contest: always 2 segments of 15h
    if n_bins == 30:
        return [(0, 15), (15, 30)]
    n_segments = math.ceil(n_bins / max_per_segment)
    segment_size = n_bins // n_segments
    segments = []
    start = 0
    for _ in range(n_segments - 1):
        segments.append((start, start + segment_size))
        start += segment_size
    segments.append((start, n_bins))
    return segments


class Report(ContestReport):
    """
    Generates QSO Rate Chart and (when contest uses points) Point Rate Chart:
    side-by-side hourly bars per station, all bands all modes, one color per station.
    Supports 1, 2, or 3 logs. Time is segmented per spec (48/24/12 or 15h for 30h).
    """

    report_id: str = "chart_rate"
    report_name: str = "Rate Chart"
    report_type: str = "chart"
    supports_single: bool = True
    supports_pairwise: bool = True
    supports_multi: bool = True

    def generate(self, output_path: str, **kwargs) -> str:
        n_logs = len(self.logs)
        if n_logs < 1 or n_logs > 3:
            return "Error: Rate Chart supports 1, 2, or 3 logs only."

        valid_logs = []
        for log in self.logs:
            df = get_valid_dataframe(log)
            if not df.empty:
                valid_logs.append(log)
        if not valid_logs:
            return "Skipping report: No logs have valid QSO data."

        contest_def = valid_logs[0].contest_definition
        score_formula = getattr(contest_def, "score_formula", None) or contest_def._data.get(
            "score_formula", "points_times_mults"
        )
        metrics_to_run = ["qsos"]
        if score_formula in ("total_points", "points_times_mults"):
            metrics_to_run.append("points")

        get_cached_ts_data = kwargs.get("_get_cached_ts_data")
        if get_cached_ts_data:
            ts_data = get_cached_ts_data()
        else:
            agg = TimeSeriesAggregator(valid_logs)
            ts_data = agg.get_time_series_data()
        time_bins = [pd.Timestamp(t) for t in ts_data["time_bins"]]
        if not time_bins:
            return "Skipping report: No time series data."

        n_bins = len(time_bins)
        n_logs = len(valid_logs)
        segments = _compute_segments(n_bins, n_logs)
        if not segments:
            return "Skipping report: No time segments to plot."

        calls = [log.get_metadata().get("MyCall", "Unknown") for log in valid_logs]
        metric_names = {"qsos": "QSO Rate Chart", "points": "Point Rate Chart"}

        create_output_directory(output_path)
        generated = []
        modes_present = set()
        for log in valid_logs:
            df = get_valid_dataframe(log)
            if "Mode" in df.columns:
                modes_present.update(df["Mode"].dropna().unique())

        for metric in metrics_to_run:
            title_display = metric_names[metric]
            y_label = "QSOs per Hour" if metric == "qsos" else (contest_def.points_header_label or "Points") + " per Hour"

            # Independent x-axes per row so each subplot shows only its segment's time range.
            fig = make_subplots(
                rows=len(segments),
                cols=1,
                shared_xaxes=False,
                vertical_spacing=0.06,
                subplot_titles=[
                    _segment_title(time_bins[s], time_bins[e - 1], s, e)
                    for s, e in segments
                ],
                specs=[[{"type": "xy"}] for _ in segments],
            )

            # Use integer x (hour index within segment) so Plotly groups bars. Datetime x uses
            # a continuous axis and grouping/offset does not work there (bars stack).
            for call in calls:
                log_entry = ts_data["logs"].get(call)
                if not log_entry:
                    continue
                hourly_vals = log_entry["hourly"].get(metric)
                if not hourly_vals or len(hourly_vals) != n_bins:
                    hourly_vals = [0] * n_bins
                idx = calls.index(call)
                color = PlotlyStyleManager._COLOR_PALETTE[idx % len(PlotlyStyleManager._COLOR_PALETTE)]

                for row_idx, (s, e) in enumerate(segments):
                    seg_len = e - s
                    # Integer x: 0, 1, ..., seg_len-1 so barmode='group' produces N bars per hour.
                    x_positions = list(range(seg_len))
                    seg_y = [int(hourly_vals[i]) if i < len(hourly_vals) else 0 for i in range(s, e)]
                    fig.add_trace(
                        go.Bar(
                            x=x_positions,
                            y=seg_y,
                            name=call,
                            marker_color=color,
                            showlegend=(row_idx == 0),
                            legendgroup=call,
                        ),
                        row=row_idx + 1,
                        col=1,
                    )

            # Vertical grouped bar chart (not stacked): N bars per hour = one per station.
            fig.update_layout(
                template="plotly_white",
                barmode="group",
                bargap=0,
                width=1200,
                height=400 * len(segments),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(t=120, b=180, l=50, r=50),
            )
            title_lines = get_standard_title_lines(
                title_display,
                valid_logs,
                "All",
                None,
                modes_present,
                callsign_separator=" \u2212 ",
                callsigns_bold=True,
            )
            title_text = f"<b>{title_lines[0]}</b><br><sup>{title_lines[1]}</sup>"
            if len(title_lines) > 2 and title_lines[2]:
                title_text += f"<br><sup>{title_lines[2]}</sup>"
            fig.add_annotation(
                text=title_text,
                xref="paper",
                yref="paper",
                x=0,
                y=1.0,
                xanchor="left",
                yanchor="bottom",
                yshift=25,
                showarrow=False,
                font=dict(size=20),
            )
            footer_text = get_standard_footer(valid_logs)
            fig.add_annotation(
                text=footer_text.replace("\n", "<br>"),
                xref="paper",
                yref="paper",
                x=0.5,
                y=0,
                xanchor="center",
                yanchor="top",
                showarrow=False,
                font=dict(size=10, color="gray"),
                yshift=-80,
            )
            # Each row: integer x 0..seg_len-1; tick labels = contest hour numbers (1-based).
            for row_idx, (s, e) in enumerate(segments):
                seg_len = e - s
                tickvals = list(range(seg_len))
                ticktext = [str(s + i + 1) for i in range(seg_len)]
                fig.update_xaxes(
                    title_text="",
                    showticklabels=True,
                    tickmode="array",
                    tickvals=tickvals,
                    ticktext=ticktext,
                    row=row_idx + 1,
                    col=1,
                )
                fig.update_yaxes(title_text=y_label, row=row_idx + 1, col=1)

            base_filename = build_filename(f"{self.report_id}_{metric}", valid_logs, "All", None)
            html_path = os.path.join(output_path, f"{base_filename}.html")
            json_path = os.path.join(output_path, f"{base_filename}.json")
            try:
                config = {"toImageButtonOptions": {"filename": base_filename, "format": "png"}}
                fig.write_html(html_path, include_plotlyjs="cdn", config=config)
                generated.append(html_path)
            except Exception as e:
                logging.error("Failed to save Rate Chart HTML: %s", e)
            try:
                fig.write_json(json_path)
                generated.append(json_path)
            except Exception as e:
                logging.error("Failed to save Rate Chart JSON: %s", e)

        if not generated:
            return "No Rate Chart files generated."
        return f"Rate Chart saved to {output_path}."


def _segment_title(first_ts: pd.Timestamp, last_ts: pd.Timestamp, start_idx: int, end_idx: int) -> str:
    """Human-readable segment label, e.g. 'Hours 1–15'."""
    return f"Hours {start_idx + 1}–{end_idx}"
