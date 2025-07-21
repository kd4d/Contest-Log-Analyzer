# Contest Log Analyzer/contest_tools/core_annotations/run_s_p.py
#
# Purpose: This utility infers whether each contact in an amateur radio contest log
#          was made while "Running" (CQing) or "Search & Pounce" (S&P). It adds a
#          'Run' column to the log, classifying each QSO accordingly.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-21
# Version: 0.10.0-Beta
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
# All notable changes to this project will be documented in this file.
# The format is based on "Keep a Changelog" (https://keepachangelog.com/en/1.0.0/),
# and this project aims to adhere to Semantic Versioning (https://semver.org/).

## [0.10.0-Beta] - 2025-07-21
# - Updated version for consistency with new reporting structure.

### Changed
# - (None)

### Fixed
# - (None)

### Removed
# - (None)

import pandas as pd
from collections import deque
import os
import sys
import traceback

# --- Constants ---
DEFAULT_RUN_TIME_WINDOW_MINUTES = 10
DEFAULT_FREQ_TOLERANCE_CW = 0.1
DEFAULT_FREQ_TOLERANCE_PH = 0.5
DEFAULT_MIN_QSO_FOR_RUN = 3

# --- Core Inference Logic (internal helper function) ---
def _infer_run_s_and_p_logic(
    df: pd.DataFrame,
    my_call_column: str,
    datetime_column: str,
    frequency_column: str,
    mode_column: str,
    band_column: str,
    run_time_window_minutes: int,
    freq_tolerance_cw: float,
    freq_tolerance_ph: float,
    min_qso_for_run: int
) -> pd.DataFrame:
    """
    Internal helper to infer "Run" or "S&P" status for QSO records.
    """
    df_sorted = df.sort_values(by=[my_call_column, band_column, mode_column, datetime_column]).copy()
    df_sorted['Inferred_Run'] = 'S&P'
    time_delta_threshold = pd.Timedelta(minutes=run_time_window_minutes) + pd.Timedelta(seconds=1)

    def _get_run_info_from_buffer(base_freq: float, buffer_to_check: deque, min_qso: int, time_threshold: pd.Timedelta, tol: float):
        relevant_qso_data = []
        for buffered_idx, buffered_time, buffered_freq in buffer_to_check:
            if abs(buffered_freq - base_freq) <= tol:
                relevant_qso_data.append((buffered_idx, buffered_time))

        if len(relevant_qso_data) < min_qso:
            return False, []

        for i in range(min_qso - 1, len(relevant_qso_data)):
            latest_time_in_segment = relevant_qso_data[i][1]
            oldest_time_in_segment = relevant_qso_data[i - (min_qso - 1)][1]
            if (latest_time_in_segment - oldest_time_in_segment) <= time_threshold:
                qualifying_indices = [q[0] for q in relevant_qso_data[i - (min_qso - 1) : i + 1]]
                return True, qualifying_indices
        return False, []

    def _evaluate_single_stream_run(stream_df_original: pd.DataFrame, stream_tolerance: float):
        inferred_run_status_raw_list = ['S&P'] * len(stream_df_original)
        original_idx_to_list_pos = {idx: i for i, idx in enumerate(stream_df_original.index)}
        all_recent_qso_buffer = deque()
        active_run_freq = None

        for local_list_pos in range(len(stream_df_original)):
            original_df_idx = stream_df_original.index[local_list_pos]
            current_qso_time = stream_df_original.at[original_df_idx, datetime_column]
            current_qso_freq = stream_df_original.at[original_df_idx, frequency_column]

            while all_recent_qso_buffer and (current_qso_time - all_recent_qso_buffer[0][1]) > time_delta_threshold:
                all_recent_qso_buffer.popleft()
            all_recent_qso_buffer.append((original_df_idx, current_qso_time, current_qso_freq))

            if active_run_freq is not None:
                if abs(current_qso_freq - active_run_freq) > stream_tolerance:
                    active_run_freq = None
                    inferred_run_status_raw_list[original_idx_to_list_pos[original_df_idx]] = 'S&P'
                else:
                    is_active_run_still_valid, segment_indices = _get_run_info_from_buffer(active_run_freq, all_recent_qso_buffer, min_qso_for_run, time_delta_threshold, stream_tolerance)
                    if is_active_run_still_valid:
                        for idx in segment_indices:
                            inferred_run_status_raw_list[original_idx_to_list_pos[idx]] = 'Run'
                    else:
                        active_run_freq = None
                        inferred_run_status_raw_list[original_idx_to_list_pos[original_df_idx]] = 'S&P'

            if active_run_freq is None:
                is_new_run, new_run_indices = _get_run_info_from_buffer(current_qso_freq, all_recent_qso_buffer, min_qso_for_run, time_delta_threshold, stream_tolerance)
                if is_new_run:
                    active_run_freq = current_qso_freq
                    for idx in new_run_indices:
                        inferred_run_status_raw_list[original_idx_to_list_pos[idx]] = 'Run'

        return pd.Series(inferred_run_status_raw_list, index=stream_df_original.index, dtype=str)

    grouped_df_object = df_sorted.groupby([my_call_column, band_column, mode_column], group_keys=True)
    for group_name, group_df_original in grouped_df_object:
        representative_mode = group_name[2]
        stream_tolerance = freq_tolerance_cw if representative_mode.upper() == 'CW' else freq_tolerance_ph
        group_results_series = _evaluate_single_stream_run(group_df_original, stream_tolerance)
        df_sorted.loc[group_results_series.index, 'Inferred_Run'] = group_results_series

    return df_sorted

