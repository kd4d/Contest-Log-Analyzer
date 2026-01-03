# contest_tools/reports/plot_wrtc_propagation.py
#
# Purpose: A plot report that generates a visual prototype for one frame
#          of the proposed WRTC propagation animation. It creates a side-by-side
#          butterfly chart comparing two logs' hourly QSO data, broken down by
#          band, continent, and mode for a single, peak-activity hour.
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

    def _create_propagation_chart(self, propagation_data: Dict, hour_num: int, total_