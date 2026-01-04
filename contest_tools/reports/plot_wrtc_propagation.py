# contest_tools/reports/plot_wrtc_propagation.py
#
# Purpose: A plot report that generates a visual prototype for one frame
#          of the proposed WRTC propagation animation. It creates a side-by-side
#          butterfly chart comparing two logs' hourly QSO data, broken down by
#          band, continent, and mode for a single, peak-activity hour.
#
# Author: Gemini AI
# Date: 2026-01-03
# Version: 0.151.4-Beta
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
# [0.151.4-Beta] - 2026-01-03
# - Refactored imports to use contest_tools.utils.report_utils to break circular dependency.
# [0.92.7-Beta] - 2025-10-12
# - Changed figure height to 11.04 inches to produce a 2000x1104 pixel
#   image, resolving the ffmpeg macro_block_size warning.
# [0.92.6-Beta] - 2025-10-12
# - Fixed AttributeError by changing `set_ticks` to the correct `set_xticks` method.
# [0.92.5-Beta] - 2025-10-12
# - Fixed UserWarning by explicitly setting fixed ticks before applying custom labels.
# [0.92.2-Beta] - 2025-10-12
# - Fixed x-axis labels to show absolute values for QSO counts instead of negative numbers.
# [0.92.1-Beta] - 2025-10-12
# - Set `is_specialized = True` to make this an opt-in report.
# [0.92.0-Beta] - 2025-10-12
# - Initial creation of the live-data report based on the
#   prototype_wrtc_propagation.py script, serving as the proof-of-concept
#   for the new data aggregation layer.
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec
import pandas as pd
import os
import logging
from typing import List, Dict, Any

from ..contest_log import ContestLog
from .report_interface import ContestReport
from contest_tools.utils.report_utils import get_valid_dataframe, create_output_directory, save_debug_data
from ..data_aggregators import propagation_aggregator

