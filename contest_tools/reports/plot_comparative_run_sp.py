# Contest Log Analyzer/contest_tools/reports/plot_comparative_run_sp.py
#
# Version: 0.41.9-Beta
# Date: 2025-08-20
#
# Purpose: A plot report that generates a "paired timeline" chart, visualizing
#          the operating style (Run, S&P, or Mixed) of two operators over time.
#
# --- Revision History ---
## [0.41.9-Beta] - 2025-08-20
### Fixed
# - Corrected a data flow regression that caused empty plots by ensuring
#   timezone-aware data is passed correctly between functions.
## [0.41.8-Beta] - 2025-08-20
### Fixed
# - Permanently fixed AttributeError regression and UserWarning by enforcing
#   a minimum figure height and removing faulty single-band logic.
## [0.41.7-Beta] - 2025-08-20
### Fixed
# - Enforced a minimum figure height to resolve a UserWarning from the
#   layout manager on pages with few bands.
## [0.41.3-Beta] - 2025-08-20
### Fixed
# - Resolved an AttributeError that occurred when plotting a page with a
#   single band by removing incorrect conditional logic.
## [0.41.2-Beta] - 2025-08-20
### Fixed
# - Resolved a FileNotFoundError by sanitizing illegal characters ('/') from
#   debug and plot filenames for paginated reports.
## [0.41.1-Beta] - 2025-08-20
### Fixed
# - Resolved a NameError by adding the missing 'matplotlib.dates' import.
## [0.41.0-Beta] - 2025-08-20
# - Initial release of the Comparative Run/S&P Timeline report.
#
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

# Define the color scheme for the timeline blocks
ACTIVITY_COLORS = {
    'Run': '#FF4136',          # Red
    'S&P': '#2ECC40',          # Green
    'Mixed': '#FFDC00',        # Yellow
    'Inactive': '#FFFFFF'      # White for empty intervals
}

