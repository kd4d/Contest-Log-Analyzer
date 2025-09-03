# Contest Log Analyzer/contest_tools/reports/plot_comparative_run_sp.py
#
# Version: 0.57.4-Beta
# Date: 2025-09-03
#
# Purpose: A plot report that generates a "paired timeline" chart, visualizing
#          the operating style (Run, S&P, or Mixed) of two operators over time.
#
# --- Revision History ---
## [0.57.4-Beta] - 2025-09-03
### Changed
# - Updated the chart title to the standard two-line format to conform
#   to the official CLA Reports Style Guide.
## [0.56.7-Beta] - 2025-08-31
### Fixed
# - Updated band sorting logic to use the refactored _HAM_BANDS
#   variable from the ContestLog class, fixing an AttributeError.
## [0.52.1-Beta] - 2025-08-26
### Changed
# - Refactored report to generate individual plots by mode (CW, PH, DG) in
#   addition to the overall plot for contests with multiple modes.
## [0.42.2-Beta] - 2025-08-20
### Fixed
# - Explicitly disabled horizontal gridlines on the timeline chart to
#   remove visual clutter, per user feedback.
## [0.42.1-Beta] - 2025-08-20
### Changed
# - Refactored the plotting logic to use the higher-level ax.barh function
#   instead of drawing low-level rectangles.
### Fixed
# - "Inactive" periods are now rendered as transparent instead of white.
# - Removed the 15-minute borders around every time interval.
### Removed
# - Removed the temporary diagnostic logging statements.
## [0.42.0-Beta] - 2025-08-20
### Changed
# - Redesigned the plot to use a single, split subplot per band instead
#   of two separate subplots, making the chart more compact.
# - Implemented dynamic pagination, targeting ~8 bands per page.
# - Updated gridlines to appear only on the hour for better readability.
## [0.41.12-Beta] - 2025-08-20
### Fixed
# - Resolved the blank plot bug by explicitly setting the x-axis limits
#   after drawing the timeline patches, as the add_patch method does not
#   trigger matplotlib's autoscaling.
## [0.41.11-Beta] - 2025-08-20
### Added
# - Added detailed diagnostic logging to _generate_plot_for_page to trace
#   the data flow and diagnose the blank plot issue.
### Changed
# - Updated Y-axis labels to include the band for better clarity.
## [0.41.10-Beta] - 2025-08-20
### Fixed
# - Corrected the data aggregation logic to explicitly reindex against the
#   master time index, fixing the blank plot bug caused by a timezone-
#   related misalignment.
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

    def _generate_plot_for_page(self, df1: pd.DataFrame, df2: pd.DataFrame, log1_meta: Dict, log2_meta: Dict, bands_on_page: List[str], time_bins: pd.DatetimeIndex, output_path: str, page_title_suffix: str, page_file_suffix: str, mode_filter: str, **kwargs):
        """Helper to generate a single plot page."""
        call1 = log1_meta.get('MyCall', 'Log1')
        call2 = log2_meta.get('MyCall', 'Log2')
        debug_data_flag = kwargs.get("debug_data", False)
        
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
            for y_position, df, call in [(0.75, df1, call1), (0.25, df2, call2)]:
                df_band = df[df['Band'] == band]
                
                activity_by_interval = {}
                if not df_band.empty:
                    activity_by_interval = df_band.set_index('Datetime').groupby(pd.Grouper(freq='15min'))['Run'].apply(self._get_activity_type)
                
                activity_series = pd.Series(activity_by_interval).reindex(time_bins[:-1], fill_value='Inactive')

                # Use ax.barh to draw the timeline
                for interval_start, activity in activity_series.items():
                    if call == call1: # Only save debug data once per interval
                        plot_data_for_debug[band][call][interval_start.isoformat()] = activity
                    
                    if activity != 'Inactive':
                        ax.barh(
                            y=y_position,
                            width=1/96, # Width of a 15-minute interval in days
                            height=0.5,
                            left=mdates.date2num(interval_start),
                            color=ACTIVITY_COLORS[activity],
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

        df1 = get_valid_dataframe(log1, include_dupes=False)
        df2 = get_valid_dataframe(log2, include_dupes=False)

        if df1.empty or df2.empty:
            return f"Skipping '{self.report_name}': At least one log has no valid QSOs."

        df1['Datetime'] = pd.to_datetime(df1['Datetime']).dt.tz_localize('UTC')
        df2['Datetime'] = pd.to_datetime(df2['Datetime']).dt.tz_localize('UTC')
        
        # --- 1. Generate the main "All Modes" plot ---
        filepath = self._run_plot_for_slice(df1, df2, log1, log2, output_path, BANDS_PER_PAGE, mode_filter=None, **kwargs)
        if filepath:
            created_files.append(filepath)
        
        # --- 2. Generate per-mode plots if necessary ---
        modes_present = pd.concat([df1['Mode'], df2['Mode']]).dropna().unique()
        if len(modes_present) > 1:
            for mode in ['CW', 'PH', 'DG']:
                if mode in modes_present:
                    df1_slice = df1[df1['Mode'] == mode]
                    df2_slice = df2[df2['Mode'] == mode]

                    if not df1_slice.empty or not df2_slice.empty:
                        filepath = self._run_plot_for_slice(df1_slice, df2_slice, log1, log2, output_path, BANDS_PER_PAGE, mode_filter=mode, **kwargs)
                        if filepath:
                            created_files.append(filepath)

        if not created_files:
            return f"Report '{self.report_name}' did not generate any files."

        return f"Report file(s) saved to:\n" + "\n".join([f"  - {fp}" for fp in created_files])

    def _run_plot_for_slice(self, df1, df2, log1, log2, output_path, bands_per_page, mode_filter, **kwargs):
        """Helper to run the paginated plot generation for a specific data slice."""
        all_datetimes = pd.concat([df1['Datetime'], df2['Datetime']])
        min_time = all_datetimes.min().floor('h')
        max_time = all_datetimes.max().ceil('h')
        time_bins = pd.date_range(start=min_time, end=max_time, freq='15min', tz='UTC')
        
        active_bands_set = set(df1['Band'].unique()) | set(df2['Band'].unique())
        canonical_band_order = [band[1] for band in ContestLog._HAM_BANDS]
        active_bands = sorted(list(active_bands_set), key=lambda b: canonical_band_order.index(b) if b in canonical_band_order else -1)

        if not active_bands:
            return None

        num_pages = math.ceil(len(active_bands) / bands_per_page)
        
        for page_num in range(num_pages):
            start_index = page_num * bands_per_page
            end_index = start_index + bands_per_page
            bands_on_page = active_bands[start_index:end_index]
            
            page_title_suffix = f" (Page {page_num + 1}/{num_pages})" if num_pages > 1 else ""
            # Sanitize suffix for filename
            page_file_suffix = f"_Page_{page_num + 1}_of_{num_pages}" if num_pages > 1 else ""
            
            return self._generate_plot_for_page(
                df1=df1,
                df2=df2,
                log1_meta=log1.get_metadata(),
                log2_meta=log2.get_metadata(),
                bands_on_page=bands_on_page,
                time_bins=time_bins,
                output_path=output_path,
                page_title_suffix=page_title_suffix,
                page_file_suffix=page_file_suffix.replace('/', '_'),
                mode_filter=mode_filter,
                **kwargs
            )