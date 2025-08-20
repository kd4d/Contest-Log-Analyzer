# Contest Log Analyzer/contest_tools/reports/chart_qso_breakdown.py
#
# Purpose: A chart report that generates a comparative QSO breakdown bar chart.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-20
# Version: 0.41.4-Beta
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
## [0.41.4-Beta] - 2025-08-20
### Changed
# - Switched to Matplotlib's constrained_layout manager for robust and
#   automatic label spacing.
# - Implemented dynamic font sizing based on band count and callsign length.
### Fixed
# - Removed conflicting manual layout adjustments that caused whitespace issues.
# - Corrected vertical line placement to extend from above the 'Common'
#   label to the chart axis.
## [0.41.3-Beta] - 2025-08-19
### Fixed
# - Reduced excessive whitespace between the X-axis and the three-tier
#   labels for a tighter layout.
## [0.41.2-Beta] - 2025-08-19
### Changed
# - Reworked X-axis labels into a correct and more readable three-tier format.
# - Font size for labels is now reduced only on pages with exactly six bands.
### Fixed
# - Corrected implementation of the three-tier layout, fixing inverted
#   lines and single-line label bugs from the previous version.
## [0.41.1-Beta] - 2025-08-19
### Added
# - Logic to automatically skip bands with no QSOs from either log.
### Changed
# - Refactored report to use a multi-page output (6 bands per page) to
#   prevent X-axis label overlapping on contests with many active bands.
# - Updated X-axis to a three-tier format showing Band, Callsign, and Common.
## [0.41.0-Beta] - 2025-08-19
### Added
# - Logic to automatically skip bands with no QSOs from either log.
### Changed
# - Refactore report to use a multi-page output to prevent
#   X-axis label overlapping on contests with many active bands.
# - Updated X-axis to a three-tier format showing Band, Callsign, and Common.
## [0.38.0-Beta] - 2025-08-18
### Added
# - Added call to the save_debug_data helper function to dump the source
#   data dictionary when the --debug-data flag is enabled.
## [0.30.41-Beta] - 2025-08-06
### Fixed
# - Regenerated file to fix a SyntaxError likely caused by file corruption.
## [0.30.40-Beta] - 2025-08-06
### Changed
# - Renamed file from plot_qso_breakdown_chart.py to chart_qso_breakdown.py
#   to match its report_type.
## [0.30.18-Beta] - 2025-08-05
### Changed
# - Restored the original stacked bar chart with two-level x-axis labels.
# - Integrated the restored plotting logic with current, bug-fixed data handling.
from typing import List
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import math

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import create_output_directory, save_debug_data

