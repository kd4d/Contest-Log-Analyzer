# contest_tools/reports/plot_comparative_run_sp.py
#
# Purpose: A plot report that generates a "paired timeline" chart, visualizing
#          the operating style (Run, S&P, or Mixed) of two operators over time.
#
# Author: Gemini AI
# Date: 2025-11-24
# Version: 1.0.0
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
# --- Revision History ---
# [1.0.0] - 2025-11-24
# Refactored to use MatrixAggregator (DAL).
# [0.90.0-Beta] - 2025-10-01
# Set new baseline version for release.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import os
import logging
import math
import itertools
from typing import List, Dict, Any

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import get_valid_dataframe, create_output_directory, save_debug_data
from ..data_aggregators.matrix_stats import MatrixAggregator

# Define the color scheme for the timeline blocks
ACTIVITY_COLORS = {
    'Run': '#FF4136',          # Red
    'S&P': '#2ECC40',          # Green
    'Mixed': '#FFDC00',        # Yellow
}

class Report(ContestReport):
    """
    Generates a "paired timeline" chart to visualize Run/S&P activity.
    """
    report_id: str = "comparative_run_sp_timeline"
    report_name: str = "Comparative Activity Timeline (Run/S&P)"
    report_type: str = "plot"
    supports_pairwise = True

    def _generate_plot_for_page(self, matrix_data: Dict, log1_meta: Dict, log2_meta: Dict, bands_on_page: List[str], output_path: str, page_title_suffix: str, page_file_suffix: str, mode_filter: str, **kwargs):
        """Helper to generate a single plot page using Matrix Data."""
        call1 = log1_meta.get('MyCall', 'Log1')
        call2 = log2_meta.get('MyCall', 'Log2')
        debug_data_flag = kwargs.get("debug_data", False)
        
        # Unpack Matrix Data
        time_bins_str = matrix_data['time_bins']
        time_bins = pd.to_datetime(time_bins_str)
        all_bands = matrix_data['bands']
        
        # --- Create figure with one subplot per band ---
        height = max(8.0, 1.5 * len(bands_on_page))
        fig, axes = plt.subplots(
            nrows=len(bands_on_page), 
            ncols=1, 
            figsize=(20, height), 
            sharex=True
        )
        if len(bands_on_page) == 1:
            axes = np.array([axes])

        plot_data_for_debug = {}

        for i, band in enumerate(bands_on_page):
            ax = axes[i]
            plot_data_for_debug[band] = {call1: {}, call2: {}}

            # --- Plot data for both callsigns on the same subplot (ax) ---
            for y_position, call in [(0.75, call1), (0.25, call2)]:
                
                # Retrieve pre-calculated grid from Aggregator
                try:
                    band_idx = all_bands.index(band)
                    activity_row = matrix_data['logs'][call]['activity_status'][band_idx]
                except (ValueError, KeyError):
                    activity_row = ['Inactive'] * len(time_bins)

                # Use ax.barh to draw the timeline
                # We iterate the activity row and plot 15min blocks
                for j, activity in enumerate(activity_row):
                    interval_start = time_bins[j]
                    
                    if call == call1: # Only save debug data once per interval
                        plot_data_for_debug[band][call][interval_start.isoformat()] = activity
                    
                    if activity != 'Inactive':
                        ax.barh(
                            y=y_position,
                            width=1/96, # Width of a 15-minute interval in days
                            height=0.5,
                            left=mdates.date2num(interval_start),
                            color=ACTIVITY_COLORS.get(activity, '#888888'),
                            edgecolor='none'
                        )
            
            # --- Formatting for each band's subplot ---
            ax.axhline(0.5, color='black', linewidth=0.8)
            ax.set_ylabel(band, rotation=0, ha='right', va='center', fontweight='bold', fontsize=12)
            ax.set_yticks([0.25, 0.75])
            ax.set_yticklabels([call2, call1])
            ax.tick_params(axis='y', length=0)
            ax.set_ylim(0, 1)
            ax.grid(False, axis='y') # Disable horizontal gridlines

            # Add hourly gridlines
            for ts in time_bins:
                if ts.minute == 0:
                    ax.axvline(x=mdates.date2num(ts), color='gray', linestyle=':', linewidth=0.75)

        # --- Overall Figure Formatting ---
        fig.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%H%M'))
        fig.gca().xaxis.set_major_locator(mdates.HourLocator(interval=3))
        plt.xticks(rotation=45, ha='right')
        
        # --- Set X-axis limits ---
        if not time_bins.empty:
            x_min = mdates.date2num(time_bins[0])
            x_max = mdates.date2num(time_bins[-1])
            axes[-1].set_xlim(x_min, x_max)

        # --- Title ---
        year = get_valid_dataframe(self.logs[0])['Date'].dropna().iloc[0].split('-')[0]
        contest_name = log1_meta.get('ContestName', '')
        event_id = log1_meta.get('EventID', '')
        
        mode_title_str = f" ({mode_filter})" if mode_filter else ""
        callsign_str = f"{call1} vs. {call2}"
        
        title_line1 = f"{self.report_name}{mode_title_str}{page_title_suffix}"
        title_line2 = f"{year} {event_id} {contest_name} - {callsign_str}".strip().replace("  ", " ")
        final_title = f"{title_line1}\n{title_line2}"
        fig.suptitle(final_title, fontsize=16, fontweight='bold')
        
        # --- Legend ---
        legend_handles = [
            mpatches.Patch(color=ACTIVITY_COLORS['Run'], label='Pure Run'),
            mpatches.Patch(color=ACTIVITY_COLORS['S&P'], label='Pure S&P'),
            mpatches.Patch(color=ACTIVITY_COLORS['Mixed'], label='Mixed / Unknown')
        ]
        fig.legend(handles=legend_handles, loc='upper right', ncol=3)
        fig.tight_layout(rect=[0, 0, 0.9, 0.9])

        # --- Save File ---
        mode_filename_str = f"_{mode_filter.lower()}" if mode_filter else ""
        filename = f"{self.report_id}{mode_filename_str}_{call1}_vs_{call2}{page_file_suffix}.png"
        filepath = os.path.join(output_path, filename)
        
        debug_filename = f"{self.report_id}{mode_filename_str}_{call1}_vs_{call2}{page_file_suffix}.txt"
        save_debug_data(debug_data_flag, output_path, plot_data_for_debug, custom_filename=debug_filename)
        
        fig.savefig(filepath)
        plt.close(fig)
        return filepath

    def generate(self, output_path: str, **kwargs) -> str:
        """Orchestrates the generation of the combined plot and per-mode plots."""
        if len(self.logs) != 2:
            return f"Error: Report '{self.report_name}' requires exactly two logs."

        BANDS_PER_PAGE = 8
        log1, log2 = self.logs[0], self.logs[1]
        created_files = []

        aggregator = MatrixAggregator(self.logs)

        # --- 1. Generate the main "All Modes" plot ---
        matrix_data_all = aggregator.get_matrix_data(bin_size='15min', mode_filter=None)
        
        filepath = self._run_plot_for_slice(matrix_data_all, log1, log2, output_path, BANDS_PER_PAGE, mode_filter=None, **kwargs)
        if filepath:
            created_files.append(filepath)
        
        # --- 2. Generate per-mode plots if necessary ---
        df1 = get_valid_dataframe(log1, include_dupes=False)
        df2 = get_valid_dataframe(log2, include_dupes=False)
        modes_present = pd.concat([df1['Mode'], df2['Mode']]).dropna().unique()

        if len(modes_present) > 1:
            for mode in ['CW', 'PH', 'DG']:
                if mode in modes_present:
                    matrix_data_mode = aggregator.get_matrix_data(bin_size='15min', mode_filter=mode)
                    
                    filepath = self._run_plot_for_slice(matrix_data_mode, log1, log2, output_path, BANDS_PER_PAGE, mode_filter=mode, **kwargs)
                    if filepath:
                        created_files.append(filepath)

        if not created_files:
            return f"Report '{self.report_name}' did not generate any files."
        return f"Report file(s) saved to:\n" + "\n".join([f"  - {fp}" for fp in created_files])

    def _run_plot_for_slice(self, matrix_data, log1, log2, output_path, bands_per_page, mode_filter, **kwargs):
        """Helper to run the paginated plot generation for a specific data slice (DAL-based)."""
        # Determine active bands from matrix data by checking counts?
        # Actually, matrix data returns sorted bands. We can check if a band is empty for BOTH logs.
        all_bands = matrix_data['bands']
        active_bands = []
        
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')

        for i, band in enumerate(all_bands):
            row1 = matrix_data['logs'][call1]['qso_counts'][i]
            row2 = matrix_data['logs'][call2]['qso_counts'][i]
            # Check sum of QSOs to determine activity
            if sum(row1) > 0 or sum(row2) > 0:
                active_bands.append(band)

        if not active_bands:
            return None

        num_pages = math.ceil(len(active_bands) / bands_per_page)
        
        for page_num in range(num_pages):
            start_index = page_num * bands_per_page
            end_index = start_index + bands_per_page
            bands_on_page = active_bands[start_index:end_index]
            
            page_title_suffix = f" (Page {page_num + 1}/{num_pages})" if num_pages > 1 else ""
            page_file_suffix = f"_Page_{page_num + 1}_of_{num_pages}" if num_pages > 1 else ""
            
            return self._generate_plot_for_page(
                matrix_data=matrix_data,
                log1_meta=log1.get_metadata(),
                log2_meta=log2.get_metadata(),
                bands_on_page=bands_on_page,
                output_path=output_path,
                page_title_suffix=page_title_suffix,
                page_file_suffix=page_file_suffix.replace('/', '_'),
                mode_filter=mode_filter,
                **kwargs
            )