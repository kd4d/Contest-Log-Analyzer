# contest_tools/reports/chart_activity.py
#
# Purpose: A single Plotly figure with two butterfly charts: (1) All Bands
#          Run/S&P/Unknown for two logs (six bar elements, 3 above zero, 3 below),
#          (2) Hourly Difference. QSO and Points variants. Standard project title/header.
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
import logging
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


class Report(ContestReport):
    """
    Generates a single figure with two butterfly charts: top = All Bands (six bar
    elements: Log1 Run/S&P/Unknown above zero, Log2 Run/S&P/Unknown below zero);
    bottom = Hourly Difference. Standard project title/header with callsigns.
    QSO and Points variants via metric kwarg.
    """
    report_id: str = "chart_activity"
    report_name: str = "Activity Chart"
    report_type: str = "chart"
    supports_pairwise = True

    def generate(self, output_path: str, **kwargs) -> str:
        if len(self.logs) != 2:
            return "Error: The Activity Chart report requires exactly two logs."

        log1, log2 = self.logs[0], self.logs[1]
        df1 = get_valid_dataframe(log1)
        df2 = get_valid_dataframe(log2)
        if df1.empty or df2.empty:
            return "Skipping report: At least one log has no valid QSO data."

        call1 = log1.get_metadata().get("MyCall", "Log1")
        call2 = log2.get_metadata().get("MyCall", "Log2")

        # All bands, all modes (fetch once; reuse for both metrics)
        get_cached_ts_data = kwargs.get("_get_cached_ts_data")
        if get_cached_ts_data:
            ts_data = get_cached_ts_data(band_filter="All", mode_filter=None)
        else:
            agg = TimeSeriesAggregator([log1, log2])
            ts_data = agg.get_time_series_data(band_filter="All", mode_filter=None)

        time_bins = [pd.Timestamp(t) for t in ts_data["time_bins"]]
        if not time_bins:
            return "Skipping report: No time series data."

        def hourly_series(call_key: str, field: str):
            vals = ts_data["logs"][call_key]["hourly"][field]
            return pd.Series(vals, index=time_bins)

        mode_colors = PlotlyStyleManager.get_qso_mode_colors()
        colors = {
            "Run": mode_colors["Run"],
            "S&P": mode_colors["S&P"],
            "Unknown": mode_colors["Mixed/Unk"],
        }

        create_output_directory(output_path)
        generated = []

        for metric in ("qsos", "points"):
            metric_name = "QSOs" if metric == "qsos" else (log1.contest_definition.points_header_label or "Points")
            if metric == "points":
                run1 = hourly_series(call1, "run_points")
                sp1 = hourly_series(call1, "sp_points")
                unk1 = hourly_series(call1, "unknown_points")
                run2 = hourly_series(call2, "run_points")
                sp2 = hourly_series(call2, "sp_points")
                unk2 = hourly_series(call2, "unknown_points")
            else:
                run1 = hourly_series(call1, "run_qsos")
                sp1 = hourly_series(call1, "sp_qsos")
                unk1 = hourly_series(call1, "unknown_qsos")
                run2 = hourly_series(call2, "run_qsos")
                sp2 = hourly_series(call2, "sp_qsos")
                unk2 = hourly_series(call2, "unknown_qsos")

            def to_list(s):
                return [int(round(v)) if v == v else 0 for v in s.tolist()]

            r1, s1, u1 = to_list(run1), to_list(sp1), to_list(unk1)
            r2, s2, u2 = to_list(run2), to_list(sp2), to_list(unk2)
            base_s1 = [a for a in r1]
            base_u1 = [a + b for a, b in zip(r1, s1)]
            r2_neg = [-v for v in r2]
            s2_neg = [-v for v in s2]
            u2_neg = [-v for v in u2]
            base_u2 = [-a for a in r2]
            base_u2_third = [-(a + b) for a, b in zip(r2, s2)]

            # Both rows must use the exact same x-axis (ticks and range): shared_xaxes=True.
            # Both rows must have one bar cluster per x (center-to-center): same offsetgroup per row.
            fig = make_subplots(
                rows=2,
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.02,
                row_heights=[0.5, 0.5],
                subplot_titles=(f"All {metric_name}", f"Hourly {metric_name} Difference"),
                specs=[[{"type": "xy"}], [{"type": "xy"}]],
            )

            # Unify offsetgroup + alignmentgroup across ALL bars so both rows occupy same horizontal slot
            shared_og = "activity_bars"
            fig.add_trace(
                go.Bar(
                    x=time_bins,
                    y=r1,
                    name="Run",
                    marker_color=colors["Run"],
                    showlegend=True,
                    legendgroup="Run",
                    offsetgroup=shared_og,
                    alignmentgroup=shared_og,
                ),
                row=1,
                col=1,
            )
            fig.add_trace(
                go.Bar(
                    x=time_bins,
                    y=s1,
                    base=base_s1,
                    name="S&P",
                    marker_color=colors["S&P"],
                    showlegend=True,
                    legendgroup="S&P",
                    offsetgroup=shared_og,
                    alignmentgroup=shared_og,
                ),
                row=1,
                col=1,
            )
            fig.add_trace(
                go.Bar(
                    x=time_bins,
                    y=u1,
                    base=base_u1,
                    name="Unknown",
                    marker_color=colors["Unknown"],
                    showlegend=True,
                    legendgroup="Unknown",
                    offsetgroup=shared_og,
                    alignmentgroup=shared_og,
                ),
                row=1,
                col=1,
            )
            fig.add_trace(
                go.Bar(
                    x=time_bins,
                    y=r2_neg,
                    base=[0] * len(time_bins),
                    marker_color=colors["Run"],
                    showlegend=False,
                    offsetgroup=shared_og,
                    alignmentgroup=shared_og,
                ),
                row=1,
                col=1,
            )
            fig.add_trace(
                go.Bar(
                    x=time_bins,
                    y=s2_neg,
                    base=base_u2,
                    marker_color=colors["S&P"],
                    showlegend=False,
                    offsetgroup=shared_og,
                    alignmentgroup=shared_og,
                ),
                row=1,
                col=1,
            )
            fig.add_trace(
                go.Bar(
                    x=time_bins,
                    y=u2_neg,
                    base=base_u2_third,
                    marker_color=colors["Unknown"],
                    showlegend=False,
                    offsetgroup=shared_og,
                    alignmentgroup=shared_og,
                ),
                row=1,
                col=1,
            )

            # ---- Row 2: Hourly Difference (stacked Run/S&P/Unknown difference) ----
            run_diff = run1 - run2
            sp_diff = sp1 - sp2
            unk_diff = unk1 - unk2

            def _to_int(x):
                return int(round(x)) if x == x else 0

            run_pos, run_neg = [], []
            run_pos_base, run_neg_base = [], []
            sp_pos, sp_neg = [], []
            sp_pos_base, sp_neg_base = [], []
            unk_pos, unk_neg = [], []
            unk_pos_base, unk_neg_base = [], []

            for i in range(len(time_bins)):
                r, s, u = run_diff.iloc[i], sp_diff.iloc[i], unk_diff.iloc[i]
                nr = _to_int(r) if r < 0 else 0
                ns = _to_int(s) if s < 0 else 0
                nu = _to_int(u) if u < 0 else 0
                pr = _to_int(r) if r > 0 else 0
                ps = _to_int(s) if s > 0 else 0
                pu = _to_int(u) if u > 0 else 0
                total_neg = nr + ns + nu
                run_neg.append(abs(nr) if nr < 0 else 0)
                run_neg_base.append(nr)
                sp_neg.append(abs(ns) if ns < 0 else 0)
                sp_neg_base.append(nr + ns)
                unk_neg.append(abs(nu) if nu < 0 else 0)
                unk_neg_base.append(total_neg)
                run_pos.append(pr if pr > 0 else 0)
                run_pos_base.append(0)
                sp_pos.append(ps if ps > 0 else 0)
                sp_pos_base.append(pr)
                unk_pos.append(pu if pu > 0 else 0)
                unk_pos_base.append(pr + ps)

            # Row 2: same offsetgroup + alignmentgroup so bars align with row 1
            for y_vals, base_vals, color_key in [
                (run_neg, run_neg_base, "Run"),
                (sp_neg, sp_neg_base, "S&P"),
                (unk_neg, unk_neg_base, "Unknown"),
            ]:
                fig.add_trace(
                    go.Bar(
                        x=time_bins,
                        y=y_vals,
                        base=base_vals,
                        marker_color=colors[color_key],
                        showlegend=False,
                        offsetgroup=shared_og,
                        alignmentgroup=shared_og,
                    ),
                    row=2,
                    col=1,
                )
            for y_vals, base_vals, color_key in [
                (run_pos, run_pos_base, "Run"),
                (sp_pos, sp_pos_base, "S&P"),
                (unk_pos, unk_pos_base, "Unknown"),
            ]:
                fig.add_trace(
                    go.Bar(
                        x=time_bins,
                        y=y_vals,
                        base=base_vals,
                        marker_color=colors[color_key],
                        showlegend=False,
                        offsetgroup=shared_og,
                        alignmentgroup=shared_og,
                    ),
                    row=2,
                    col=1,
                )

            fig.add_hline(y=0, line_width=1, line_color="gray", line_dash="dash", row=1, col=1)
            fig.add_hline(y=0, line_width=1, line_color="gray", line_dash="dash", row=2, col=1)

            # Standard project title/header (same pattern as chart_comparative_activity_butterfly)
            modes_present = set()
            for log in self.logs:
                df = get_valid_dataframe(log)
                if "Mode" in df.columns:
                    modes_present.update(df["Mode"].dropna().unique())
            title_lines = get_standard_title_lines(
                f"{self.report_name} ({metric_name})",
                self.logs,
                "All",
                None,
                modes_present,
                callsign_separator=" \u2212 ",
                callsigns_bold=True,
            )
            footer_text = get_standard_footer(self.logs)

            fig.update_layout(
                template="plotly_white",
                barmode="relative",
                bargap=0,
                width=1200,
                height=900,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                # Top margin: room for title above plot area; bottom: room for footer
                margin=dict(t=120, b=180, l=50, r=50),
            )
            # Title at top of image: bottom of text at top of plot area, text in margin (yshift up)
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
            # Footer: bottom center
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
            # shared_xaxes=True gives same x-axis; only bottom row shows x title/labels
            fig.update_xaxes(showticklabels=False, row=1, col=1)
            fig.update_xaxes(title_text="Contest Time", title_standoff=40, row=2, col=1)
            fig.update_yaxes(title_text=f"{metric_name} (All Bands)", row=1, col=1)
            fig.update_yaxes(title_text=f"Hourly {metric_name} Difference", row=2, col=1)

            base_filename = build_filename(f"{self.report_id}_{metric}", self.logs, "All", None)
            html_path = os.path.join(output_path, f"{base_filename}.html")
            json_path = os.path.join(output_path, f"{base_filename}.json")

            try:
                config = {"toImageButtonOptions": {"filename": base_filename, "format": "png"}}
                fig.write_html(html_path, include_plotlyjs="cdn", config=config)
                generated.append(html_path)
            except Exception as e:
                logging.error("Failed to save Activity Chart HTML: %s", e)
            try:
                fig.write_json(json_path)
                generated.append(json_path)
            except Exception as e:
                logging.error("Failed to save Activity Chart JSON: %s", e)

        if not generated:
            return "No Activity Chart files generated."
        return f"Activity Chart (QSO and Points) saved to {output_path}."
