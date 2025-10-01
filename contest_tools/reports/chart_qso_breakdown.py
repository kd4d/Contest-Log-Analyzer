# contest_tools/reports/chart_qso_breakdown.py
#
# Purpose: A chart report that generates a comparative QSO breakdown bar chart.
#
# Author: Gemini AI
# Date: 2025-10-01
# Version: 0.90.0-Beta
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
# [0.90.0-Beta] - 2025-10-01
# Set new baseline version for release.

from typing import List
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import math
import colorsys
from matplotlib.patches import Patch

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import create_output_directory, save_debug_data

def _adjust_lightness(hex_color, factor):
    """Increases the lightness of a hex color by a factor."""
    h = hex_color.lstrip('#')
    r, g, b = tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    hue, lightness, saturation = colorsys.rgb_to_hls(r, g, b)
    lightness = min(1.0, lightness * factor)
    r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
    return f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'

# Base colors for a consistent palette
BASE_UNIQUE_COLORS = {
    'Run': '#FF4136',
    'S&P': '#2ECC40',
    'Unknown': '#FFDC00'
}

# Brightened colors for UNIQUE QSOs
UNIQUE_COLORS = {k: _adjust_lightness(v, 1.25) for k, v in BASE_UNIQUE_COLORS.items()}

# Muted/darker colors for COMMON QSOs
COMMON_COLORS = {
    'Run (Both)': '#85144b',
    'S&P (Both)': '#004D40',
    'Mixed or Unknown': '#DAA520'
}

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
        canonical_band_order = [band[1] for band in ContestLog._HAM_BANDS]
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
                call1: {'Run': [], 'S&P': [], 'Unknown': []},
                call2: {'Run': [], 'S&P': [], 'Unknown': []},
                'common': {'Run (Both)': [], 'S&P (Both)': [], 'Mixed or Unknown': []}
            }

            for band in bands_on_page:
                df1_band = df1_full[df1_full['Band'] == band]
                df2_band = df2_full[df2_full['Band'] == band]

                calls1 = set(df1_band['Call'])
                calls2 = set(df2_band['Call'])
                
                common_calls = calls1.intersection(calls2)
                unique_to_1 = calls1.difference(calls2)
                unique_to_2 = calls2.difference(calls1)

                df1_unique = df1_band[df1_band['Call'].isin(unique_to_1)]
                df2_unique = df2_band[df2_band['Call'].isin(unique_to_2)]

                plot_data[call1]['Run'].append((df1_unique['Run'] == 'Run').sum())
                plot_data[call1]['S&P'].append((df1_unique['Run'] == 'S&P').sum())
                plot_data[call1]['Unknown'].append((df1_unique['Run'] == 'Unknown').sum())
                
                plot_data[call2]['Run'].append((df2_unique['Run'] == 'Run').sum())
                plot_data[call2]['S&P'].append((df2_unique['Run'] == 'S&P').sum())
                plot_data[call2]['Unknown'].append((df2_unique['Run'] == 'Unknown').sum())
                
                # --- New logic for Common QSO breakdown ---
                df1_common = df1_band[df1_band['Call'].isin(common_calls)][['Call', 'Run']].set_index('Call')
                df2_common = df2_band[df2_band['Call'].isin(common_calls)][['Call', 'Run']].set_index('Call')
                merged_common = df1_common.join(df2_common, lsuffix='_1', rsuffix='_2')

                both_run = len(merged_common[(merged_common['Run_1'] == 'Run') & (merged_common['Run_2'] == 'Run')])
                both_sp = len(merged_common[(merged_common['Run_1'] == 'S&P') & (merged_common['Run_2'] == 'S&P')])
                other = len(merged_common) - both_run - both_sp
                
                plot_data['common']['Run (Both)'].append(both_run)
                plot_data['common']['S&P (Both)'].append(both_sp)
                plot_data['common']['Mixed or Unknown'].append(other)

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

            # Unique Bars for Call 1
            bottom = np.zeros(len(bands_on_page))
            for activity, color in UNIQUE_COLORS.items():
                counts = np.array(plot_data[call1][activity])
                ax.bar(index - bar_width, counts, bar_width, bottom=bottom, color=color)
                bottom += counts

            # Common Stacked Bar
            bottom = np.zeros(len(bands_on_page))
            for category, color in COMMON_COLORS.items():
                counts = np.array(plot_data['common'][category])
                ax.bar(index, counts, bar_width, bottom=bottom, color=color)
                bottom += counts
            
            # Unique Bars for Call 2
            bottom = np.zeros(len(bands_on_page))
            for activity, color in UNIQUE_COLORS.items():
                counts = np.array(plot_data[call2][activity])
                ax.bar(index + bar_width, counts, bar_width, bottom=bottom, color=color)
                bottom += counts

            # --- Formatting ---
            metadata = log1.get_metadata()
            year = log1.get_processed_data()['Date'].iloc[0].split('-')[0] if not log1.get_processed_data().empty else "----"
            contest_name = metadata.get('ContestName', '')
            event_id = metadata.get('EventID', '')
            page_title_suffix = f" (Page {page_num + 1}/{num_pages})" if num_pages > 1 else ""
            
            # Per CLA Reports Style Guide v0.52.14-Beta
            title_line1 = self.report_name
            context_str = f"{year} {event_id} {contest_name}".strip().replace("  ", " ")
            calls_str = f"{call1} vs {call2}{page_title_suffix}"
            title_line2 = f"{context_str} - {calls_str}"
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
                y_pos_tier3 = -0.12 # Band
                y_pos_tier2 = -0.08 # Common
                y_pos_tier1 = -0.04 # Callsigns
                
                ax.text(group_center, y_pos_tier3, f"{plot_data['bands'][i]} Meters", ha='center', va='top', transform=ax.get_xaxis_transform(), fontweight='bold')
                ax.text(group_center, y_pos_tier2, "Common", ha='center', va='top', transform=ax.get_xaxis_transform(), fontsize=font_size)
                ax.text(group_center - bar_width, y_pos_tier1, call1, ha='center', va='top', transform=ax.get_xaxis_transform(), fontsize=font_size)
                ax.text(group_center + bar_width, y_pos_tier1, call2, ha='center', va='top', transform=ax.get_xaxis_transform(), fontsize=font_size)
                ax.plot([group_center, group_center], [y_pos_tier2 + 0.005, 0], color='gray', linestyle=':', transform=ax.get_xaxis_transform(), clip_on=False)
            
            # --- Two-Legend System ---
            unique_handles = [Patch(color=color, label=label) for label, color in UNIQUE_COLORS.items()]
            leg1 = ax.legend(handles=unique_handles, loc='upper left', title=f'Unique QSOs')
            ax.add_artist(leg1)
            
            common_handles = [Patch(color=color, label=label) for label, color in COMMON_COLORS.items()]
            ax.legend(handles=common_handles, loc='upper right', title='Common QSOs')

            # --- Save File ---
            create_output_directory(output_path)
            filename = f"{self.report_id}_{call1}_vs_{call2}{page_suffix}.png"
            filepath = os.path.join(output_path, filename)
            fig.savefig(filepath)
            plt.close(fig)
            created_files.append(filepath)

        return f"QSO breakdown chart(s) saved to:\n" + "\n".join([f"  - {fp}" for fp in created_files])
