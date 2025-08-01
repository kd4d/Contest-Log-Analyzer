# Contest Log Analyzer/contest_tools/reports/chart_point_contribution_single.py
#
# Purpose: A chart report that generates a per-band breakdown of total points
#          by QSO point value, presented as a series of proportionally-sized
#          pie charts for a single log.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-01
# Version: 0.22.23-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# --- Revision History ---
# All notable changes to this project will be documented in this file.
# The format is based on "Keep a Changelog" (https://keepachangelog.com/en/1.0.0/),
# and this project aims to adhere to Semantic Versioning (https://semver.org/).

## [0.22.23-Beta] - 2025-08-01
### Changed
# - Corrected the vertical position of the "*NOT TO SCALE*" note, moving it
#   up to sit correctly between the chart and the table.

## [0.22.22-Beta] - 2025-08-01
### Changed
# - Corrected the vertical position of the "*NOT TO SCALE*" note, moving it
#   up to sit correctly between the chart and the table.

## [0.22.21-Beta] - 2025-08-01
### Changed
# - Corrected the vertical position of the "*NOT TO SCALE*" note, moving it
#   up to sit correctly between the chart and the table.

## [0.22.20-Beta] - 2025-08-01
### Changed
# - Further adjusted the vertical position of the "*NOT TO SCALE*" note to
#   center it correctly between the chart and the table.

## [0.22.19-Beta] - 2025-08-01
### Changed
# - Further adjusted the vertical position of the "*NOT TO SCALE*" note to
#   place it closer to the pie chart it refers to.

## [0.22.18-Beta] - 2025-08-01
### Changed
# - Increased the font size and corrected the vertical position of the
#   "*NOT TO SCALE*" note for better visibility and layout.

## [0.22.17-Beta] - 2025-08-01
### Changed
# - Increased the font size and adjusted the vertical position of the
#   "*NOT TO SCALE*" note for better visibility and layout.

## [0.22.16-Beta] - 2025-08-01
### Added
# - A "*NOT TO SCALE" note is now added below any pie chart that is rendered
#   at the minimum size, clarifying its proportionality.

## [0.22.12-Beta] - 2025-08-01
### Changed
# - Reverted the label placement logic. Percentage labels are now always
#   drawn inside the pie chart.
# - Reduced the font size of the percentage labels to prevent overlap on
#   smaller charts.

## [0.22.11-Beta] - 2025-08-01
### Changed
# - Refined the threshold for moving percentage labels outside the pie chart
#   to affect only the smallest charts.
# - Increased the distance for external labels and their connecting lines.

## [0.22.10-Beta] - 2025-08-01
### Changed
# - For smaller pie charts, the percentage labels are now drawn outside the
#   slices with connecting lines to prevent text overlap and improve readability.

## [0.22.9-Beta] - 2025-07-31
### Changed
# - Slightly reduced the maximum radius of the pie charts to prevent any
#   overlap with the subplot titles.

## [0.22.8-Beta] - 2025-07-31
### Changed
# - Further adjusted the vertical positioning of the pie charts and tables
#   to achieve better centering within the subplot area.

## [0.22.7-Beta] - 2025-07-31
### Changed
# - Adjusted the vertical positioning of the pie charts and summary tables
#   to create a more balanced and centered layout.

## [0.22.6-Beta] - 2025-07-31
### Changed
# - Removed markdown bold characters from titles and increased title font
#   sizes for better readability.

## [0.22.5-Beta] - 2025-07-31
### Changed
# - Adjusted the vertical positioning of the pie charts and summary tables
#   to create a more balanced and centered layout.

## [0.22.4-Beta] - 2025-07-31
### Changed
# - The proportional sizing logic now enforces a minimum chart area of 5%
#   of the largest chart for any band with points.

## [0.22.3-Beta] - 2025-07-31
### Changed
# - Reduced the maximum radius for the pie charts to prevent the largest
#   chart from overlapping with the subplot title.

## [0.22.2-Beta] - 2025-07-31
### Changed
# - Reworked the pie chart sizing logic. The AREA of each chart is now
#   proportional to the total points for that band, providing a more
#   accurate visual representation.
# - Increased the overall size of the pie charts to better fill the subplot area.

## [0.22.1-Beta] - 2025-07-31
### Changed
# - The radius of each band's pie chart is now proportional to the total
#   points earned on that band, not the total number of QSOs.

## [0.22.0-Beta] - 2025-07-31
# - Initial release of the Single Log Point Contribution chart report.

