# contest_tools/reports/chart_qso_breakdown_contest_wide.py
#
# Purpose: A chart report that generates contest-wide QSO breakdown charts for contests
#          where QSOs count once per contest (dupe_check_scope: "all_bands"), not per band.
#          Generates two charts: Contest-Wide QSO Breakdown (primary) and QSO Band Distribution (secondary).
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
from plotly.subplots import make_subplots
from contest_tools.reports.report_interface import ContestReport
from contest_tools.contest_log import ContestLog
from contest_tools.data_aggregators.categorical_stats import CategoricalAggregator
from contest_tools.styles.plotly_style_manager import PlotlyStyleManager
from contest_tools.reports.qso_chart_helpers import (
    build_qso_chart_filename,
    apply_qso_chart_styling,
    save_qso_chart_files,
    prepare_qso_chart_title
)
from contest_tools.utils.report_utils import get_valid_dataframe, get_standard_footer


class Report(ContestReport):
    """
    Generates contest-wide QSO breakdown charts for contests where QSOs count once per contest.
    Creates two charts:
    1. Contest-Wide QSO Breakdown (primary): Single stacked bar showing Log1 Unique | Common | Log2 Unique
    2. QSO Band Distribution (secondary): Subplots per band showing unique QSOs worked on each band
    """
    report_id = 'qso_breakdown_chart_contest_wide'
    report_name = 'QSO Breakdown - Contest Wide'
    report_type = 'chart'
    supports_pairwise = True

    def __init__(self, logs: List[ContestLog]):
        super().__init__(logs)
        if len(logs) != 2:
            raise ValueError("ChartQSOBreakdownContestWide requires exactly two logs for comparison.")
        self.log1 = logs[0]
        self.log2 = logs[1]
        self.aggregator = CategoricalAggregator()

    def _check_contest_wide_qso(self) -> bool:
        """
        Checks if this contest uses contest-wide QSO counting.
        
        Returns:
            True if dupe_check_scope == "all_bands", False otherwise
        """
        contest_def = self.log1.contest_definition
        return getattr(contest_def, 'dupe_check_scope', None) == 'all_bands'

    def _generate_contest_wide_breakdown(self, output_path: str) -> List[str]:
        """
        Generates the contest-wide QSO breakdown chart (primary view).
        Single stacked bar: Log1 Unique | Common | Log2 Unique
        
        Returns:
            List of generated file paths
        """
        # Get contest-wide data (no band filter)
        comparison_data = self.aggregator.compute_comparison_breakdown(
            self.log1,
            self.log2,
            band_filter=None,
            mode_filter=None
        )
        
        # Prepare categories and data
        log1_call = self.log1.get_metadata().get('MyCall', 'Log1')
        log2_call = self.log2.get_metadata().get('MyCall', 'Log2')
        
        categories = [log1_call, "Common", log2_call]
        modes = ['Run', 'S&P', 'Mixed/Unk']
        colors = PlotlyStyleManager.get_qso_mode_colors()
        
        # Build figure
        fig = go.Figure()
        
        for mode in modes:
            if mode == 'Run':
                y_values = [
                    comparison_data['log1_unique']['run'],
                    comparison_data['common']['run_both'],
                    comparison_data['log2_unique']['run']
                ]
            elif mode == 'S&P':
                y_values = [
                    comparison_data['log1_unique']['sp'],
                    comparison_data['common']['sp_both'],
                    comparison_data['log2_unique']['sp']
                ]
            else:  # Mixed/Unk
                y_values = [
                    comparison_data['log1_unique']['unk'],
                    comparison_data['common']['mixed'],
                    comparison_data['log2_unique']['unk']
                ]
            
            fig.add_trace(go.Bar(
                name=mode,
                x=categories,
                y=y_values,
                marker_color=colors[mode]
            ))
        
        # Apply styling
        title_lines = prepare_qso_chart_title(
            "QSO Breakdown - Contest Total",
            self.logs,
            "Contest Total"
        )
        footer_text = get_standard_footer(self.logs)
        apply_qso_chart_styling(fig, title_lines, footer_text, barmode='stack')
        
        # Save files
        base_filename = build_qso_chart_filename(self.report_id, self.logs)
        return save_qso_chart_files(fig, output_path, base_filename)

    def _generate_band_distribution(self, output_path: str) -> List[str]:
        """
        Generates the QSO Band Distribution chart (secondary view).
        Shows band distribution of unique QSOs (symmetric difference).
        One subplot per band, two bars per subplot (Log1, Log2) - NO "Common" category.
        
        Returns:
            List of generated file paths
        """
        # Get band distribution data using new aggregator method
        band_data = self.aggregator.compute_band_distribution_breakdown(self.log1, self.log2)
        
        # Get valid bands from contest definition
        contest_def = self.log1.contest_definition
        valid_bands = contest_def.valid_bands
        
        # Filter to bands that have data
        bands_with_data = []
        for band in valid_bands:
            if band in band_data['bands']:
                band_info = band_data['bands'][band]
                # Check if either log has data for this band
                if (band_info['log1']['run'] + band_info['log1']['sp'] + band_info['log1']['unk'] > 0 or
                    band_info['log2']['run'] + band_info['log2']['sp'] + band_info['log2']['unk'] > 0):
                    bands_with_data.append(band)
        
        if not bands_with_data:
            return []
        
        # Sort bands in canonical order
        canonical_band_order = [b[1] for b in ContestLog._HAM_BANDS]
        bands_with_data = sorted(
            bands_with_data,
            key=lambda b: canonical_band_order.index(b) if b in canonical_band_order else 99
        )
        
        # Grid Calculation
        num_bands = len(bands_with_data)
        cols = min(3, num_bands)
        rows = (num_bands + cols - 1) // cols
        
        fig = make_subplots(
            rows=rows,
            cols=cols,
            shared_yaxes=True,
            vertical_spacing=0.15
        )
        
        colors = PlotlyStyleManager.get_qso_mode_colors()
        log1_call = self.log1.get_metadata().get('MyCall', 'Log1')
        log2_call = self.log2.get_metadata().get('MyCall', 'Log2')
        categories = [log1_call, log2_call]  # NO "Common" category
        
        for i, band in enumerate(bands_with_data):
            row = (i // cols) + 1
            col = (i % cols) + 1
            
            band_info = band_data['bands'][band]
            
            # Show legend only on the first subplot
            show_legend = (i == 0)
            
            # Add traces for each mode
            modes = ['Run', 'S&P', 'Mixed/Unk']
            for mode in modes:
                if mode == 'Run':
                    y_values = [band_info['log1']['run'], band_info['log2']['run']]
                elif mode == 'S&P':
                    y_values = [band_info['log1']['sp'], band_info['log2']['sp']]
                else:  # Mixed/Unk
                    y_values = [band_info['log1']['unk'], band_info['log2']['unk']]
                
                fig.add_trace(
                    go.Bar(
                        name=mode,
                        x=categories,
                        y=y_values,
                        marker_color=colors[mode],
                        showlegend=show_legend,
                        legendgroup=mode
                    ),
                    row=row, col=col
                )
            
            fig.update_xaxes(title_text=band, title_standoff=5, row=row, col=col)
        
        # Apply styling
        title_lines = prepare_qso_chart_title(
            "QSO Band Distribution",
            self.logs,
            "Band Distribution of Worked Stations"
        )
        footer_text = get_standard_footer(self.logs)
        apply_qso_chart_styling(fig, title_lines, footer_text, barmode='stack')
        
        # Save files
        base_filename = build_qso_chart_filename('qso_band_distribution', self.logs)
        return save_qso_chart_files(fig, output_path, base_filename)

    def generate(self, output_path: str, **kwargs) -> List[str]:
        """
        Generates both contest-wide QSO breakdown charts.
        Returns a list of generated file paths.
        """
        # Check if this contest uses contest-wide QSO counting
        if not self._check_contest_wide_qso():
            # Skip if not contest-wide QSO counting
            return []
        
        all_outputs = []
        
        # Generate contest-wide breakdown (primary view)
        contest_wide_outputs = self._generate_contest_wide_breakdown(output_path)
        all_outputs.extend(contest_wide_outputs)
        
        # Generate band distribution (secondary view)
        band_dist_outputs = self._generate_band_distribution(output_path)
        all_outputs.extend(band_dist_outputs)
        
        return all_outputs