class Report(ContestReport):
    """
    Generates a "paired timeline" chart to visualize Run/S&P activity.
    """
    report_id: str = "comparative_run_sp_timeline"
    report_name: str = "Comparative Activity Timeline (Run/S&P)"
    report_type: str = "plot"
    supports_pairwise = True

    def _get_activity_type(self, series: pd.Series) -> str:
        """Determines the activity type for a 15-minute block."""
        if series.empty:
            return 'Inactive'
        
        run_statuses = set(series.unique())
        
        is_run = 'Run' in run_statuses
        is_sp = 'S&P' in run_statuses
        
        if is_run and not is_sp:
            return 'Run'
        elif is_sp and not is_run:
            return 'S&P'
        else:
            return 'Mixed'

    def _generate_plot_for_page(self, df1: pd.DataFrame, df2: pd.DataFrame, log1_meta: Dict, log2_meta: Dict, bands_on_page: List[str], time_bins: pd.DatetimeIndex, output_path: str, page_title_suffix: str, page_file_suffix: str, **kwargs):
        """Helper to generate a single plot page."""
        call1 = log1_meta.get('MyCall', 'Log1')
        call2 = log2_meta.get('MyCall', 'Log2')
        debug_data_flag = kwargs.get("debug_data", False)
        
        # --- Create figure with paired subplots for each band ---
        height = max(8.0, 2 * len(bands_on_page))
        fig, axes = plt.subplots(
            nrows=len(bands_on_page) * 2, 
            ncols=1, 
            figsize=(20, height), 
            sharex=True
        )
        if len(bands_on_page) * 2 == 1:
            axes = np.array([axes])

        plot_data_for_debug = {}

        for i, band in enumerate(bands_on_page):
            ax1 = axes[i*2] if len(bands_on_page) > 1 else axes[0]
            ax2 = axes[i*2 + 1] if len(bands_on_page) > 1 else axes[1]
            
            plot_data_for_debug[band] = {call1: {}, call2: {}}

            for ax, df, call in [(ax1, df1, call1), (ax2, df2, call2)]:
                df_band = df[df['Band'] == band]
                
                activity_by_interval = {}
                if not df_band.empty:
                    activity_by_interval = df_band.set_index('Datetime').groupby(pd.Grouper(freq='15min'))['Run'].apply(self._get_activity_type)
                
                for j, interval_start in enumerate(time_bins[:-1]):
                    activity = activity_by_interval.get(interval_start, 'Inactive')
                    plot_data_for_debug[band][call][interval_start.isoformat()] = activity
                    rect = mpatches.Rectangle(
                        (mdates.date2num(interval_start), 0),
                        width=1/96, # Width of a 15-minute interval in days
                        height=1,
                        facecolor=ACTIVITY_COLORS[activity],
                        edgecolor='gray'
                    )
                    ax.add_patch(rect)
                
                # Formatting for each subplot
                ax.set_yticks([0.5])
                ax.set_yticklabels([call], fontsize=12)
                ax.tick_params(axis='y', length=0)
                ax.set_ylim(0, 1)

        # --- Overall Figure Formatting ---
        fig.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%H%M'))
        fig.gca().xaxis.set_major_locator(mdates.HourLocator(interval=3))
        plt.xticks(rotation=45, ha='right')

        # --- Title ---
        year = get_valid_dataframe(self.logs[0])['Date'].dropna().iloc[0].split('-')[0]
        contest_name = log1_meta.get('ContestName', '')
        event_id = log1_meta.get('EventID', '')
        
        title_line1 = f"{self.report_name}{page_title_suffix}"
        title_line2 = f"{event_id} {year} {contest_name}".strip()
        title_line3 = f"{call1} vs. {call2}"
        final_title = f"{title_line1}\n{title_line2}\n{title_line3}"
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
        filename = f"{self.report_id}_{call1}_vs_{call2}{page_file_suffix}.png"
        filepath = os.path.join(output_path, filename)
        
        # Save Debug Data
        debug_filename = f"{self.report_id}_{call1}_vs_{call2}{page_file_suffix}.txt"
        save_debug_data(debug_data_flag, output_path, plot_data_for_debug, custom_filename=debug_filename)
        
        fig.savefig(filepath)
        plt.close(fig)
        return filepath

    def generate(self, output_path: str, **kwargs) -> str:
        """Orchestrates the generation of the timeline plot(s)."""
        if len(self.logs) != 2:
            return "Error: This report requires exactly two logs."

        BANDS_PER_PAGE = 5
        log1, log2 = self.logs[0], self.logs[1]
        
        # --- MODIFICATION: Prepare and localize data ONCE ---
        df1 = get_valid_dataframe(log1, include_dupes=False)
        df2 = get_valid_dataframe(log2, include_dupes=False)
        if df1.empty or df2.empty:
            return f"Skipping '{self.report_name}': At least one log has no valid QSOs."

        df1['Datetime'] = pd.to_datetime(df1['Datetime']).dt.tz_localize('UTC')
        df2['Datetime'] = pd.to_datetime(df2['Datetime']).dt.tz_localize('UTC')
        
        all_datetimes = pd.concat([df1['Datetime'], df2['Datetime']])
        min_time = all_datetimes.min().floor('h')
        max_time = all_datetimes.max().ceil('h')
        time_bins = pd.date_range(start=min_time, end=max_time, freq='15min', tz='UTC')
        
        active_bands_set = set(df1['Band'].unique()) | set(df2['Band'].unique())
        canonical_band_order = [band[1] for band in ContestLog._HF_BANDS]
        active_bands = sorted(list(active_bands_set), key=lambda b: canonical_band_order.index(b) if b in canonical_band_order else -1)

        if not active_bands:
            return f"Skipping '{self.report_name}': No bands with activity found."

        num_pages = math.ceil(len(active_bands) / BANDS_PER_PAGE)
        created_files = []

        for page_num in range(num_pages):
            start_index = page_num * BANDS_PER_PAGE
            end_index = start_index + BANDS_PER_PAGE
            bands_on_page = active_bands[start_index:end_index]
            
            page_title_suffix = f" (Page {page_num + 1}/{num_pages})" if num_pages > 1 else ""
            page_file_suffix = f"_Page_{page_num + 1}_of_{num_pages}" if num_pages > 1 else ""
            
            filepath = self._generate_plot_for_page(
                df1=df1,
                df2=df2,
                log1_meta=log1.get_metadata(),
                log2_meta=log2.get_metadata(),
                bands_on_page=bands_on_page,
                time_bins=time_bins,
                output_path=output_path,
                page_title_suffix=page_title_suffix,
                page_file_suffix=page_file_suffix,
                **kwargs
            )
            created_files.append(filepath)

        return f"Report file(s) saved to:\n" + "\n".join([f"  - {fp}" for fp in created_files])