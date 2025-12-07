# contest_tools/reports/chart_comparative_activity_butterfly.py
#
# Purpose: Generates a comparative 'Butterfly' chart (stacked diverging bars)
#          visualizing Run vs S&P activity for two stations per band.
#
# Author: Gemini AI (Builder)
# Date: 2025-12-06
# Version: 1.0.2
#
# Copyright (c) 2025 Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# --- Revision History ---
# [1.0.2] - 2025-12-06
# - Fixed output directory pathing issue where charts were saved to a nested
#   'charts/charts' directory. Now saves directly to the provided output_path.
# [1.0.1] - 2025-12-06
# - Updated color palette to Blue (S&P) / Green (Run) / Grey (Unknown) to match
#   standard breakdown charts.
# [1.0.0] - 2025-12-06
# - Initial creation implementing the Stacked Butterfly Chart.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os
import logging
from typing import List, Dict, Any, Optional
from math import ceil

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ..data_aggregators.matrix_stats import MatrixAggregator
from ._report_utils import create_output_directory, _sanitize_filename_part
from ..styles.mpl_style_manager import MPLStyleManager

class Report(ContestReport):
    report_id = "chart_comparative_activity_butterfly"
    report_name = "Comparative Activity Butterfly Chart"
    report_type = "chart"
    supports_single = False
    supports_pairwise = True
    supports_multi = False

    def __init__(self, logs: List[ContestLog]):
        super().__init__(logs)
        
        # Load authoritative colors from StyleManager
        # Run=Green (#2ca02c), S&P=Blue (#1f77b4), Mixed/Unk=Gray (#7f7f7f)
        style_colors = MPLStyleManager.get_qso_mode_colors()
        
        self.COLORS = {
            'Run': style_colors.get('Run', '#2ca02c'),
            'S&P': style_colors.get('S&P', '#1f77b4'),
            'Unknown': style_colors.get('Mixed/Unk', '#7f7f7f')
        }

    def generate(self, output_path: str, **kwargs) -> str:
        if len(self.logs) != 2:
            return "Skipping: Butterfly chart requires exactly 2 logs."

        call1 = self.logs[0].get_metadata().get('MyCall', 'LOG1')
        call2 = self.logs[1].get_metadata().get('MyCall', 'LOG2')

        # 1. Fetch Data
        aggregator = MatrixAggregator(self.logs)
        data = aggregator.get_stacked_matrix_data(bin_size='60min')
        
        bands = data['bands']
        time_bins = [pd.Timestamp(t) for t in data['time_bins']]
        
        if not bands or not time_bins:
            return "No data available to plot."

        # 2. Setup Output
        # Corrected: Do not append "charts" again; assume output_path is correct.
        charts_dir = output_path
        create_output_directory(charts_dir)

        # 3. Pagination Logic (Max 6 bands per page)
        BANDS_PER_PAGE = 6
        num_pages = ceil(len(bands) / BANDS_PER_PAGE)

        saved_files = []

        for page_idx in range(num_pages):
            start_idx = page_idx * BANDS_PER_PAGE
            end_idx = min(start_idx + BANDS_PER_PAGE, len(bands))
            page_bands = bands[start_idx:end_idx]
            
            filename = self._plot_page(
                data, time_bins, page_bands, call1, call2, 
                page_idx + 1, num_pages, charts_dir
            )
            if filename:
                saved_files.append(filename)

        return f"Generated {len(saved_files)} butterfly chart(s) in {charts_dir}"

    def _plot_page(self, data: Dict[str, Any], time_bins: List[pd.Timestamp], 
                   bands: List[str], call1: str, call2: str, 
                   page_num: int, total_pages: int, output_dir: str) -> Optional[str]:
        
        num_plots = len(bands)
        if num_plots == 0:
            return None

        # Dynamic figure size based on number of bands
        fig, axes = plt.subplots(num_plots, 1, figsize=(12, 3 * num_plots), sharex=True)
        if num_plots == 1:
            axes = [axes] # Ensure iterable

        # Metadata for Titles
        meta = self.logs[0].get_metadata()
        year = meta.get('Year', '')
        contest = meta.get('ContestName', '')
        
        # Super Title
        title_line1 = f"Comparative Activity Breakdown (Hrly)"
        title_line2 = f"{year} {contest} - {call1} (Top) vs {call2} (Bottom)"
        if total_pages > 1:
            title_line2 += f" - Page {page_num} of {total_pages}"
        
        fig.suptitle(f"{title_line1}\n{title_line2}", fontsize=16, fontweight='bold', y=0.98 if num_plots > 2 else 1.05)

        # Iterate Bands
        for ax, band in zip(axes, bands):
            # --- Extract Data for this Band ---
            # Log 1 (Positive)
            l1_run = np.array(data['logs'][call1][band]['Run'])
            l1_sp = np.array(data['logs'][call1][band]['S&P'])
            l1_unk = np.array(data['logs'][call1][band]['Unknown'])
            
            # Log 2 (Negative)
            l2_run = np.array(data['logs'][call2][band]['Run'])
            l2_sp = np.array(data['logs'][call2][band]['S&P'])
            l2_unk = np.array(data['logs'][call2][band]['Unknown'])

            # --- Plot Log 1 (Top) ---
            width = 0.04 # Width in days (approx 1 hour)
            
            # Note: Order is Run (Green), S&P (Blue), Unknown (Gray)
            ax.bar(time_bins, l1_run, width=width, color=self.COLORS['Run'], label='Run', align='edge')
            ax.bar(time_bins, l1_sp, bottom=l1_run, width=width, color=self.COLORS['S&P'], label='S&P', align='edge')
            ax.bar(time_bins, l1_unk, bottom=l1_run + l1_sp, width=width, color=self.COLORS['Unknown'], label='Unknown', align='edge')

            # --- Plot Log 2 (Bottom - Negative) ---
            # To stack downwards:
            # First bar starts at 0, goes to -val
            # Second bar starts at -val1, goes to -(val1+val2)
            
            ax.bar(time_bins, -l2_run, width=width, color=self.COLORS['Run'], align='edge')
            ax.bar(time_bins, -l2_sp, bottom=-l2_run, width=width, color=self.COLORS['S&P'], align='edge')
            ax.bar(time_bins, -l2_unk, bottom=-(l2_run + l2_sp), width=width, color=self.COLORS['Unknown'], align='edge')

            # --- Styling ---
            ax.axhline(0, color='black', linewidth=1.0)
            ax.grid(True, axis='y', linestyle='--', alpha=0.5)
            ax.set_ylabel(f"{band}\nQSOs/Hr", fontweight='bold')
            
            # Y-Axis Formatting (Absolute values)
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'{int(abs(x))}'))

            # Dynamic Y-Limits
            # Find max absolute height in either direction
            max_h1 = np.max(l1_run + l1_sp + l1_unk) if len(l1_run) > 0 else 0
            max_h2 = np.max(l2_run + l2_sp + l2_unk) if len(l2_run) > 0 else 0
            limit = max(max_h1, max_h2)
            
            # Round up to nearest 10
            limit = ceil((limit + 1) / 10) * 10
            ax.set_ylim(-limit, limit)

        # X-Axis Formatting (Only on bottom plot due to sharex)
        axes[-1].xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))
        axes[-1].set_xlabel("Time (UTC)")
        fig.autofmt_xdate()

        # Legend (Single legend for the page)
        # Create proxy artists for legend
        handles = [
            plt.Rectangle((0,0),1,1, color=self.COLORS['Run']),
            plt.Rectangle((0,0),1,1, color=self.COLORS['S&P']),
            plt.Rectangle((0,0),1,1, color=self.COLORS['Unknown'])
        ]
        labels = ["Run", "S&P", "Unknown"]
        fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.95 if num_plots > 2 else 0.90), ncol=3, frameon=False)

        plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust for suptitle/legend

        # Save
        filename = f"chart_comparative_activity_butterfly_{_sanitize_filename_part(call1)}_vs_{_sanitize_filename_part(call2)}_p{page_num}.png"
        filepath = os.path.join(output_dir, filename)
        
        try:
            fig.savefig(filepath)
            plt.close(fig)
            return filename
        except Exception as e:
            logging.error(f"Error saving butterfly chart page {page_num}: {e}")
            plt.close(fig)
            return None