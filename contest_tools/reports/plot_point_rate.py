# contest_tools/reports/plot_point_rate.py
#
# Purpose: A plot report that generates a point rate graph for all bands
#          and for each individual band.
#
# Author: Gemini AI
# Date: 2025-12-29
# Version: 0.134.0-Beta
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
# [0.134.0-Beta] - 2025-12-29
# - Refactored to inherit from BaseRateReport, reducing code duplication.
# [0.133.0-Beta] - 2025-12-20
# - Refactored `_create_plot` to use centralized `build_filename` utility.
# - Resolved NameError crash caused by missing `is_single_band` variable in plot generation scope.
# [0.131.0-Beta] - 2025-12-20
# - Refactored to use `get_standard_title_lines` for standardized 3-line headers.
# - Implemented explicit "Smart Scoping" for title generation.
# - Added footer metadata via `get_cty_metadata`.
# [0.118.0-Beta] - 2025-12-15
# - Injected descriptive filename configuration for interactive HTML plot downloads.
# [0.117.0-Beta] - 2025-12-15
# - Moved legend to top-left internal position to match QSO Rate Plot.
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

from .base_rate_report import BaseRateReport

class Report(BaseRateReport):
    """
    Generates a series of plots comparing cumulative points: one for all bands
    combined, and one for each individual contest band.
    """
    report_id: str = "point_rate_plots"
    report_name: str = "Point Rate Comparison Plots"
    
    # BaseRateReport configuration
    metric_key: str = "points"
    metric_label: str = "Points"

    def _get_metric_name(self) -> str:
        """Override to check for contest-specific point labels."""
        if self.logs:
             return self.logs[0].contest_definition.points_header_label or self.metric_label
        return self.metric_label