def process_contest_log_for_run_s_p(
    df: pd.DataFrame,
    my_call_column: str = 'MyCall',
    datetime_column: str = 'Datetime',
    frequency_column: str = 'Frequency',
    mode_column: str = 'Mode',
    band_column: str = 'Band',
    run_time_window_minutes: int = DEFAULT_RUN_TIME_WINDOW_MINUTES,
    freq_tolerance_cw: float = DEFAULT_FREQ_TOLERANCE_CW,
    freq_tolerance_ph: float = DEFAULT_FREQ_TOLERANCE_PH,
    min_qso_for_run: int = DEFAULT_MIN_QSO_FOR_RUN
) -> pd.DataFrame:
    """
    Main wrapper function to infer "Run" or "S&P" status for each QSO in a DataFrame.
    """
    processed_df = df.copy()
    try:
        required_cols = [my_call_column, datetime_column, frequency_column, mode_column, band_column]
        for col in required_cols:
            if col not in processed_df.columns:
                raise KeyError(f"Missing required column for Run/S&P processing: '{col}'")
        
        # Ensure correct data types before processing
        processed_df[datetime_column] = pd.to_datetime(processed_df[datetime_column], errors='coerce')
        processed_df[frequency_column] = pd.to_numeric(processed_df[frequency_column], errors='coerce')
        processed_df.dropna(subset=[datetime_column, frequency_column], inplace=True)

        for col in [my_call_column, mode_column, band_column]:
            processed_df[col] = processed_df[col].astype(str)

        if 'Run' in processed_df.columns:
            processed_df.drop(columns=['Run'], inplace=True)

        processed_df_with_run = _infer_run_s_and_p_logic(
            processed_df, my_call_column, datetime_column, frequency_column, mode_column, band_column,
            run_time_window_minutes, freq_tolerance_cw, freq_tolerance_ph, min_qso_for_run
        )
        processed_df_with_run.rename(columns={'Inferred_Run': 'Run'}, inplace=True)
        return processed_df_with_run

    except KeyError as e:
        raise KeyError(f"Error during Run/S&P pre-processing: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during Run/S&P processing: {e}")
        traceback.print_exc()
        raise

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_s_p.py <input_csv_file_path>")
        sys.exit(1)

    csv_file_path = sys.argv[1]
    
    try:
        initial_df = pd.read_csv(csv_file_path, sep=',', header=0, dtype=str)
        base_name = os.path.splitext(csv_file_path)[0]
        output_file_path = f"{base_name}_Run.csv"

        processed_df = process_contest_log_for_run_s_p(df=initial_df)
        
        # Prepare for output
        df_for_output = processed_df.copy()
        if 'Datetime' in df_for_output.columns:
             df_for_output['Datetime'] = pd.to_datetime(df_for_output['Datetime']).dt.strftime('%Y-%m-%d %H:%M:%S')
        df_for_output = df_for_output.sort_values(by='Datetime', na_position='last').reset_index(drop=True)
        df_for_output.to_csv(output_file_path, index=False)

        print(f"\n--- Processing Complete ---")
        print(f"Processed CSV file created at: {output_file_path}")
        
        if not processed_df.empty:
            print("\nSummary of Inferred Run counts:")
            print(processed_df['Run'].value_counts())

    except Exception as e:
        print(f"Script execution terminated due to an error: {e}")
        sys.exit(1)
