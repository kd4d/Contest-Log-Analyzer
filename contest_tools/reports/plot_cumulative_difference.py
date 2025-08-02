# Contest Log Analyzer/contest_tools/reports/plot_cumulative_difference.py
#
# Purpose: A plot report that generates a cumulative difference graph,
#          comparing two logs.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-02
# Version: 0.26.1-Beta
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

## [0.26.1-Beta] - 2025-08-02
### Fixed
# - Converted report_id, report_name, and report_type from @property methods
#   to simple class attributes to fix a bug in the report generation loop.

## [0.25.0-Beta] - 2025-08-01
### Changed
# - The report now uses the pre-aligned master time index to display the
#   entire contest period.

## [0.22.0-Beta] - 2025-07-31
### Changed
# - Implemented the boolean support properties, correctly identifying this
#   report as 'pairwise'.

## [0.15.0-Beta] - 2025-07-25
### Changed
# - Rewrote the report to use the new 'align_logs_by_time' shared helper
#   function, which corrects data alignment issues and simplifies the code.

## [0.14.0-Beta] - 2025-07-22
# - Initial release of the Cumulative Difference Plot report.
# - The bottom subplot now displays the cumulative difference for "S&P + Unknown"
#   QSOs/Points combined.
# - Added the band name as a second line to the main title of each plot.
### Fixed
# - Corrected a critical bug in the data aggregation logic that was causing
#   the difference plots to show incorrect values.

from typing import List
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import align_logs_by_time # Import the new helper

class Report(ContestReport):
    """
    Generates a three-subplot plot showing the cumulative difference in
    QSOs or Points between two logs.
    """
    report_id: str = "cumulative_difference_plots"
    report_name: str = "Cumulative Difference Plots"
    report_type: str = "plot"
    supports_pairwise = True
    
    def _generate_single_plot(self, output_path: str, band_filter: str, metric: str, master_index: pd.DatetimeIndex):
        """
        Helper function to generate a single cumulative difference plot.
        """
        log1, log2 = self.logs[0], self.logs[1]
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')

        value_column = 'QSOPoints' if metric == 'points' else 'Call'
        agg_func = 'sum' if metric == 'points' else 'count'
        
        # --- Data Preparation using the shared helper ---
        aligned_data = align_logs_by_time(
            logs=self.logs,
            value_column=value_column,
            agg_func=agg_func,
            master_index=master_index,
            band_filter=band_filter,
            time_unit='1h'
        )

        if len(aligned_data) < 2:
                print(f"  - Skipping {band_filter} difference plot: one or both logs have no QSOs on this band.")
                return None
                
        pt1_aligned = aligned_data[call1]
        pt2_aligned = aligned_data[call2]

        # --- Calculate Cumulative Differences ---
        run_diff = (pt1_aligned['Run'].cumsum() - pt2_aligned['Run'].cumsum())
        sp_unk_diff = (pt1_aligned['S&P+Unknown'].cumsum() - pt2_aligned['S&P+Unknown'].cumsum())
        overall_diff = run_diff + sp_unk_diff

        # --- Plotting ---
        sns.set_theme(style="whitegrid")
        fig = plt.figure(figsize=(12, 9))
        gs = fig.add_gridspec(5, 1)
        
        ax1 = fig.add_subplot(gs[0:3, 0])
        ax2 = fig.add_subplot(gs[3, 0], sharex=ax1)
        ax3 = fig.add_subplot(gs[4, 0], sharex=ax1)

        ax1.plot(overall_diff.index, overall_diff, marker='o', markersize=4)
        ax2.plot(run_diff.index, run_diff, marker='o', markersize=4, color='green')
        ax3.plot(sp_unk_diff.index, sp_unk_diff, marker='o', markersize=4, color='purple')

        # --- Formatting ---
        contest_name = log1.get_metadata().get('ContestName', '')
        year = log1.get_processed_data()['Date'].iloc[0].split('-')[0]
        metric_name = "Points" if metric == 'points' else "QSOs"
        band_text = "All Bands" if band_filter == "All" else f"{band_filter.replace('M', '')} Meters"
        
        main_title = f"{year} {contest_name} - Cumulative {metric_name} Difference\n{band_text}"
        sub_title = f"{call1} minus {call2}"
        
        fig.suptitle(main_title, fontsize=16, fontweight='bold')
        ax1.set_title(sub_title, fontsize=12)

        ax1.set_ylabel(f"Overall Diff ({metric_name})")
        ax2.set_ylabel(f"Run Diff")
        ax3.set_ylabel(f"S&P+Unk Diff")
        ax3.set_xlabel("Contest Time")

        for ax in [ax1, ax2, ax3]:
            ax.grid(True, which='both', linestyle='--')
            ax.axhline(0, color='black', linewidth=0.8, linestyle='-')
        
        plt.setp(ax1.get_xticklabels(), visible=False)
        plt.setp(ax2.get_xticklabels(), visible=False)
        fig.tight_layout(rect=[0, 0.03, 1, 0.93])

        # --- Save File ---
        os.makedirs(output_path, exist_ok=True)
        filename_band = band_filter.lower().replace('m', '')
        filename = f"diff_{metric}_{filename_band}_{call1}_vs_{call2}.png"
        filepath = os.path.join(output_path, filename)
        fig.savefig(filepath)
        plt.close(fig)

        return filepath

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Orchestrates the generation of all cumulative difference plots.
        """
        if len(self.logs) != 2:
            return "Error: The Cumulative Difference Plot report requires exactly two logs."

        log_manager = getattr(self.logs[0], '_log_manager_ref', None)
        if not log_manager or log_manager.master_time_index is None:
            return "Error: Master time index not available for plot report."
        master_index = log_manager.master_time_index

        metric = kwargs.get('metric', 'qsos')
        bands_to_plot = ['All', '160M', '80M', '40M', '20M', '15M', '10M']
        created_files = []
        
        for band in bands_to_plot:
            try:
                save_path = os.path.join(output_path, band) if band != "All" else output_path
                filepath = self._generate_single_plot(
                    output_path=save_path,
                    band_filter=band,
                    metric=metric,
                    master_index=master_index
                )
                if filepath:
                    created_files.append(filepath)
            except Exception as e:
                print(f"  - Failed to generate difference plot for {band}: {e}")

        if not created_files:
            return f"No difference plots were generated for metric '{metric}'."

        return f"Cumulative difference plots for {metric} saved to:\n" + "\n".join([f"  - {fp}" for fp in created_files])