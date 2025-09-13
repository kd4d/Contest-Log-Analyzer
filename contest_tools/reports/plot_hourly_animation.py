# Contest Log Analyzer/contest_tools/reports/plot_hourly_animation.py
#
# Version: 0.85.10-Beta
# Date: 2025-09-13
#
# Purpose: A plot report that generates a series of hourly images and compiles
#          them into an animated video showing contest progression.
#          It also creates a standalone interactive HTML version of the chart.
# Copyright (c) 2025 Mark Bailey, KD4D
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# --- Revision History ---
## [0.85.10-Beta] - 2025-09-13
### Changed
# - Refactored the _prepare_data method to source its cumulative score
#   and QSO data from the new, centralized time_series_score_df, removing
#   all internal calculation logic to align with the new architecture.
## [0.80.3-Beta] - 2025-09-12
### Fixed
# - Corrected the band sorting logic to use a robust, two-step pattern
#   to prevent a ValueError during report generation.
## [0.58.0-Beta] - 2025-09-03
### Changed
# - Updated the chart title to the standard three-line format to conform
#   to the official CLA Reports Style Guide.
## [0.57.40-Beta] - 2025-09-03
### Fixed
# - Modified the video generation to use the system's temporary
#   directory for frame creation, preventing file-locking errors
#   caused by cloud sync services like OneDrive.
## [0.57.39-Beta] - 2025-09-03
### Fixed
# - Applied the resilient retry logic to the initial cleanup call at the
#   start of the video generation function. This prevents a crash if
#   the temporary directory is locked from a previous failed run.
## [0.56.25-Beta] - 2025-08-31
### Fixed
# - Replaced the cleanup logic with a resilient 10-second retry loop to
#   prevent a PermissionError race condition when deleting temp files.
# - Downgraded the final cleanup failure message from an error to a warning.
## [0.56.8-Beta] - 2025-08-31
### Fixed
# - Updated band sorting logic to use the refactored _HAM_BANDS
#   variable from the ContestLog class.
## [0.38.2-Beta] - 2025-08-18
### Fixed
# - Corrected a TypeError in the animation's debug data generation by
#   manually creating a nested dictionary to prevent invalid tuple keys.
## [0.38.1-Beta] - 2025-08-18
### Fixed
# - Expanded the frame_debug_data dictionary to be a complete snapshot
#   of the source data for all three animation charts, fixing the
#   incomplete debug file bug.
## [0.38.0-Beta] - 2025-08-18
### Added
# - Added call to the save_debug_data helper function inside the per-frame
#   loop to dump the source data for each frame of the animation.
## [0.36.7-Beta] - 2025-08-16
### Fixed
# - Corrected a SyntaxError by adding a missing colon to the color
#   shades dictionary in the _get_color_shades function.
## [0.36.6-Beta] - 2025-08-16
### Changed
# - Modified the video generation loop to display the final frame for
#   30 seconds, while all other frames remain at 2 seconds.
## [0.36.5-Beta] - 2025-08-15
### Fixed
# - Replaced the flawed, manual cumulative multiplier calculation with a
#   vectorized approach. The new logic correctly uses pandas resample/cumsum
#   methods, ensuring multipliers from the final hour are included in the score.
## [0.36.4-Beta] - 2025-08-15
### Fixed
# - Corrected a SyntaxError on line 57 by adding a missing colon in the
#   `_get_color_shades` dictionary definition.
## [0.36.3-Beta] - 2025-08-15
### Fixed
# - Corrected the animation timeline calculation to use `.floor('h')`
#   directly on the max timestamp. This prevents the final hour from being
#   truncated when the last QSO is exactly on the hour.
## [0.35.28-Beta] - 2025-08-15
### Fixed
# - Corrected the animation timeline calculation to prevent an extra
#   hour from being added to the end of the contest.
## [0.35.21-Beta] - 2025-08-15
### Changed
# - Updated the color scheme for vertical bar charts to use bright red
#   for 'Unknown' QSOs and a dark/light shading for 'Run'/'S&P'.
## [0.35.20-Beta] - 2025-08-14
### Fixed
# - Fixed blank hourly rate chart by ensuring all Run/S&P/Unknown
#   columns are present after data preparation.
# - Added vertical spacing (hspace) to the GridSpec layout to
#   resolve all element overlaps.
import pandas as pd
import os
import logging
import imageio.v2 as imageio
import shutil
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.gridspec as gridspec
import colorsys
import time
import errno
import tempfile
from typing import List, Dict

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import create_output_directory, get_valid_dataframe, save_debug_data

