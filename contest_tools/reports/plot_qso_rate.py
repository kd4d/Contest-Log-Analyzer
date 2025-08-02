# Contest Log Analyzer/contest_tools/reports/plot_qso_rate.py
#
# Purpose: A plot report that generates a QSO rate graph for all bands
#          and for each individual band by calling a shared utility.
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
#   report as 'multi'.

## [0.21.3-Beta] - 2025-07-28
### Fixed
# - The inset summary table now has a solid background color, which makes it
#   opaque and prevents the plot's grid lines from showing through.

## [0.21.2-Beta] - 2025-07-27
### Added
# - Added a summary of final QSO totals as an inset table on the plot itself,
#   placed in the bottom-right corner for better readability.

## [0.21.1-Beta] - 2025-07-27
### Reverted
# - Reverted the addition of the summary table to the bottom of the plot.

## [0.21.0-Beta] - 2025-07-27
### Added
# - Added a summary table to the bottom of the plot showing the final
#   total, Run, S&P, and Unknown QSO counts for each station.
### Changed
# - Adjusted the plot layout to accommodate the new summary table.

## [0.15.0-Beta] - 2025-07-26
### Fixed
# - Corrected the logic to use 'count' instead of 'sum' for the aggregation
#   function, ensuring that QSO rates are plotted correctly.

from typing import List
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import align_logs_by_time # Import the shared helper

class Report(ContestReport):
    """
    Generates a series of plots comparing QSO rates: one for all bands
    combined, and one for each individual contest band.
    """
    report_id: str = "qso_rate_plots"
    report_name: str = "QSO Rate Comparison Plots"
    report_type: str = "plot"
    supports_multi = True
    
    def _generate_single_plot(self, output_path: str, include_dupes: bool, band_filter: str, master_index: pd.DatetimeIndex) -> str:
        """
        Helper function to generate a single QSO rate plot for a specific band.
        """
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(12, 7))

        # --- Data Preparation using the shared helper ---
        aligned_data = align_logs_by_time(
            logs=self.logs,
            value_column='Call',
            agg_func='count', # Use 'count' for QSO rate
            master_index=master_index,
            band_filter=band_filter,
            time_unit='10min'
        )
        
        if not aligned_data:
                print(f"  - Skipping {band_filter} QSO rate plot: no logs have QSOs on this band.")
                return None

        # --- Plotting ---
        summary_data = []
        row_labels = []
        for callsign, df_aligned in aligned_data.items():
            cumulative_qsos = df_aligned['Overall'].cumsum()
            ax.plot(cumulative_qsos.index, cumulative_qsos, marker='o', linestyle='-', markersize=4, label=callsign)
            
            # --- Calculate Totals for Summary Table ---
            row_labels.append(callsign)
            summary_data.append([
                int(df_aligned['Overall'].sum()),
                int(df_aligned['Run'].sum()),
                int(df_aligned['S&P'].sum()),
                int(df_aligned['Unknown'].sum())
            ])

        # --- Formatting ---
        first_log_meta = self.logs[0].get_metadata()
        contest_name = first_log_meta.get('ContestName', '')
        year = self.logs[0].get_processed_data()['Date'].iloc[0].split('-')[0]
        
        main_title = f"{year} {contest_name} QSO Rate Comparison"
        band_text = "All Bands" if band_filter == "All" else f"{band_filter.replace('M', '')} Meters"
        dupe_text = "(Includes Dupes)" if include_dupes else "(Does Not Include Dupes)"
        sub_title = f"{band_text} - {dupe_text}"

        fig.suptitle(main_title, fontsize=16, fontweight='bold')
        ax.set_title(sub_title, fontsize=12)
        
        ax.set_xlabel("Contest Time")
        ax.set_ylabel("Total QSOs")
        ax.legend()
        ax.grid(True)
        
        # --- Add Inset Summary Table ---
        col_labels = ['Total', 'Run', 'S&P', 'Unk']
        table = ax.table(cellText=summary_data,
                            rowLabels=row_labels,
                            colLabels=col_labels,
                            loc='lower right',
                            cellLoc='center',
                            bbox=[0.75, 0.05, 0.2, 0.25]) # Position [left, bottom, width, height]
        
        # Set face color for all cells to make the table opaque
        table.set_alpha(0.9)
        for key, cell in table.get_celld().items():
            cell.set_facecolor('white')

        fig.tight_layout(rect=[0, 0.03, 1, 0.95])

        # --- Save File ---
        os.makedirs(output_path, exist_ok=True)
        filename_band = band_filter.lower().replace('m', '')
        filename = f"qso_rate_{filename_band}_plot.png"
        filepath = os.path.join(output_path, filename)
        fig.savefig(filepath)
        plt.close(fig)

        return filepath

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Orchestrates the generation of all QSO rate plots.
        """
        log_manager = getattr(self.logs[0], '_log_manager_ref', None)
        if not log_manager or log_manager.master_time_index is None:
            return "Error: Master time index not available for plot report."
        master_index = log_manager.master_time_index

        include_dupes = kwargs.get('include_dupes', False)
        bands_to_plot = ['All', '160M', '80M', '40M', '20M', '15M', '10M']
        created_files = []
        
        for band in bands_to_plot:
            try:
                save_path = os.path.join(output_path, band) if band != "All" else output_path
                filepath = self._generate_single_plot(
                    output_path=save_path,
                    include_dupes=include_dupes,
                    band_filter=band,
                    master_index=master_index
                )
                if filepath:
                    created_files.append(filepath)
            except Exception as e:
                print(f"  - Failed to generate QSO rate plot for {band}: {e}")

        if not created_files:
            return "No QSO rate plots were generated."

        return "QSO rate plots saved to:\n" + "\n".join([f"  - {fp}" for fp in created_files])