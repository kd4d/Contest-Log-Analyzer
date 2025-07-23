# Contest Log Analyzer/contest_tools/core_annotations/run_s_p.py
#
# Purpose: This utility infers whether each contact in an amateur radio contest log
#          was made while "Running" (CQing) or "Search & Pounce" (S&P). It adds a
#          'Run' column to the log, classifying each QSO accordingly.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-23
# Version: 0.14.3-Beta
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

## [0.14.3-Beta] - 2025-07-23
### Fixed
# - Corrected the "sticky run" logic to only break a run if the consecutive
#   off-frequency QSOs are on the same new frequency, not on multiple
#   different S&P frequencies.

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
RUN_BREAK_QSO_COUNT = 3
RUN_BREAK_TIME_MINUTES = 2

def _get_run_info_from_buffer(base_freq: float, buffer_to_check: deque, min_qso: int, time_threshold: pd.Timedelta, tol: float):
    """
    Helper to check if a given `base_freq` forms a valid run within the `buffer_to_check`.
    """
    relevant_qso_data = []
    for buffered_idx, buffered_time, buffered_freq in buffer_to_check:
        if abs(buffered_freq - base_freq) <= tol:
            relevant_qso_data.append((buffered_idx, buffered_time))

    if len(relevant_qso_data) < min_qso:
        return False, []

    # Check from the most recent QSOs backwards
    for i in range(len(relevant_qso_data) - 1, min_qso - 2, -1):
        latest_time_in_segment = relevant_qso_data[i][1]
        oldest_time_in_segment = relevant_qso_data[i - (min_qso - 1)][1]
        if (latest_time_in_segment - oldest_time_in_segment) <= time_threshold:
            qualifying_indices = [q[0] for q in relevant_qso_data[i - (min_qso - 1) : i + 1]]
            return True, qualifying_indices
    return False, []

def _evaluate_single_stream_run(
    stream_df_original: pd.DataFrame, 
    datetime_column: str,
    frequency_column: str,
    stream_tolerance: float,
    time_delta_threshold: pd.Timedelta,
    min_qso_for_run: int
):
    """
    Evaluates run status for a single operational stream using a "sticky run" state machine.
    """
    inferred_run_status = ['S&P'] * len(stream_df_original)
    original_idx_to_list_pos = {idx: i for i, idx in enumerate(stream_df_original.index)}

    active_run_freq = None
    last_qso_on_run_freq_time = None
    off_frequency_qso_count = 0
    potential_new_run_freq = None # Track the frequency of consecutive S&P QSOs
    qso_buffer = deque()

    for list_pos, original_df_idx in enumerate(stream_df_original.index):
        current_qso_time = stream_df_original.at[original_df_idx, datetime_column]
        current_qso_freq = stream_df_original.at[original_df_idx, frequency_column]
        
        qso_buffer.append((original_df_idx, current_qso_time, current_qso_freq))
        while qso_buffer and (current_qso_time - qso_buffer[0][1]) > time_delta_threshold:
            qso_buffer.popleft()

        # --- Main State Machine: Prioritize maintaining an existing run ---
        if active_run_freq is not None:
            is_on_run_freq = abs(current_qso_freq - active_run_freq) <= stream_tolerance
            timed_out = (current_qso_time - last_qso_on_run_freq_time) > pd.Timedelta(minutes=RUN_BREAK_TIME_MINUTES)

            if is_on_run_freq and not timed_out:
                inferred_run_status[list_pos] = 'Run'
                last_qso_on_run_freq_time = current_qso_time
                off_frequency_qso_count = 0
                potential_new_run_freq = None
            else:
                inferred_run_status[list_pos] = 'S&P'
                if not is_on_run_freq:
                    # Check if this S&P QSO continues a potential new run
                    if potential_new_run_freq and abs(current_qso_freq - potential_new_run_freq) <= stream_tolerance:
                        off_frequency_qso_count += 1
                    else: # It's a new S&P frequency, reset the counter
                        potential_new_run_freq = current_qso_freq
                        off_frequency_qso_count = 1
                
                if timed_out or off_frequency_qso_count >= RUN_BREAK_QSO_COUNT:
                    active_run_freq = None # Break the run
        
        # --- If no run is active, check if a new one has formed ---
        if active_run_freq is None:
            is_new_run, new_run_indices = _get_run_info_from_buffer(
                current_qso_freq, qso_buffer, min_qso_for_run, time_delta_threshold, stream_tolerance
            )
            if is_new_run:
                active_run_freq = current_qso_freq
                last_qso_on_run_freq_time = current_qso_time
                off_frequency_qso_count = 0
                potential_new_run_freq = None
                for idx in new_run_indices:
                    if idx in original_idx_to_list_pos:
                        inferred_run_status[original_idx_to_list_pos[idx]] = 'Run'
            else:
                inferred_run_status[list_pos] = 'S&P'

    return pd.Series(inferred_run_status, index=stream_df_original.index, dtype=str)

def process_contest_log_for_run_s_p(
    df: pd.DataFrame,
    my_call_column: str = 'MyCall',
    datetime_column: str = 'Datetime',
    frequency_column: str = 'Frequency',
    mode_column: str = 'Mode',
    band_column: str = 'Band'
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
        
        processed_df[datetime_column] = pd.to_datetime(processed_df[datetime_column], errors='coerce')
        processed_df[frequency_column] = pd.to_numeric(processed_df[frequency_column], errors='coerce')
        processed_df.dropna(subset=[datetime_column, frequency_column], inplace=True)

        for col in [my_call_column, mode_column, band_column]:
            processed_df[col] = processed_df[col].astype(str)

        if 'Run' in processed_df.columns:
            processed_df.drop(columns=['Run'], inplace=True)

        df_sorted = processed_df.sort_values(by=[my_call_column, band_column, mode_column, datetime_column])
        time_delta_threshold = pd.Timedelta(minutes=DEFAULT_RUN_TIME_WINDOW_MINUTES) + pd.Timedelta(seconds=1)
        
        results = []
        for group_name, group_df in df_sorted.groupby([my_call_column, band_column, mode_column], group_keys=False):
            representative_mode = group_name[2]
            stream_tolerance = DEFAULT_FREQ_TOLERANCE_CW if representative_mode.upper() == 'CW' else DEFAULT_FREQ_TOLERANCE_PH
            
            group_results_series = _evaluate_single_stream_run(
                group_df, datetime_column, frequency_column, stream_tolerance,
                time_delta_threshold, DEFAULT_MIN_QSO_FOR_RUN
            )
            results.append(group_results_series)
        
        if results:
            run_column_series = pd.concat(results)
            processed_df['Run'] = run_column_series
        else:
            processed_df['Run'] = 'S&P'

        return processed_df

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