from typing import List
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a chart with a grid of pie charts and tables, one for each band,
    showing the breakdown of total points by the point value of each QSO.
    The size of each pie chart is proportional to its point total.
    """
    supports_single = True

    @property
    def report_id(self) -> str:
        return "chart_point_contribution_single"

    @property
    def report_name(self) -> str:
        return "Single Log Point Contribution"

    @property
    def report_type(self) -> str:
        return "chart"

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content.
        """
        final_report_messages = []

        for log in self.logs:
            try:
                filepath = self._create_plot_for_log(log, output_path)
                if filepath:
                    final_report_messages.append(f"Chart saved to: {filepath}")
            except Exception as e:
                final_report_messages.append(f"Failed to generate chart for {log.get_metadata().get('MyCall', 'Unknown')}: {e}")
        
        return "\n".join(final_report_messages)

    def _create_plot_for_log(self, log: ContestLog, output_path: str) -> str:
        """
        Creates a single multi-plot image for a given log.
        """
        metadata = log.get_metadata()
        callsign = metadata.get('MyCall', 'UnknownCall')
        df_full = log.get_processed_data()
        df = df_full[df_full['Dupe'] == False].copy()

        if df.empty or 'QSOPoints' not in df.columns:
            return None

        bands = ['160M', '80M', '40M', '20M', '15M', '10M']
        
        # --- Pre-calculate band points for proportional sizing ---
        band_points = {band: df[df['Band'] == band]['QSOPoints'].sum() for band in bands}
        max_band_points = max(band_points.values()) if band_points else 1

        # --- Plot Layout ---
        fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(20, 14))
        axes = axes.flatten()

        # --- Generate a subplot for each band ---
        for i, band in enumerate(bands):
            ax = axes[i]
            band_df = df[df['Band'] == band]

            if band_df.empty or band_df['QSOPoints'].sum() == 0:
                ax.text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=12)
                ax.set_title(f"{band.replace('M','')} Meters", fontweight='bold', fontsize=16)
                ax.axis('off')
                continue

            # --- Data Aggregation for the subplot ---
            point_summary = band_df.groupby('QSOPoints').agg(
                QSOs=('Call', 'count')
            ).reset_index()
            point_summary['Points'] = point_summary['QSOPoints'] * point_summary['QSOs']
            point_summary['AVG'] = point_summary['QSOPoints']

            # --- Proportional Pie Chart Sizing ---
            current_band_points = band_points.get(band, 0)
            point_ratio = (current_band_points / max_band_points) if max_band_points > 0 else 0
            
            is_not_to_scale = False
            if 0 < point_ratio < 0.05:
                point_ratio = 0.05
                is_not_to_scale = True

            max_radius = 1.25
            radius = max_radius * np.sqrt(point_ratio)

            pie_data = point_summary.set_index('QSOPoints')['Points']
            labels = [f"{idx} Pts" for idx in pie_data.index]
            
            wedges, texts, autotexts = ax.pie(pie_data, labels=labels, autopct='%1.1f%%',
                                              startangle=90, counterclock=False, radius=radius,
                                              center=(0, 0.1))
            for autotext in autotexts:
                autotext.set_fontsize(8)

            ax.set_title(f"{band.replace('M','')} Meters", fontweight='bold', fontsize=16)

            # --- Add "Not to Scale" note if needed ---
            if is_not_to_scale:
                ax.text(0.5, 0.0, "*NOT TO SCALE*", ha='center', va='center',
                        transform=ax.transAxes, fontsize=12, fontweight='bold')

            # --- Summary Table ---
            total_row = pd.DataFrame({
                'QSOPoints': ['Total'],
                'QSOs': [point_summary['QSOs'].sum()],
                'Points': [point_summary['Points'].sum()],
                'AVG': [point_summary['Points'].sum() / point_summary['QSOs'].sum() if point_summary['QSOs'].sum() > 0 else 0]
            })
            
            table_data = pd.concat([point_summary, total_row], ignore_index=True)
            table_data['AVG'] = table_data['AVG'].map('{:.2f}'.format)
            
            cell_text = table_data[['QSOPoints', 'QSOs', 'Points', 'AVG']].values
            col_labels = ['Pts/QSO', 'QSOs', 'Points', 'Avg']
            
            table = ax.table(cellText=cell_text, colLabels=col_labels, cellLoc='center', loc='bottom', bbox=[0.1, -0.5, 0.8, 0.4])
            table.auto_set_font_size(False)
            table.set_fontsize(10)

        # --- Final Formatting and Save ---
        fig.suptitle(f"{callsign} - Point Contribution Breakdown by Band", fontsize=22, fontweight='bold')
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])

        os.makedirs(output_path, exist_ok=True)
        filename = f"{self.report_id}_{callsign}.png"
        filepath = os.path.join(output_path, filename)
        fig.savefig(filepath, bbox_inches='tight')
        plt.close(fig)

        return filepath
