# Contest Log Analyzer/contest_tools/reports/plot_cumulative_difference.py
#
# Purpose: A plot report that generates a cumulative difference graph,
#          comparing two logs.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-22
# Version: 0.14.0-Beta
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

## [0.14.0-Beta] - 2025-07-22
# - Initial release of the Cumulative Difference Plot report.

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
    @property
    def report_id(self) -> str:
        return "cumulative_difference_plots"

    @property
    def report_name(self) -> str:
        return "Cumulative Difference Plots"

    @property
    def report_type(self) -> str:
        return "plot"

    def _generate_single_plot(self, output_path: str, band_filter: str, metric: str, **kwargs):
        """
        Helper function to generate a single cumulative difference plot.
        """
        log1, log2 = self.logs[0], self.logs[1]
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')

        # Determine which column to use for the metric
        value_column = 'QSOPoints' if metric == 'points' else 'Call'
        agg_func = 'sum' if metric == 'points' else 'count'
        
        # --- Data Preparation ---
        dfs = []
        for log in [log1, log2]:
            df = log.get_processed_data()
            df = df[df['Dupe'] == False].copy()
            if band_filter != "All":
                df = df[df['Band'] == band_filter]
            dfs.append(df)
        
        df1, df2 = dfs
        
        if df1.empty or df2.empty:
            print(f"  - Skipping {band_filter} difference plot: one or both logs have no QSOs on this band.")
            return None

        # Create pivot tables for each log to get hourly rates for Run/S&P
        pt1 = df1.pivot_table(index='Datetime', columns='Run', values=value_column, aggfunc=agg_func).resample('1H').sum().fillna(0)
        pt2 = df2.pivot_table(index='Datetime', columns='Run', values=value_column, aggfunc=agg_func).resample('1H').sum().fillna(0)

        # Ensure both tables have 'Run' and 'S&P' columns
        for col in ['Run', 'S&P']:
            if col not in pt1.columns: pt1[col] = 0
            if col not in pt2.columns: pt2[col] = 0
            
        # Combine the tables and calculate the hourly difference
        diff_df = pt1.subtract(pt2, fill_value=0)
        
        # Calculate cumulative differences
        diff_df['Run_Cum'] = diff_df['Run'].cumsum()
        diff_df['S&P_Cum'] = diff_df['S&P'].cumsum()
        diff_df['Overall_Cum'] = (diff_df['Run'] + diff_df['S&P']).cumsum()

        # --- Plotting ---
        sns.set_theme(style="whitegrid")
        fig = plt.figure(figsize=(12, 9))
        gs = fig.add_gridspec(5, 1)
        
        ax1 = fig.add_subplot(gs[0:3, 0])
        ax2 = fig.add_subplot(gs[3, 0], sharex=ax1)
        ax3 = fig.add_subplot(gs[4, 0], sharex=ax1)

        # Plot the data
        ax1.plot(diff_df.index, diff_df['Overall_Cum'], marker='o', markersize=4)
        ax2.plot(diff_df.index, diff_df['Run_Cum'], marker='o', markersize=4, color='green')
        ax3.plot(diff_df.index, diff_df['S&P_Cum'], marker='o', markersize=4, color='purple')

        # --- Formatting ---
        contest_name = log1.get_metadata().get('ContestName', '')
        year = log1.get_processed_data()['Date'].iloc[0].split('-')[0]
        metric_name = "Points" if metric == 'points' else "QSOs"
        
        main_title = f"{year} {contest_name} - Cumulative {metric_name} Difference"
        sub_title = f"{call1} minus {call2}"
        
        fig.suptitle(main_title, fontsize=16, fontweight='bold')
        ax1.set_title(sub_title, fontsize=12)

        ax1.set_ylabel(f"Overall Diff ({metric_name})")
        ax2.set_ylabel(f"Run Diff")
        ax3.set_ylabel(f"S&P Diff")
        ax3.set_xlabel("Contest Time")

        for ax in [ax1, ax2, ax3]:
            ax.grid(True, which='both', linestyle='--')
            ax.axhline(0, color='black', linewidth=0.8, linestyle='-') # Add a zero line
        
        plt.setp(ax1.get_xticklabels(), visible=False)
        plt.setp(ax2.get_xticklabels(), visible=False)
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])

        # --- Save File ---
        os.makedirs(output_path, exist_ok=True)
        filename_band = band_filter.lower().replace('m', '')
        filename = f"diff_{metric}_{filename_band}_plot.png"
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

        metric = kwargs.get('metric', 'qsos') # Default to QSOs
        bands_to_plot = ['All', '160M', '80M', '40M', '20M', '15M', '10M']
        created_files = []
        
        for band in bands_to_plot:
            try:
                save_path = os.path.join(output_path, band) if band != "All" else output_path
                filepath = self._generate_single_plot(
                    output_path=save_path,
                    band_filter=band,
                    metric=metric,
                    **kwargs
                )
                if filepath:
                    created_files.append(filepath)
            except Exception as e:
                print(f"  - Failed to generate difference plot for {band}: {e}")

        if not created_files:
            return f"No difference plots were generated for metric '{metric}'."

        return f"Cumulative difference plots saved to the 'plots' directory and its subdirectories."