class Report(ContestReport):
    report_id: str = "wrtc_propagation"
    report_name: str = "WRTC Propagation by Continent"
    report_type: str = "plot"
    is_specialized = True
    supports_pairwise = True

    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report by finding the peak activity hour and creating
        a propagation chart for that hour.
        """
        if len(self.logs) != 2:
            return f"Report '{self.report_name}' requires exactly two logs."

        log1, log2 = self.logs[0], self.logs[1]
        df1 = get_valid_dataframe(log1, include_dupes=False)
        df2 = get_valid_dataframe(log2, include_dupes=False)

        if df1.empty or df2.empty:
            return f"Skipping '{self.report_name}': At least one log has no valid QSO data."

        # --- Find the hour with the most combined activity ---
        combined_df = pd.concat([df1, df2])
        hourly_counts = combined_df.set_index('Datetime').resample('h').size()
        if hourly_counts.empty:
            return f"Skipping '{self.report_name}': No hourly data to process."

        peak_hour_timestamp = hourly_counts.idxmax()
        
        log_manager = getattr(log1, '_log_manager_ref', None)
        master_index = getattr(log_manager, 'master_time_index', None)
        if master_index is None:
            return "Error: Master time index not available. Cannot generate report."

        # Find the 1-based index of the peak hour
        try:
            peak_hour_index = master_index.get_loc(peak_hour_timestamp) + 1
        except KeyError:
            logging.warning(f"Peak hour {peak_hour_timestamp} not in master index. Defaulting to hour 1.")
            peak_hour_index = 1
            
        # --- Call the aggregator to get data for the peak hour ---
        propagation_data = propagation_aggregator.generate_propagation_data(self.logs, peak_hour_index)

        if not propagation_data:
            return f"Skipping '{self.report_name}': No data aggregated for the peak activity hour."

        # --- Save debug data ---
        if kwargs.get("debug_data", False):
            all_calls = sorted([log.get_metadata().get('MyCall') for log in self.logs])
            debug_filename = f"{self.report_id}_{'_vs_'.join(all_calls)}.txt"
            save_debug_data(True, output_path, propagation_data, custom_filename=debug_filename)
        
        # --- Generate the plot using the prototype's logic ---
        filepath = self._create_propagation_chart(propagation_data, peak_hour_index, len(master_index), output_path)

        if filepath:
            return f"Plot report saved to: {filepath}"
        else:
            return f"Failed to generate plot for report '{self.report_name}'."

    def _create_propagation_chart(self, propagation_data: Dict, hour_num: int, total_hours: int, output_path: str) -> str:
        """Generates and saves the side-by-side butterfly chart."""
        
        # --- Extract data from the aggregator dictionary ---
        DATA = propagation_data.get('data', {})
        BANDS = propagation_data.get('bands', [])
        CONTINENTS = propagation_data.get('continents', [])
        MODES = propagation_data.get('modes', [])
        CALLS = propagation_data.get('calls', [])
        
        if not all([DATA, BANDS, CONTINENTS, MODES, CALLS]):
            logging.warning("Propagation data from aggregator is incomplete. Cannot generate plot.")
            return ""

        # --- Color Mapping for Continents ---
        COLORS = plt.get_cmap('viridis', len(CONTINENTS))
        CONTINENT_COLORS = {cont: COLORS(i) for i, cont in enumerate(CONTINENTS)}
        
        fig = plt.figure(figsize=(20, 11.04))

        # --- Main 3-Row GridSpec Layout (Title, Plots, Legend) ---
        gs_main = gridspec.GridSpec(
            3, 1, figure=fig, height_ratios=[1, 10, 1.5],
            top=0.93, bottom=0.12, hspace=0.3
        )

        # --- Create zones for title, plots, and legend ---
        ax_title = fig.add_subplot(gs_main[0])
        ax_legend = fig.add_subplot(gs_main[2])
        ax_title.axis('off')
        ax_legend.axis('off')

        # --- Nested GridSpec for the two butterfly plots ---
        gs_plots = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=gs_main[1], wspace=0.1)
        ax_cw = fig.add_subplot(gs_plots[0, 0])
        ax_ph = fig.add_subplot(gs_plots[0, 1], sharey=ax_cw)
        axes = {'CW': ax_cw, 'PH': ax_ph}
        plt.setp(ax_ph.get_yticklabels(), visible=False)

        max_qso_rate = 0
        for mode in MODES:
            for band in BANDS:
                for call in CALLS:
                    max_qso_rate = max(max_qso_rate, sum(DATA.get(call, {}).get(mode, {}).get(band, {}).values()))
        
        axis_limit = (max_qso_rate // 10 + 1) * 10 if max_qso_rate > 0 else 10
        bands_for_plotting = list(reversed(self.logs[0].contest_definition.valid_bands))

        for mode in ['CW', 'PH']: # Always plot both axes for consistent layout
            ax = axes.get(mode)
            ax.set_title(mode, fontsize=16, fontweight='bold')

            for j, band in enumerate(bands_for_plotting):
                if mode in MODES and band in BANDS:
                    left_pos = 0
                    for continent in CONTINENTS:
                        qso_count = DATA.get(CALLS[0], {}).get(mode, {}).get(band, {}).get(continent, 0)
                        if qso_count > 0:
                            ax.barh(j, qso_count, left=left_pos, color=CONTINENT_COLORS.get(continent, 'gray'), edgecolor='white', height=0.8)
                            left_pos += qso_count

                    left_neg = 0
                    for continent in CONTINENTS:
                        qso_count = DATA.get(CALLS[1], {}).get(mode, {}).get(band, {}).get(continent, 0)
                        if qso_count > 0:
                            ax.barh(j, -qso_count, left=left_neg, color=CONTINENT_COLORS.get(continent, 'gray'), edgecolor='white', height=0.8)
                            left_neg -= qso_count
            
            ax.axvline(0, color='black', linewidth=1.5)
            ax.set_yticks(np.arange(len(bands_for_plotting)))
            ax.set_yticklabels(bands_for_plotting, fontsize=12)
            ax.set_xlim(-axis_limit, axis_limit)

            ticks = ax.get_xticks()
            ax.set_xticks(ticks) # Lock in the ticks to prevent UserWarning
            ax.set_xticklabels([int(abs(tick)) for tick in ticks])

            ax.grid(axis='x', linestyle='--', alpha=0.6)

            ax.text(0.02, 1.02, CALLS[0], transform=ax.transAxes, ha='left', fontsize=12, fontweight='bold')
            ax.text(0.98, 1.02, CALLS[1], transform=ax.transAxes, ha='right', fontsize=12, fontweight='bold')
            ax.set_xlabel("QSO Count for the Hour")

        # --- Overall Figure Title and Legend ---
        metadata = self.logs[0].get_metadata()
        year = get_valid_dataframe(self.logs[0])['Date'].dropna().iloc[0].split('-')[0]
        contest_name = metadata.get('ContestName', '')
        event_id = metadata.get('EventID', '')
        
        title_line1 = f"{self.report_name} (Hour {hour_num}/{total_hours})"
        title_line2 = f"{year} {event_id} {contest_name} - {CALLS[0]} vs. {CALLS[1]}".strip().replace("  ", " ")
        ax_title.text(0.5, 0.5, f"{title_line1}\n{title_line2}", ha='center', va='center', fontsize=22, fontweight='bold', wrap=True)
        
        legend_patches = [plt.Rectangle((0,0),1,1, color=CONTINENT_COLORS.get(c, 'gray'), label=c) for c in CONTINENTS]
        ax_legend.legend(handles=legend_patches, loc='center', ncol=len(CONTINENTS), title="Continents", fontsize='large', frameon=False)

        # --- Save Plot ---
        create_output_directory(output_path)
        filename = f"{self.report_id}_{'_vs_'.join(sorted(CALLS))}.png"
        filepath = os.path.join(output_path, filename)

        try:
            plt.savefig(filepath)
            return filepath
        except Exception as e:
            logging.error(f"Error saving plot: {e}")
            return ""
        finally:
            plt.close(fig)