class Report(ContestReport):
    """
    Generates a stacked bar chart comparing the QSO breakdown (Run/S&P/Unknown/Common)
    between two logs for each band.
    """
    report_id: str = "qso_breakdown_chart"
    report_name: str = "QSO Breakdown Chart"
    report_type: str = "chart"
    supports_pairwise = True
    
    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the plot. This report always excludes dupes.
        """
        if len(self.logs) != 2:
            return "Error: The QSO Breakdown Chart report requires exactly two logs."
        
        BANDS_PER_PAGE = 6
        debug_data_flag = kwargs.get("debug_data", False)
        log1, log2 = self.logs[0], self.logs[1]
        call1 = log1.get_metadata().get('MyCall', 'Log1')
        call2 = log2.get_metadata().get('MyCall', 'Log2')

        df1_full = log1.get_processed_data()[log1.get_processed_data()['Dupe'] == False]
        df2_full = log2.get_processed_data()[log2.get_processed_data()['Dupe'] == False]
        
        # --- Get active bands from data and sort them ---
        active_bands_set = set(df1_full['Band'].unique()) | set(df2_full['Band'].unique())
        canonical_band_order = [band[1] for band in ContestLog._HF_BANDS]
        active_bands = sorted(list(active_bands_set), key=lambda b: canonical_band_order.index(b) if b in canonical_band_order else -1)

        if not active_bands:
            return "Skipping QSO Breakdown Chart: No bands with activity found."

        num_pages = math.ceil(len(active_bands) / BANDS_PER_PAGE)
        created_files = []

        for page_num in range(num_pages):
            start_index = page_num * BANDS_PER_PAGE
            end_index = start_index + BANDS_PER_PAGE
            bands_on_page = active_bands[start_index:end_index]

            # --- Data Aggregation for the current page ---
            plot_data = {
                'bands': [b.replace('M', '') for b in bands_on_page],
                call1: {'run': [], 'sp': [], 'unknown': []},
                call2: {'run': [], 'sp': [], 'unknown': []},
                'common': []
            }

            for band in bands_on_page:
                df1_band = df1_full[df1_full['Band'] == band]
                df2_band = df2_full[df2_full['Band'] == band]

                calls1 = set(df1_band['Call'].unique())
                calls2 = set(df2_band['Call'].unique())
                
                common_calls = calls1.intersection(calls2)
                unique_to_1 = calls1.difference(calls2)
                unique_to_2 = calls2.difference(calls1)

                df1_unique = df1_band[df1_band['Call'].isin(unique_to_1)]
                df2_unique = df2_band[df2_band['Call'].isin(unique_to_2)]

                plot_data[call1]['run'].append((df1_unique['Run'] == 'Run').sum())
                plot_data[call1]['sp'].append((df1_unique['Run'] == 'S&P').sum())
                plot_data[call1]['unknown'].append((df1_unique['Run'] == 'Unknown').sum())
                
                plot_data[call2]['run'].append((df2_unique['Run'] == 'Run').sum())
                plot_data[call2]['sp'].append((df2_unique['Run'] == 'S&P').sum())
                plot_data[call2]['unknown'].append((df2_unique['Run'] == 'Unknown').sum())
                
                plot_data['common'].append(len(common_calls))

            # --- Save Debug Data ---
            page_suffix = f"_p{page_num + 1}" if num_pages > 1 else ""
            debug_filename = f"{self.report_id}_{call1}_vs_{call2}{page_suffix}.txt"
            save_debug_data(debug_data_flag, output_path, plot_data, custom_filename=debug_filename)

            # --- Plotting ---
            sns.set_theme(style="whitegrid")
            fig, ax = plt.subplots(figsize=(20, 8), constrained_layout=True)

            group_spacing = 3.0 
            bar_width = 0.8
            index = np.arange(len(plot_data['bands'])) * group_spacing

            run1_bars = np.array(plot_data[call1]['run'])
            sp1_bars = np.array(plot_data[call1]['sp'])
            ax.bar(index - bar_width, run1_bars, bar_width, color='red', label=f'Unique Run')
            ax.bar(index - bar_width, sp1_bars, bar_width, bottom=run1_bars, color='green', label=f'Unique S&P')
            ax.bar(index - bar_width, plot_data[call1]['unknown'], bar_width, bottom=run1_bars + sp1_bars, color='gold', label=f'Unique Unknown')

            ax.bar(index, plot_data['common'], bar_width, color='grey', label='Common Calls')

            run2_bars = np.array(plot_data[call2]['run'])
            sp2_bars = np.array(plot_data[call2]['sp'])
            ax.bar(index + bar_width, run2_bars, bar_width, color='red')
            ax.bar(index + bar_width, sp2_bars, bar_width, bottom=run2_bars, color='green')
            ax.bar(index + bar_width, plot_data[call2]['unknown'], bar_width, bottom=run2_bars + sp2_bars, color='gold')

            # --- Formatting ---
            metadata = log1.get_metadata()
            year = log1.get_processed_data()['Date'].iloc[0].split('-')[0] if not log1.get_processed_data().empty else "----"
            contest_name = metadata.get('ContestName', '')
            event_id = metadata.get('EventID', '')
            page_title_suffix = f" (Page {page_num + 1}/{num_pages})" if num_pages > 1 else ""
            
            title_line1 = f"{event_id} {year} {contest_name}".strip()
            title_line2 = f"QSO Breakdown ({call1} vs {call2}){page_title_suffix}"
            ax.set_title(f"{title_line1}\n{title_line2}", fontsize=16, fontweight='bold')
            ax.set_ylabel('QSO Count')
            
            # --- Three-Level X-Axis Labels ---
            ax.set_xticks(index)
            ax.set_xticklabels([''] * len(plot_data['bands']))
            ax.tick_params(axis='x', which='major', length=0) 
            
            # Dynamic Font Sizing
            font_size = plt.rcParams['xtick.labelsize'] + 2
            max_call_len = max(len(call1), len(call2))
            if len(bands_on_page) == 6 or (len(bands_on_page) == 5 and max_call_len > 6):
                font_size -= 2

            for i, group_center in enumerate(index):
                # Tier 3 (Bottom)
                y_pos_tier3 = -0.12
                ax.text(group_center, y_pos_tier3, f"{plot_data['bands'][i]} Meters", ha='center', va='top', transform=ax.get_xaxis_transform(), fontweight='bold')
                
                # Tier 2 (Middle)
                y_pos_tier2 = -0.08
                ax.text(group_center, y_pos_tier2, "Common", ha='center', va='top', transform=ax.get_xaxis_transform(), fontsize=font_size)
                
                # Tier 1 (Top)
                y_pos_tier1 = -0.04
                ax.text(group_center - bar_width, y_pos_tier1, call1, ha='center', va='top', transform=ax.get_xaxis_transform(), fontsize=font_size)
                ax.text(group_center + bar_width, y_pos_tier1, call2, ha='center', va='top', transform=ax.get_xaxis_transform(), fontsize=font_size)

                # Vertical line from just above Tier 2 up to the axis
                line_y_start = y_pos_tier2 + 0.005 
                ax.plot([group_center, group_center], [0, line_y_start], color='gray', linestyle=':', transform=ax.get_xaxis_transform(), clip_on=False)
            
            handles, labels = ax.get_legend_handles_labels()
            unique_labels = dict(zip(labels, handles))
            ax.legend(unique_labels.values(), unique_labels.keys(), ncol=4)

            # --- Save File ---
            create_output_directory(output_path)
            filename = f"{self.report_id}_{call1}_vs_{call2}{page_suffix}.png"
            filepath = os.path.join(output_path, filename)
            fig.savefig(filepath)
            plt.close(fig)
            created_files.append(filepath)

        return f"QSO breakdown chart(s) saved to:\n" + "\n".join([f"  - {fp}" for fp in created_files])