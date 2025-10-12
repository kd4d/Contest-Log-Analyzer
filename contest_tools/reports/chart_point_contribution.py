# contest_tools/reports/chart_point_contribution.py
#
# Purpose: A chart report that generates a breakdown of total points by QSO
#          point value, presented as a series of pie charts.
#
# Author: Gemini AI
# Date: 2025-10-10
# Version: 0.91.13-Beta
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
# [0.91.13-Beta] - 2025-10-10
# - Changed: Corrected title generation to conform to the CLA Reports Style Guide.
# [0.90.0-Beta] - 2025-10-01
# Set new baseline version for release.

from typing import List
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os
import numpy as np
import re
from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import DonutChartComponent, create_output_directory, get_valid_dataframe, save_debug_data

class Report(ContestReport):
    report_id: str = "chart_point_contribution"
    report_name: str = "Point Contribution Breakdown"
    report_type: str = "chart"
    supports_multi = True
    MAX_LOGS_TO_COMPARE = 3

    def generate(self, output_path: str, **kwargs) -> str:
        if len(self.logs) > self.MAX_LOGS_TO_COMPARE:
            return f"Error: This report supports a maximum of {self.MAX_LOGS_TO_COMPARE} logs."
        
        valid_bands = self.logs[0].contest_definition.valid_bands
        is_single_band = len(valid_bands) == 1
        
        canonical_band_order = [band[1] for band in ContestLog._HAM_BANDS]
        bands_to_plot = valid_bands if is_single_band else ['All Bands'] + sorted(
            valid_bands,
            key=lambda b: canonical_band_order.index(b) if b in canonical_band_order else -1
        )
        
        created_files = []

        for band in bands_to_plot:
            try:
                save_path = output_path
                if not is_single_band and band != 'All Bands':
                    save_path = os.path.join(output_path, band)

                filepath = self._create_plot_for_band(band, save_path, **kwargs)
                if filepath:
                    created_files.append(filepath)
            except Exception as e:
                created_files.append(f"Failed to generate chart for {band}: {e}")
        
        if not created_files:
            return "No Point Contribution charts were generated."
        return "Point Contribution charts saved to:\n" + "\n".join([f"  - {fp}" for fp in created_files])

    def _create_plot_for_band(self, band: str, output_path: str, **kwargs) -> str:
        num_logs = len(self.logs)
        debug_data_flag = kwargs.get("debug_data", False)
        
        # --- Dynamic Layout ---
        nrows = 1
        ncols = num_logs
        figsize = (ncols * 7, nrows * 8) # Landscape format

        fig = plt.figure(figsize=figsize, constrained_layout=True)
        gs = GridSpec(nrows, ncols, figure=fig)

        band_log_points = [
            (get_valid_dataframe(log)['QSOPoints'].sum() if band == 'All Bands' 
             else get_valid_dataframe(log)[get_valid_dataframe(log)['Band'] == band]['QSOPoints'].sum())
            for log in self.logs
        ]
        max_band_points = max(band_log_points) if band_log_points else 1

        all_calls = sorted([log.get_metadata().get('MyCall', f'Log{i+1}') for i, log in enumerate(self.logs)])
        callsign_str = '_vs_'.join(all_calls)
        is_single_band = len(self.logs[0].contest_definition.valid_bands) == 1
        filename_band = self.logs[0].contest_definition.valid_bands[0].lower() if is_single_band else band.lower().replace('m','').replace(' ', '_')

        for i, log in enumerate(self.logs):
            df = get_valid_dataframe(log)
            band_df = df if band == 'All Bands' else df[df['Band'] == band]

            aggregated_data = DonutChartComponent.aggregate_data(band_df)

            # --- Save Debug Data ---
            debug_filename = f"{self.report_id}_{filename_band}_{all_calls[i]}.txt"
            save_debug_data(debug_data_flag, output_path, aggregated_data, custom_filename=debug_filename)
            
            point_ratio = (band_log_points[i] / max_band_points) if max_band_points > 0 else 0
            
            is_not_to_scale = 0 < point_ratio < 0.15
            radius_ratio = 0.15 if is_not_to_scale else point_ratio
            radius = 1.0 * np.sqrt(radius_ratio)

            component = DonutChartComponent(
                aggregated_data=aggregated_data, 
                title=log.get_metadata().get('MyCall', f'Log {i+1}'), 
                radius=radius, 
                is_not_to_scale=is_not_to_scale
            )
            component.draw_on(fig, gs[i])

        # --- Title and Filename ---
        metadata = self.logs[0].get_metadata()
        year = get_valid_dataframe(self.logs[0])['Date'].dropna().iloc[0].split('-')[0]
        contest_name = metadata.get('ContestName', '')
        event_id = metadata.get('EventID', '')
        
        band_title = self.logs[0].contest_definition.valid_bands[0].replace('M', ' Meters') if is_single_band else band.replace('M', ' Meters')

        title_line1 = f"{self.report_name} - {band_title}"
        title_line2 = f"{year} {event_id} {contest_name} - {callsign_str}".strip().replace("  ", " ")
        fig.suptitle(f"{title_line1}\n{title_line2}", fontsize=22, fontweight='bold')
        
        create_output_directory(output_path)
        filename = f"{self.report_id}_{filename_band}_{callsign_str}.png"
        filepath = os.path.join(output_path, filename)
        fig.savefig(filepath)
        plt.close(fig)

        return filepath