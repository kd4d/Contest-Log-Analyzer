# Contest Log Analyzer/contest_tools/reports/plot_hourly_animation.py
#
# Version: 0.35.3-Beta
# Date: 2025-08-14
#
# Purpose: A plot report that generates a series of hourly images and compiles
#          them into an animated video showing contest progression. It also
#          creates a standalone interactive HTML version of the chart.
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
## [0.35.3-Beta] - 2025-08-14
### Fixed
# - Corrected the top bar chart to position the Score axis on top and the
#   QSO axis on the bottom. Disabled scientific notation on the Score axis.
## [0.35.2-Beta] - 2025-08-14
### Fixed
# - Corrected the cumulative multiplier calculation to properly sum multipliers
#   per band, fixing the scoring logic for contests like NAQP.
## [0.35.1-Beta] - 2025-08-13
### Fixed
# - Added a safeguard to prevent axis limits from being set to zero when
#   all logs have a score of zero, resolving a Matplotlib UserWarning.
## [0.35.0-Beta] - 2025-08-13
### Changed
# - Refactored score calculation to be data-driven, using the new
#   `score_formula` from the contest definition.
import pandas as pd
import os
import logging
import imageio.v2 as imageio
import shutil
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from typing import List, Dict

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import create_output_directory, get_valid_dataframe

