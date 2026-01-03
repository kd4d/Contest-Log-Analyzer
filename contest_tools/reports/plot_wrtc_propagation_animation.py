# contest_tools/reports/plot_wrtc_propagation_animation.py
#
# Purpose: A plot report that generates an animation of the WRTC propagation
#          analysis, creating a side-by-side butterfly chart for each hour of
#          the contest.
#
# Author: Gemini AI
# Date: 2026-01-01
# Version: 0.151.1-Beta
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
# [0.151.1-Beta] - 2026-01-01
# - Repair import path for report_utils to fix circular dependency.
# [0.151.0-Beta] - 2026-01-01
# - Refactored imports to use `contest_tools.utils.report_utils` to break circular dependency.
# [0.92.7-Beta] - 2025-10-12
# - Changed figure height to 11.04 inches to produce a 2000x1104 pixel
#   image, resolving the ffmpeg macro_block_size warning.
# [0.92.6-Beta] - 2025-10-12
# - Fixed AttributeError by changing `set_ticks` to the correct `set_xticks` method.
# [0.92.5-Beta] - 2025-10-12
# - Fixed UserWarning by explicitly setting fixed ticks before applying custom labels.
# [0.92.4-Beta] - 2025-10-12
# - Modified report to save individual animation frames to a permanent
#   `propagation` subdirectory instead of deleting them.
# [0.92.3-Beta] - 2025-10-12
# - Initial creation of the animation report based on the static
#   wrtc_propagation plot.

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec
import pandas as pd
import os
import logging
import imageio.v2 as imageio
from typing import List, Dict, Any

from ..contest_log import ContestLog
from .report_interface import ContestReport
from contest_tools.utils.report_utils import get_valid_dataframe, create_output_directory, save_debug_data
from ..data_aggregators import propagation_aggregator

class Report(ContestReport):
    report_id: str = "wrtc_propagation_animation"
    report_name: str = "WRTC Propagation Animation"
    report_type: str = "animation"
    is_specialized = True
    supports_pairwise = True

    # --- Configuration ---
    FPS = 10
    FRAME_DURATION_SECONDS = 2
    LAST_FRAME_DURATION_SECONDS = 30
    
    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the animation by creating a chart for each hour of the
        contest and compiling them into a video.
        """
        if len(self.logs) != 2:
            return f"Report '{self.report_name}' requires exactly two logs."
        
        log1, log2 = self.logs[0], self.logs[1]

        log_manager = getattr(log1, '_log_manager_ref', None)
        master_index = getattr(log_manager, 'master_time_index', None)
        if master_index is None:
            return "Error: Master time index not available. Cannot generate animation."

        frame_dir = os.path.join(output_path, "propagation")
        create_output_directory(frame_dir)
        logging.info(f"Generating {len(master_index)} frames in: {frame_dir}")
        
        try:
            for i, _ in enumerate(master_index):
                hour_index = i + 1
                propagation_data = propagation_aggregator.generate_propagation_data(self.logs, hour_index)
                
                # Save debug data for this frame if enabled
                if kwargs.get("debug_data", False) and propagation_data:
                    all_calls = sorted([log.get_metadata().get('MyCall') for log in self.logs])
                    debug_filename = f"{self.report_id}_{'_vs_'.join(all_calls)}_frame_{i:03d}.txt"
                    save_debug_data(True, output_path, propagation_data, custom_filename=debug_filename)
                
                frame_path = os.path.join(frame_dir, f"frame_{i:03d}.png")
                self._create_propagation_chart_frame(propagation_data, hour_index, len(master_index), frame_path)
            
            # --- Compile Video ---
            all_calls = sorted([log.get_metadata().get('MyCall') for log in self.logs])
            video_filename = f"{self.report_id}_{'_vs_'.join(all_calls)}.mp4"
            video_filepath = os.path.join(output_path, video_filename)
            create_output_directory(output_path)
            
            with imageio.get_writer(video_filepath, fps=self.FPS) as writer:
                for i in range(len(master_index)):
                    frame_file = os.path.join(frame_dir, f"frame_{i:03d}.png")
                    if os.path.exists(frame_file):
                        image = imageio.imread(frame_file)
                        duration = self.LAST_FRAME_DURATION_SECONDS if i == len(master_index) - 1 else self.FRAME_DURATION_SECONDS
                        for _ in range(duration * self.FPS):
                            writer.append_data(image)
            
            return f"Animation saved to: {video_filepath}"

        except Exception as e:
            logging.error(f"Failed to create animation. Error: {e}")
            return f"Error generating animation for report '{self.report_name}'."

    def _create_propagation_chart_frame(self, propagation_data: Dict, hour_num: int, total_hours: int, output_filepath: str):
        """Generates and saves a single frame for the animation."""
        
        fig = plt.figure(figsize=(20, 11.04))
        
        gs_main = gridspec.GridSpec(
            3, 1, figure=fig, height_ratios=[1, 10, 1.5],
            top=0.93, bottom=0.12, hspace=0.3
        )

        ax_title = fig.add_subplot(gs_main[0])
        ax_legend = fig.add_subplot(gs_main[2])
        ax_title.axis('off')
        ax_legend.axis('off')

        if not propagation_data:
            # Draw a blank frame with just the title if no data for this hour
            year = get_valid_dataframe(self.logs[0])['Date'].dropna().iloc[0].split('-')[0]
            metadata = self.logs[0].get_metadata()
            contest_name = metadata.get('ContestName', '')
            event_id = metadata.get('EventID', '')
            calls = [log.get_metadata().get('MyCall') for log in self.logs]
            title_line1 = f"{self.report_name} (Hour {hour_num}/{total_hours})"
            title_line2 = f"{year} {event_id} {contest_name} - {calls[0]} vs. {calls[1]}".strip().replace("  ", " ")
            ax_title.text(0.5, 0.5, f"{title_line1}\n{title_line2}\n\n(No Activity)", ha='center', va='center', fontsize=22, fontweight='bold', wrap=True)
            plt.savefig(output_filepath)
            plt.close(fig)
            return

        DATA = propagation_data.get('data', {})
        BANDS = propagation_data.get('bands', [])
        CONTINENTS = propagation_data.get('continents', [])
        MODES = propagation_data.get('modes', [])
        CALLS = propagation_data.get('calls', [])
        
        COLORS = plt.get_cmap('viridis', len(CONTINENTS))
        CONTINENT_COLORS = {cont: COLORS(i) for i, cont in enumerate(CONTINENTS)}

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

        metadata = self.logs[0].get_metadata()
        year = get_valid_dataframe(self.logs[0])['Date'].dropna().iloc[0].split('-')[0]
        contest_name = metadata.get('ContestName', '')
        event_id = metadata.get('EventID', '')
        
        title_line1 = f"{self.report_name} (Hour {hour_num}/{total_hours})"
        title_line2 = f"{year} {event_id} {contest_name} - {CALLS[0]} vs. {CALLS[1]}".strip().replace("  ", " ")
        ax_title.text(0.5, 0.5, f"{title_line1}\n{title_line2}", ha='center', va='center', fontsize=22, fontweight='bold', wrap=True)
        
        legend_patches = [plt.Rectangle((0,0),1,1, color=CONTINENT_COLORS.get(c, 'gray'), label=c) for c in CONTINENTS]
        ax_legend.legend(handles=legend_patches, loc='center', ncol=len(CONTINENTS), title="Continents", fontsize='large', frameon=False)
        
        try:
            plt.savefig(output_filepath)
        except Exception as e:
            logging.error(f"Error saving frame: {e}")
        finally:
            plt.close(fig)