# Contest Log Analyzer/contest_tools/reports/chart_point_contribution_single.py
#
# Purpose: Generates a single-log report with per-band pie charts and tables
#          showing the breakdown of QSO points.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-05
# Version: 0.30.0-Beta
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
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
# - Standardized all project files to a common baseline version.
from .report_interface import ContestReport
from ._report_utils import get_valid_dataframe, create_output_directory
import matplotlib.pyplot as plt
import pandas as pd
import os
import logging
from ..contest_log import ContestLog

class Report(ContestReport):
    """
    Generates a single-log report with per-band pie charts for QSO point contributions.
    """
    report_id = "chart_point_contribution_single"
    report_name = "Point Contribution Breakdown (Single Log)"
    report_type = "chart"
    supports_single = True
    supports_pairwise = False
    supports_multi = False

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the per-band pie charts and summary table.
        """
        create_output_directory(output_path)
        include_dupes = kwargs.get('include_dupes', False)
        
        log = self.logs[0]
        callsign = log.get_metadata().get('MyCall', 'Log')
        df = get_valid_dataframe(log, include_dupes)

        if df['QSOPoints'].sum() == 0:
            return f"Skipping '{self.report_name}': No QSO points found in log for {callsign}."

        bands = sorted(df['Band'].unique(), key=ContestLog._HF_BANDS.index)
        
        # Determine grid size
        num_bands = len(bands)
        if num_bands <= 3:
            nrows, ncols = 1, num_bands
            figsize = (6 * ncols, 5)
        elif num_bands <= 6:
            nrows, ncols = 2, 3
            figsize = (18, 10)
        else: # Handles up to 9 bands
            nrows, ncols = 3, 3
            figsize = (18, 15)

        fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
        axes = axes.flatten() # Flatten to 1D array for easy iteration

        fig.suptitle(f'QSO Point Contribution for {callsign}', fontsize=16, y=1.0)

        for i, band in enumerate(bands):
            ax = axes[i]
            band_df = df[df['Band'] == band]
            
            point_counts = band_df['QSOPoints'].value_counts().sort_index()
            point_labels = [f'{idx}-pt\n({val:,.0f})' for idx, val in point_counts.items()]

            wedges, texts, autotexts = ax.pie(
                point_counts, labels=point_labels, autopct='%1.1f%%',
                startangle=90, textprops={'fontsize': 9}, wedgeprops={'edgecolor': 'white'}
            )
            ax.set_title(f'{band}\n{band_df["QSOPoints"].sum():,.0f} Pts', fontsize=11, weight='bold')
            plt.setp(autotexts, size=9, weight="bold", color="white")

        # Hide any unused subplots
        for j in range(num_bands, len(axes)):
            fig.delaxes(axes[j])
            
        plt.tight_layout(rect=[0, 0, 1, 0.96])

        # --- Save the chart ---
        output_filename = os.path.join(output_path, f"{self.report_id}_{callsign}.png")
        try:
            plt.savefig(output_filename, bbox_inches='tight', dpi=150)
            plt.close(fig)
            logging.info(f"Successfully generated '{self.report_name}' for {callsign} and saved to {output_filename}")
            return f"'{self.report_name}' for {callsign} saved to {output_filename}"
        except Exception as e:
            logging.error(f"Error saving chart for {callsign}: {e}")
            plt.close(fig)
            return f"Error generating report '{self.report_name}' for {callsign}"