class Report(ContestReport):
    report_id = "hourly_animation"
    report_name = "Hourly Rate Animation"
    report_type = "animation"
    supports_single = True
    supports_multi = True

    # --- Configuration ---
    FPS = 10
    FRAME_DURATION_SECONDS = 2
    IMAGE_WIDTH_PX = 1280
    IMAGE_HEIGHT_PX = 720
    DPI = 100
    
    RUN_STATE_HATCHES = {'Run': '/', 'S&P': '\\', 'Unknown': 'x'}
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

        first_log_def = self.logs[0].contest_definition
        score_formula = first_log_def.score_formula

        min_time, max_time = combined_df['Datetime'].min().floor('h'), combined_df['Datetime'].max().ceil('h')
        master_index = pd.date_range(start=min_time, end=max_time, freq='h', tz='UTC')
        
        log_data = {}
        final_scores = {}
        
        hourly_rates_df = combined_df.groupby([combined_df['Datetime'].dt.floor('h'), 'Band', 'MyCall']).size().reset_index(name='QSOs')
        max_hourly_rate = hourly_rates_df['QSOs'].max() if not hourly_rates_df.empty else 1

        for call, log_df in combined_df.groupby('MyCall'):
            cum_qso = log_df.set_index('Datetime')['Call'].resample('h').count().cumsum().reindex(master_index, method='ffill').fillna(0)
            
            # --- Correct Multiplier Calculation Logic ---
            cum_mults = pd.Series(0.0, index=master_index)
            for hour in master_index:
                df_slice = log_df[log_df['Datetime'] <= hour]
                total_mults_for_hour = 0
                
                for rule in first_log_def.multiplier_rules:
                    m_col = rule['value_column']
                    totaling_method = rule.get('totaling_method', 'sum_by_band')

                    if m_col in df_slice.columns:
                        df_slice_valid_mults = df_slice[df_slice[m_col].notna() & (df_slice[m_col] != 'Unknown')]
                        if df_slice_valid_mults.empty:
                            continue

                        if totaling_method in ['once_per_band', 'sum_by_band']:
                            per_band_counts = df_slice_valid_mults.groupby('Band')[m_col].nunique()
                            total_mults_for_hour += per_band_counts.sum()
                        else: # 'once_per_log' or 'once_per_contest'
                            total_mults_for_hour += df_slice_valid_mults[m_col].nunique()
                
                cum_mults[hour] = total_mults_for_hour

            if score_formula == 'qsos_times_mults':
                cum_score = cum_qso * cum_mults
            else: # Default to points_times_mults
                cum_points = log_df.set_index('Datetime')['QSOPoints'].resample('h').sum().cumsum().reindex(master_index, method='ffill').fillna(0)
                cum_score = cum_points * cum_mults
            
            final_scores[call] = cum_score.iloc[-1]
            
            hourly_run_sp = log_df.groupby([log_df['Datetime'].dt.floor('h'), 'Band', 'Mode', 'Run']).size().unstack(fill_value=0)

            log_data[call] = {
                'cum_qso': cum_qso,
                'cum_score': cum_score,
                'hourly_run_sp': hourly_run_sp
            }
        
        max_final_qso = max(ld['cum_qso'].iloc[-1] for ld in log_data.values()) if log_data else 1
        max_final_score = max(final_scores.values()) if final_scores else 1
        
        # --- Safeguard against zero max values ---
        if max_final_qso == 0: max_final_qso = 1
        if max_final_score == 0: max_final_score = 1
        if max_hourly_rate == 0: max_hourly_rate = 1

        return {
            'log_data': log_data, 'master_index': master_index,
            'max_final_qso': max_final_qso, 'max_final_score': max_final_score, 'max_hourly_rate': max_hourly_rate,
            'bands': sorted(combined_df['Band'].unique(), key=lambda b: [band[1] for band in ContestLog._HF_BANDS].index(b)),
            'modes': combined_df['Mode'].unique().tolist()
        }

    def _generate_video(self, data: Dict, output_path: str):
        """Generates the MP4 video using Matplotlib for frames."""
        frame_dir = os.path.join(output_path, "temp_frames")
        if os.path.exists(frame_dir): shutil.rmtree(frame_dir)
        os.makedirs(frame_dir)

        logging.info(f"Generating {len(data['master_index'])} frames for animation video...")
        frame_files = []
        
        total_frames = len(data['master_index'])
        
        first_log_meta = self.logs[0].get_metadata()
        contest_name = first_log_meta.get('ContestName', 'Unknown Contest')
        year = self.logs[0].get_processed_data()['Date'].iloc[0].split('-')[0]
        event_id = first_log_meta.get('EventID', '')

        for i, hour in enumerate(data['master_index']):
            fig_mpl, (ax_top, ax_bottom) = plt.subplots(2, 1, figsize=(self.IMAGE_WIDTH_PX / self.DPI, self.IMAGE_HEIGHT_PX / self.DPI),
                                                        gridspec_kw={'height_ratios': [0.25, 0.75]}, dpi=self.DPI)
            
            # --- Axis Configuration ---
            ax_qso = ax_top  # Bottom bar, bottom axis
            ax_score = ax_top.twiny() # Top bar, top axis

            calls = list(data['log_data'].keys())
            
            for j, call in enumerate(calls):
                score = data['log_data'][call]['cum_score'].get(hour, 0)
                qsos = data['log_data'][call]['cum_qso'].get(hour, 0)
                bar_color = self.CALLSIGN_COLORS[j % len(self.CALLSIGN_COLORS)]
                
                # Plot Score on the top bar (y=j+0.2), controlled by the top axis (ax_score)
                ax_score.barh(j + 0.2, score, height=0.4, align='center', color=bar_color, label=call)
                ax_score.text(score, j + 0.2, f' {score:,.0f}', va='center', ha='left')

                # Plot QSOs on the bottom bar (y=j-0.2), controlled by the bottom axis (ax_qso)
                ax_qso.barh(j - 0.2, qsos, height=0.4, align='center', color=bar_color, alpha=0.6)
                ax_qso.text(qsos, j - 0.2, f' {qsos:,.0f}', va='center', ha='left')
            
            # Configure bottom axis (QSOs)
            ax_qso.set_yticks(range(len(calls)))
            ax_qso.set_yticklabels([f"{c}\nScore\nQSOs" for c in calls])
            ax_qso.tick_params(axis='y', length=0)
            ax_qso.set_xlim(0, data['max_final_qso'])
            ax_qso.set_xlabel("Cumulative QSOs")

            # Configure top axis (Score)
            ax_score.set_xlim(0, data['max_final_score'])
            ax_score.set_xlabel("Cumulative Score")
            ax_score.xaxis.set_ticks_position('top')
            ax_score.xaxis.set_label_position('top')
            ax_score.xaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))

            legend_pos = 'lower left' if i > total_frames / 2 else 'lower right'
            ax_score.legend(loc=legend_pos, title="Callsign")
            
            x_labels = [f"{b}-{m}" for b in data['bands'] for m in data['modes']]
            bar_width = 0.8 / len(calls)
            
            for j, call in enumerate(calls):
                bottoms = [0] * len(x_labels)
                for run_state in ['Run', 'S&P', 'Unknown']:
                    hatch = self.RUN_STATE_HATCHES[run_state]
                    y_values = []
                    for band in data['bands']:
                        for mode in data['modes']:
                            try:
                                count = data['log_data'][call]['hourly_run_sp'].loc[(hour, band, mode), run_state]
                            except KeyError:
                                count = 0
                            y_values.append(count)
                    
                    ax_bottom.bar([x + j * bar_width for x in range(len(x_labels))], y_values,
                                  width=bar_width, bottom=bottoms, color=self.CALLSIGN_COLORS[j % len(self.CALLSIGN_COLORS)],
                                  hatch=hatch, edgecolor='white', alpha=0.8)
                    bottoms = [b + y for b, y in zip(bottoms, y_values)]
            
            ax_bottom.set_xticks([x + (bar_width * (len(calls)-1) / 2) for x in range(len(x_labels))])
            ax_bottom.set_xticklabels(x_labels, rotation=45, ha='right')
            ax_bottom.set_ylabel("QSOs per Hour")
            ax_bottom.set_ylim(0, data['max_hourly_rate'] * 1.1)
            ax_bottom.grid(False)

            hatch_legend_handles = [plt.Rectangle((0,0),1,1, facecolor='grey', edgecolor='black', hatch=h) for h in self.RUN_STATE_HATCHES.values()]
            ax_bottom.legend(hatch_legend_handles, self.RUN_STATE_HATCHES.keys(), title="QSO Type", loc='best')

            title_line_1 = f"{year} {event_id} {contest_name}"
            title_line_2 = f"Hour {i + 1} of {total_frames}"
            fig_mpl.suptitle(f"{title_line_1}\n{title_line_2}")
            fig_mpl.tight_layout(rect=[0, 0.03, 1, 0.93])

            frame_path = os.path.join(frame_dir, f"frame_{i:03d}.png")
            plt.savefig(frame_path)
            plt.close(fig_mpl)
            frame_files.append(frame_path)

        logging.info("Compiling video...")
        video_filename = f"{self.report_id}_{'_vs_'.join(sorted(data['log_data'].keys()))}.mp4"
        video_filepath = os.path.join(output_path, video_filename)
        
        try:
            with imageio.get_writer(video_filepath, fps=self.FPS) as writer:
                for frame_file in frame_files:
                    image = imageio.imread(frame_file)
                    for _ in range(self.FRAME_DURATION_SECONDS * self.FPS):
                        writer.append_data(image)
            logging.info(f"Animation video saved to: {video_filepath}")
        except Exception as e:
            logging.error(f"Failed to create video file. Ensure ffmpeg is installed. Error: {e}")
        finally:
            shutil.rmtree(frame_dir)

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

        self._generate_video(data, output_path)
        self._generate_interactive_html(data, output_path)
        
        return f"Animation report files generated in: {output_path}"