def _get_color_shades(base_rgb):
    """Generates dark, light, and red shades for Run/S&P/Unknown."""
    h, l, s = colorsys.rgb_to_hls(*base_rgb)
    return {
        'Run': colorsys.hls_to_rgb(h, max(0, l * 0.65), s),      # Darker
        'S&P': colorsys.hls_to_rgb(h, min(1, l * 1.2 + 0.1), s), # Lighter
        'Unknown': '#FF0000',                                   # Bright Red
    }

class Report(ContestReport):
    report_id = "hourly_animation"
    report_name = "Hourly Rate Animation"
    report_type = "animation"
    supports_single = True
    supports_multi = True

    # --- Configuration ---
    FPS = 10
    FRAME_DURATION_SECONDS = 2
    LAST_FRAME_DURATION_SECONDS = 30
    IMAGE_WIDTH_PX = 1280
    IMAGE_HEIGHT_PX = 720
    DPI = 100
    
    CALLSIGN_COLORS = plt.get_cmap('tab10').colors

    def _prepare_data(self, band_filter: str = None, mode_filter: str = None) -> Dict:
        """Pre-calculates all necessary hourly and cumulative data."""
        all_dfs = []
        for log in self.logs:
            df = get_valid_dataframe(log, include_dupes=False).copy()
            df['MyCall'] = log.get_metadata().get('MyCall')
            all_dfs.append(df)
        
        combined_df = pd.concat(all_dfs)

        if band_filter and band_filter != 'All Bands': combined_df = combined_df[combined_df['Band'] == band_filter]
        if mode_filter: combined_df = combined_df[combined_df['Mode'] == mode_filter]

        if combined_df.empty: return None

        combined_df['Datetime'] = pd.to_datetime(combined_df['Datetime']).dt.tz_localize('UTC')

        log_manager = getattr(self.logs[0], '_log_manager_ref', None)
        master_index = getattr(log_manager, 'master_time_index', None)
        if master_index is None: return None
        
        log_data = {}
        
        hourly_rates_df = combined_df.groupby([combined_df['Datetime'].dt.floor('h'), 'Band', 'MyCall']).size().reset_index(name='QSOs')
        max_hourly_rate = hourly_rates_df['QSOs'].max() if not hourly_rates_df.empty else 1

        for i, log in enumerate(self.logs):
            call = log.get_metadata().get('MyCall', f'Log{i+1}')
            log_df = all_dfs[i]
            score_ts = log.time_series_score_df
            
            hourly_run_sp = log_df.groupby([log_df['Datetime'].dt.floor('h'), 'Band', 'Mode', 'Run']).size().unstack(fill_value=0)
            for state in ['Run', 'S&P', 'Unknown']:
                if state not in hourly_run_sp.columns:
                    hourly_run_sp[state] = 0
            
            cum_qso_per_band_breakdown = log_df.groupby([log_df['Datetime'].dt.floor('h'), 'Band', 'Run']).size().unstack(level=['Band', 'Run'], fill_value=0).cumsum()
            cum_qso_per_band_breakdown = cum_qso_per_band_breakdown.reindex(master_index, method='ffill').fillna(0)

            log_data[call] = {
                'cum_qso': score_ts['run_qso_count'] + score_ts['sp_unk_qso_count'], 
                'cum_score': score_ts['score'],
                'hourly_run_sp': hourly_run_sp, 'cum_qso_per_band_breakdown': cum_qso_per_band_breakdown
            }
        
        all_cum_per_band_dfs = [ld['cum_qso_per_band_breakdown'] for ld in log_data.values()]
        max_cum_qso_on_band = 1
        if all_cum_per_band_dfs:
            final_band_totals = pd.concat([df.iloc[[-1]] for df in all_cum_per_band_dfs])
            if not final_band_totals.empty:
                canonical_band_order = [band[1] for band in ContestLog._HAM_BANDS]
                bands = sorted(combined_df['Band'].unique(), key=lambda b: canonical_band_order.index(b) if b in canonical_band_order else -1)
                max_val = 0
                for band in bands:
                    band_cols = [col for col in final_band_totals.columns if col[0] == band]
                    if band_cols:
                        max_val = max(max_val, final_band_totals[band_cols].sum(axis=1).max())
                max_cum_qso_on_band = max_val

        if max_cum_qso_on_band == 0: max_cum_qso_on_band = 1
        max_final_qso = max((ld['cum_qso'].iloc[-1] for ld in log_data.values()), default=1)
        max_final_score = max((ld['cum_score'].iloc[-1] for ld in log_data.values()), default=1)
        
        if max_final_qso == 0: max_final_qso = 1
        if max_final_score == 0: max_final_score = 1
        if max_hourly_rate == 0: max_hourly_rate = 1

        return {
            'log_data': log_data, 'master_index': master_index,
            'max_final_qso': max_final_qso, 'max_final_score': max_final_score,
            'max_hourly_rate': max_hourly_rate, 'max_cum_qso_on_band': max_cum_qso_on_band,
            'bands': bands, 'modes': combined_df['Mode'].unique().tolist()
        }

    def _generate_video(self, data: Dict, output_path: str, debug_data_flag: bool):
        frame_dir = tempfile.mkdtemp(prefix="cla_frames_")

        try:
            logging.info(f"Generating {len(data['master_index'])} frames for animation video in temp dir: {frame_dir}...")
            
            total_frames = len(data['master_index'])
            first_log_meta = self.logs[0].get_metadata()
            contest_name = first_log_meta.get('ContestName', 'Unknown Contest')
            year = self.logs[0].get_processed_data()['Date'].iloc[0].split('-')[0]
            event_id = first_log_meta.get('EventID', '')
            calls = list(data['log_data'].keys())
            num_logs = len(calls)
            callsign_str = ", ".join(calls)
            
            for i, hour in enumerate(data['master_index']):
                # --- Save Debug Data for this frame ---
                frame_debug_data = {
                    'hour_timestamp': hour.isoformat(),
                    'hour_index': i + 1,
                    'logs': {}
                }
                
                for call in calls:
                    # Data for Top Chart (Cumulative Totals)
                    top_chart_data = {
                        'score': data['log_data'][call]['cum_score'].get(hour, 0),
                        'qsos': data['log_data'][call]['cum_qso'].get(hour, 0)
                    }
    
                    # Data for Bottom-Left Chart (Hourly Rates)
                    hourly_rate_data = {}
                    try:
                        hourly_slice = data['log_data'][call]['hourly_run_sp'].loc[hour]
                        if not hourly_slice.empty:
                            # Manually build a nested dictionary to avoid tuple keys
                            for index, run_counts in hourly_slice.iterrows():
                                band, mode = index
                                if band not in hourly_rate_data:
                                    hourly_rate_data[band] = {}
                                hourly_rate_data[band][mode] = run_counts.to_dict()
                    except KeyError:
                        pass 
    
                    # Data for Bottom-Right Chart (Cumulative by Band)
                    cum_by_band_data = {}
                    try:
                        cum_slice = data['log_data'][call]['cum_qso_per_band_breakdown'].loc[hour]
                        if not cum_slice.empty:
                            cum_by_band_data = {band: cum_slice[band].to_dict() for band in cum_slice.index.get_level_values(0).unique()}
                    except KeyError:
                        pass
                    
                    frame_debug_data['logs'][call] = {
                        'top_chart_cumulative_totals': top_chart_data,
                        'bottom_left_hourly_rates': hourly_rate_data,
                        'bottom_right_cumulative_by_band': cum_by_band_data
                    }
                
                debug_filename = f"{self.report_id}_{'_vs_'.join(sorted(calls))}_frame_{i:03d}.txt"
                save_debug_data(debug_data_flag, output_path, frame_debug_data, custom_filename=debug_filename)
    
                fig_mpl = plt.figure(figsize=(self.IMAGE_WIDTH_PX / self.DPI, self.IMAGE_HEIGHT_PX / self.DPI), dpi=self.DPI)
                
                gs_main = fig_mpl.add_gridspec(3, 1, height_ratios=[1, 10, 1.2], hspace=0.8)
                
                ax_top_legend = fig_mpl.add_subplot(gs_main[0])
                ax_bottom_legend = fig_mpl.add_subplot(gs_main[2])
                ax_top_legend.axis('off'); ax_bottom_legend.axis('off')
                
                top_chart_ratio = 0.12 * num_logs
                top_chart_ratio = max(0.15, min(top_chart_ratio, 0.45))
                
                gs_plots = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=gs_main[1], height_ratios=[top_chart_ratio, 1 - top_chart_ratio], hspace=0.9)
                ax_top = fig_mpl.add_subplot(gs_plots[0])
                gs_bottom_plots = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=gs_plots[1], width_ratios=[3, 2], wspace=0.15)
                ax_bottom_left = fig_mpl.add_subplot(gs_bottom_plots[0, 0])
                ax_bottom_right = fig_mpl.add_subplot(gs_bottom_plots[0, 1])
    
                # --- Standard Three-Line Title ---
                title_line1 = self.report_name
                title_line2 = f"{year} {event_id} {contest_name} - {callsign_str}".strip()
                title_line3 = f"Hour {i + 1} of {total_frames}"
                final_title = f"{title_line1}\n{title_line2}\n{title_line3}"
                fig_mpl.suptitle(final_title)
    
                ax_qso = ax_top; ax_score = ax_top.twiny()
                for j, call in enumerate(calls):
                    score = data['log_data'][call]['cum_score'].get(hour, 0)
                    qsos = data['log_data'][call]['cum_qso'].get(hour, 0)
                    bar_color = self.CALLSIGN_COLORS[j % len(self.CALLSIGN_COLORS)]
                    
                    ax_score.barh(j + 0.2, score, height=0.4, align='center', color=bar_color, label=call)
                    ax_score.text(score, j + 0.2, f' {score:,.0f}', va='center', ha='left')
                    ax_qso.barh(j - 0.2, qsos, height=0.4, align='center', color=bar_color, alpha=0.6)
                    ax_qso.text(qsos, j - 0.2, f' {qsos:,.0f}', va='center', ha='left')
                
                ax_qso.set_yticks(range(len(calls))); ax_qso.set_yticklabels([]); ax_qso.tick_params(axis='y', length=0)
                ax_qso.set_xlim(0, data['max_final_qso']); ax_qso.set_xlabel("Cumulative QSOs")
                ax_score.set_xlim(0, data['max_final_score']); ax_score.set_xlabel("Cumulative Score")
                ax_score.xaxis.set_ticks_position('top'); ax_score.xaxis.set_label_position('top')
                ax_score.xaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))
                ax_top_legend.legend(*ax_score.get_legend_handles_labels(), loc='center', ncol=num_logs, title="Callsign", fontsize='medium')
    
                x_labels_hourly = [f"{b}-{m}" for b in data['bands'] for m in data['modes']]
                bar_width_hourly = 0.8 / len(calls)
                for j, call in enumerate(calls):
                    color_shades = _get_color_shades(self.CALLSIGN_COLORS[j % len(self.CALLSIGN_COLORS)])
                    bottoms = [0] * len(x_labels_hourly)
                    for run_state in ['Run', 'S&P', 'Unknown']:
                        y_values = []
                        for band in data['bands']:
                            for mode in data['modes']:
                                try: count = data['log_data'][call]['hourly_run_sp'].loc[(hour, band, mode), run_state]
                                except KeyError: count = 0
                                y_values.append(count)
                        
                        ax_bottom_left.bar([x + j * bar_width_hourly for x in range(len(x_labels_hourly))], y_values,
                                           width=bar_width_hourly, bottom=bottoms, color=color_shades[run_state], alpha=0.8)
                        bottoms = [b + y for b, y in zip(bottoms, y_values)]
                
                ax_bottom_left.set_xticks([x + (bar_width_hourly * (num_logs-1) / 2) for x in range(len(x_labels_hourly))])
                ax_bottom_left.set_xticklabels(x_labels_hourly, rotation=45, ha='right')
                ax_bottom_left.set_ylabel("QSOs per Hour"); ax_bottom_left.set_ylim(0, data['max_hourly_rate'] * 1.1); ax_bottom_left.grid(False)
    
                bar_width_cum = 0.8 / num_logs
                band_indices = range(len(data['bands']))
                for j, call in enumerate(calls):
                    color_shades = _get_color_shades(self.CALLSIGN_COLORS[j % len(self.CALLSIGN_COLORS)])
                    bottoms = [0] * len(data['bands'])
                    current_band_totals = data['log_data'][call]['cum_qso_per_band_breakdown'].loc[hour]
                    for run_state in ['Run', 'S&P', 'Unknown']:
                        y_values = [current_band_totals.get((band, run_state), 0) for band in data['bands']]
                        ax_bottom_right.bar([x - (bar_width_cum * (num_logs - 1) / 2) + j * bar_width_cum for x in band_indices], y_values, width=bar_width_cum, bottom=bottoms, color=color_shades[run_state], alpha=0.8)
                        bottoms = [b + y for b, y in zip(bottoms, y_values)]
    
                ax_bottom_right.set_title("Cumulative QSOs by Band", fontsize=10)
                ax_bottom_right.set_ylabel("Total QSOs"); ax_bottom_right.set_xticks(band_indices)
                ax_bottom_right.set_xticklabels(data['bands']); ax_bottom_right.set_ylim(0, data['max_cum_qso_on_band'] * 1.1)
                
                sample_shades = _get_color_shades(self.CALLSIGN_COLORS[0])
                legend_handles = [plt.Rectangle((0,0),1,1, fc=sample_shades[s]) for s in ['Run', 'S&P', 'Unknown']]
                ax_bottom_legend.legend(legend_handles, ['Run', 'S&P', 'Unknown'], title="QSO Type", loc='center', ncol=3)
    
                frame_path = os.path.join(frame_dir, f"frame_{i:03d}.png")
                plt.savefig(frame_path)
                plt.close(fig_mpl)
    
            logging.info("Compiling video...")
            video_filepath = os.path.join(output_path, f"{self.report_id}_{'_vs_'.join(sorted(calls))}.mp4")
            with imageio.get_writer(video_filepath, fps=self.FPS) as writer:
                for i in range(total_frames):
                    frame_file = os.path.join(frame_dir, f"frame_{i:03d}.png")
                    image = imageio.imread(frame_file)

                    # Use a different duration for the final frame
                    if i == total_frames - 1:
                        duration = self.LAST_FRAME_DURATION_SECONDS
                    else:
                        duration = self.FRAME_DURATION_SECONDS
                    
                    for _ in range(duration * self.FPS):
                        writer.append_data(image)
            logging.info(f"Animation video saved to: {video_filepath}")
        except Exception as e:
            logging.error(f"Failed to create video file. Ensure ffmpeg is installed. Error: {e}")
        finally:
            # Resilient cleanup to handle race condition with ffmpeg file locks
            for i in range(10):
                try:
                    shutil.rmtree(frame_dir)
                    break 
                except OSError as e:
                    if e.errno == errno.EACCES and i < 9:
                        time.sleep(1)
                        continue
                    else:
                        logging.warning(f"Could not remove temp frame directory '{frame_dir}': {e}")
                        break

    def _generate_interactive_html(self, data: Dict, output_path: str):
        logging.info("Interactive HTML generation is planned but not yet implemented in this version.")
        filename_calls = '_vs_'.join(sorted(data['log_data'].keys()))
        html_filename = f"{self.report_id}_{filename_calls}_interactive.html"
        html_filepath = os.path.join(output_path, html_filename)
        with open(html_filepath, 'w') as f:
            f.write("<h1>Interactive Report (Not Yet Implemented)</h1>")
        logging.info(f"Placeholder for interactive report saved to: {html_filepath}")

    def generate(self, output_path: str, **kwargs) -> str:
        create_output_directory(output_path)
        data = self._prepare_data()
        if not data:
            return f"Report '{self.report_name}' skipped: No data to process."

        debug_data_flag = kwargs.get("debug_data", False)
        self._generate_video(data, output_path, debug_data_flag=debug_data_flag)
        self._generate_interactive_html(data, output_path)
        
        return f"Animation report files generated in: {output_path}"