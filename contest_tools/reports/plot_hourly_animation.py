# Contest Log Analyzer/contest_tools/reports/plot_hourly_animation.py
#
# Version: 0.35.28-Beta
# Date: 2025-08-15
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
from typing import List, Dict

from ..contest_log import ContestLog
from .report_interface import ContestReport
from ._report_utils import create_output_directory, get_valid_dataframe

def _get_color_shades(base_rgb):
    """Generates dark, light, and red shades for Run/S&P/Unknown."""
    h, l, s = colorsys.rgb_to_hls(*base_rgb)
    return {
        'Run': colorsys.hls_to_rgb(h, max(0, l * 0.65), s),      # Darker
        'S&P': colorsys.hls_to_rgb(h, min(1, l * 1.2 + 0.1), s), # Lighter
        'Unknown': '#FF0000'                                   # Bright Red
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

        first_log_def = self.logs[0].contest_definition
        score_formula = first_log_def.score_formula

        min_time = combined_df['Datetime'].min().floor('h')
        max_time = (combined_df['Datetime'].max() - pd.Timedelta(microseconds=1)).ceil('h')
        master_index = pd.date_range(start=min_time, end=max_time, freq='h', tz='UTC')
        
        log_data = {}
        final_scores = {}
        
        hourly_rates_df = combined_df.groupby([combined_df['Datetime'].dt.floor('h'), 'Band', 'MyCall']).size().reset_index(name='QSOs')
        max_hourly_rate = hourly_rates_df['QSOs'].max() if not hourly_rates_df.empty else 1

        for call, log_df in combined_df.groupby('MyCall'):
            cum_qso = log_df.set_index('Datetime')['Call'].resample('h').count().cumsum().reindex(master_index, method='ffill').fillna(0)
            
            cum_mults = pd.Series(0.0, index=master_index)
            for hour in master_index:
                df_slice = log_df[log_df['Datetime'] <= hour]
                total_mults_for_hour = 0
                
                for rule in first_log_def.multiplier_rules:
                    m_col = rule['value_column']
                    totaling_method = rule.get('totaling_method', 'sum_by_band')

                    if m_col in df_slice.columns:
                        df_slice_valid_mults = df_slice[df_slice[m_col].notna() & (df_slice[m_col] != 'Unknown')]
                        if df_slice_valid_mults.empty: continue
                        if totaling_method in ['once_per_band', 'sum_by_band']:
                            total_mults_for_hour += df_slice_valid_mults.groupby('Band')[m_col].nunique().sum()
                        else:
                            total_mults_for_hour += df_slice_valid_mults[m_col].nunique()
                
                cum_mults[hour] = total_mults_for_hour

            if score_formula == 'qsos_times_mults':
                cum_score = cum_qso * cum_mults
            else:
                cum_points = log_df.set_index('Datetime')['QSOPoints'].resample('h').sum().cumsum().reindex(master_index, method='ffill').fillna(0)
                cum_score = cum_points * cum_mults
            
            final_scores[call] = cum_score.iloc[-1]
            
            hourly_run_sp = log_df.groupby([log_df['Datetime'].dt.floor('h'), 'Band', 'Mode', 'Run']).size().unstack(fill_value=0)
            for state in ['Run', 'S&P', 'Unknown']:
                if state not in hourly_run_sp.columns:
                    hourly_run_sp[state] = 0
            
            cum_qso_per_band_breakdown = log_df.groupby([log_df['Datetime'].dt.floor('h'), 'Band', 'Run']).size().unstack(level=['Band', 'Run'], fill_value=0).cumsum()
            cum_qso_per_band_breakdown = cum_qso_per_band_breakdown.reindex(master_index, method='ffill').fillna(0)

            log_data[call] = {
                'cum_qso': cum_qso, 'cum_score': cum_score,
                'hourly_run_sp': hourly_run_sp, 'cum_qso_per_band_breakdown': cum_qso_per_band_breakdown
            }
        
        all_cum_per_band_dfs = [ld['cum_qso_per_band_breakdown'] for ld in log_data.values()]
        max_cum_qso_on_band = 1
        if all_cum_per_band_dfs:
            final_band_totals = pd.concat([df.iloc[[-1]] for df in all_cum_per_band_dfs])
            if not final_band_totals.empty:
                bands = sorted(combined_df['Band'].unique(), key=lambda b: [band[1] for band in ContestLog._HF_BANDS].index(b))
                max_val = 0
                for band in bands:
                    band_cols = [col for col in final_band_totals.columns if col[0] == band]
                    if band_cols:
                        max_val = max(max_val, final_band_totals[band_cols].sum(axis=1).max())
                max_cum_qso_on_band = max_val

        if max_cum_qso_on_band == 0: max_cum_qso_on_band = 1
        max_final_qso = max((ld['cum_qso'].iloc[-1] for ld in log_data.values()), default=1)
        max_final_score = max(final_scores.values(), default=1)
        
        if max_final_qso == 0: max_final_qso = 1
        if max_final_score == 0: max_final_score = 1
        if max_hourly_rate == 0: max_hourly_rate = 1

        return {
            'log_data': log_data, 'master_index': master_index,
            'max_final_qso': max_final_qso, 'max_final_score': max_final_score,
            'max_hourly_rate': max_hourly_rate, 'max_cum_qso_on_band': max_cum_qso_on_band,
            'bands': bands, 'modes': combined_df['Mode'].unique().tolist()
        }

    def _generate_video(self, data: Dict, output_path: str):
        frame_dir = os.path.join(output_path, "temp_frames")
        if os.path.exists(frame_dir): shutil.rmtree(frame_dir)
        os.makedirs(frame_dir)

        logging.info(f"Generating {len(data['master_index'])} frames for animation video...")
        
        total_frames = len(data['master_index'])
        first_log_meta = self.logs[0].get_metadata()
        contest_name = first_log_meta.get('ContestName', 'Unknown Contest')
        year = self.logs[0].get_processed_data()['Date'].iloc[0].split('-')[0]
        event_id = first_log_meta.get('EventID', '')
        calls = list(data['log_data'].keys())
        num_logs = len(calls)

        for i, hour in enumerate(data['master_index']):
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

            fig_mpl.suptitle(f"{year} {event_id} {contest_name}\nHour {i + 1} of {total_frames}")

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
        try:
            with imageio.get_writer(video_filepath, fps=self.FPS) as writer:
                for i in range(total_frames):
                    frame_file = os.path.join(frame_dir, f"frame_{i:03d}.png")
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