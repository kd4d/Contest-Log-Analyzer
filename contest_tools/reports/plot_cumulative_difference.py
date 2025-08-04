# Contest Log Analyzer/contest_tools/reports/plot_cumulative_difference.py
#
# Purpose: A plot report that generates a cumulative difference graph,
#          comparing two logs.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-04
# Version: 0.26.4-Beta
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
## [0.26.4-Beta] - 2025-08-04
### Fixed
# - The report no longer generates redundant, per-band plots for single-band contests.
## [0.26.3-Beta] - 2025-08-04
### Changed
# - Simplified the report to work with pre-aligned dataframes, removing
#   all internal time-alignment logic to align with the new architecture.
from typing import List
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

from ..contest_log import ContestLog
from .report_interface import ContestReport

class Report(ContestReport):
    """
    Generates a three-subplot plot showing the cumulative difference in
    QSOs or Points between two logs.
    """
    report_id: str = "cumulative_difference_plots"
    report_name: str = "Cumulative Difference Plots"
    report_type: str = "plot"
    supports_pairwise = True
    
    def _prepare_data_for_plot(self, log: ContestLog, value_column: str, agg_func: str, band_filter: str) -> pd.DataFrame:
        """
        Prepares a single log's data for plotting by grouping and aggregating.
        """
        df = log.get_processed_data()[log.get_processed_data()['Dupe'] == False]
        
        if band_filter != "All":
            df = df[df['Band'] == band_filter]

        if df.empty:
            return pd.DataFrame(columns=['Run', 'S&P+Unknown'])

        df_cleaned = df.dropna(subset=['Datetime', 'Run', value_column])
        rate_data = df_cleaned.groupby([df_cleaned['Datetime'].dt.floor('h'), 'Run'])[value_column].agg(agg_func).unstack(fill_value=0)

        for col in ['Run', 'S&P', 'Unknown']:
            if col not in rate_data.columns:
                rate_data[col] = 0
        
        rate_data['S&P+Unknown'] = rate_data['S&P'] + rate_data['Unknown']
        
        return rate_data[['Run', 'S&P+Unknown']]


    def _generate_single_plot(self, output_path: str, band_filter: str, metric: str):
        """
        Helper function to generate a single cumulative difference plot.
        """
        log1, log2 = self.logs[0], self.logs[1]
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')

        value_column = 'QSOPoints' if metric == 'points' else 'Call'
        agg_func = 'sum' if metric == 'points' else 'count'
        
        data1 = self._prepare_data_for_plot(log1, value_column, agg_func, band_filter)
        data2 = self._prepare_data_for_plot(log2, value_column, agg_func, band_filter)
        
        master_index = data1.index.union(data2.index)
        
        data1 = data1.reindex(master_index, fill_value=0)
        data2 = data2.reindex(master_index, fill_value=0)

        if data1.empty and data2.empty:
            print(f"  - Skipping {band_filter} difference plot: no data.")
            return None

        # --- Calculate Cumulative Differences ---
        run_diff = (data1['Run'].cumsum() - data2['Run'].cumsum())
        sp_unk_diff = (data1['S&P+Unknown'].cumsum() - data2['S&P+Unknown'].cumsum())
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
        year = log1.get_processed_data()['Date'].dropna().iloc[0].split('-')[0] if not log1.get_processed_data().empty else "----"
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

        metric = kwargs.get('metric', 'qsos')
        
        bands = self.logs[0].contest_definition.valid_bands
        is_single_band = len(bands) == 1
        bands_to_plot = ['All'] if is_single_band else ['All'] + bands
        
        created_files = []
        
        for band in bands_to_plot:
            try:
                save_path = os.path.join(output_path, band) if band != "All" else output_path
                filepath = self._generate_single_plot(
                    output_path=save_path,
                    band_filter=band,
                    metric=metric
                )
                if filepath:
                    created_files.append(filepath)
            except Exception as e:
                print(f"  - Failed to generate difference plot for {band}: {e}")

        if not created_files:
            return f"No difference plots were generated for metric '{metric}'."

        return f"Cumulative difference plots for {metric} saved to:\n" + "\n".join([f"  - {fp}" for fp in created_files])