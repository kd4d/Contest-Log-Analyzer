# contest_tools/score_calculators/standard_calculator.py
#
# Purpose: This module provides the default time-series score calculator
#          for all standard contests that do not have complex, stateful
#          scoring rules like QTCs or weighted multipliers.
#
#
# Author: Gemini AI
# Date: 2025-12-11
# Version: 0.102.1-Beta
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
# [0.102.1-Beta] - 2025-12-11
# - Decoupled point/QSO scoring from multiplier filtering to ensure zero-point
#   QSOs still count towards totals if they are valid QSOs.
# - Added enforcement of `mults_from_zero_point_qsos` definition flag to
#   exclude zero-point QSOs from multiplier contribution when required.
# [0.90.4-Beta] - 2025-10-01
# - Added filter to drop QSOs where all multiplier columns are NaN before
#   calculating QSO/Point counts, ensuring alignment with multiplier counts.
# [0.90.2-Beta] - 2025-10-01
# - Corrected scoring logic for `qsos_times_mults` contests. The QSO
#   and Point counts are now derived from the same filtered DataFrame as
#   the multiplier counts, excluding QSOs with "Unknown" multipliers.
# [0.90.1-Beta] - 2025-10-01
# - Corrected a systemic bug in multiplier counting for contests with
#   multiple, non-sum_by_band multiplier types (e.g., NAQP, CQ-160). The
#   logic now correctly calculates the cumulative count for each multiplier
#   type independently before summing them.
# [0.90.0-Beta] - 2025-10-01
# Set new baseline version for release.

import pandas as pd
from typing import TYPE_CHECKING

from .calculator_interface import TimeSeriesCalculator

if TYPE_CHECKING:
    from ..contest_log import ContestLog

class StandardCalculator(TimeSeriesCalculator):
    """
    Default calculator for standard contests. The score is a simple
    cumulative sum of QSO points over time, broken down by operating style.
    """
    def calculate(self, log: 'ContestLog', df_non_dupes: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates a cumulative, time-series final score by multiplying
        cumulative points by cumulative multipliers, with a breakdown for
        Run vs. S&P+Unknown operating styles.
        """
        log_manager = getattr(log, '_log_manager_ref', None)
        master_index = getattr(log_manager, 'master_time_index', None)

        required_cols = ['QSOPoints', 'Datetime', 'Run', 'Call']
        if df_non_dupes.empty or not all(c in df_non_dupes.columns for c in required_cols) or master_index is None:
            return pd.DataFrame()

    
        df_original_sorted = df_non_dupes.dropna(subset=['Datetime', 'QSOPoints']).sort_values(by='Datetime')
        
        # --- Multiplier Counting based on Contest Rules ---
        multiplier_columns = sorted(list(set([rule['value_column'] for rule in log.contest_definition.multiplier_rules])))

        # Create a filtered DataFrame for multiplier counting, excluding "Unknown"
        df_for_mults = df_original_sorted.copy()
        
        # If contest prohibits zero-point mults (e.g. ARRL DX), filter them out now
        if not log.contest_definition.mults_from_zero_point_qsos:
            df_for_mults = df_for_mults[df_for_mults['QSOPoints'] > 0]

        for col in multiplier_columns:
            if col in df_for_mults.columns:
                df_for_mults = df_for_mults[df_for_mults[col] != 'Unknown']
        
        # Also drop rows where all multiplier columns are NaN
        df_for_mults.dropna(subset=multiplier_columns, how='all', inplace=True)

        mult_count_ts = pd.Series(0.0, index=master_index)
        per_band_mult_ts_dict = {}

        # --- Time-series calculation (Points/QSOs based on FULL valid log) ---
        hourly_groups_all = df_original_sorted.set_index('Datetime').groupby(pd.Grouper(freq='h'))
        
        # Cumulative QSO Points
        cum_points_ts = hourly_groups_all['QSOPoints'].sum().cumsum().reindex(master_index, method='ffill').fillna(0)
        run_points_ts = df_original_sorted[df_original_sorted['Run'] == 'Run'].set_index('Datetime')['QSOPoints'].resample('h').sum().cumsum().reindex(master_index, method='ffill').fillna(0)
        sp_unk_points_ts = cum_points_ts - run_points_ts
        
        # Cumulative QSO Counts
        cum_qso_ts = hourly_groups_all.size().cumsum().reindex(master_index, method='ffill').fillna(0)
        run_qso_ts = df_original_sorted[df_original_sorted['Run'] == 'Run'].set_index('Datetime')['Call'].resample('h').count().cumsum().reindex(master_index, method='ffill').fillna(0)
        sp_unk_qso_ts = cum_qso_ts - run_qso_ts

        # Determine if all rules use the simple 'sum_by_band' method.
        all_sum_by_band = all(rule.get('totaling_method', 'sum_by_band') == 'sum_by_band' for rule in log.contest_definition.multiplier_rules)

        if all_sum_by_band:
            for mult_col in multiplier_columns:
                if mult_col in df_for_mults.columns:
                    per_band_groups = df_for_mults.groupby('Band')
                    for band, group_df in per_band_groups:
                        mult_set_ts = group_df.groupby(pd.Grouper(key='Datetime', freq='h'))[mult_col].apply(set).reindex(master_index)
                        mult_set_ts = mult_set_ts.apply(lambda x: x if isinstance(x, set) else set())

                        running_set = set()
                
                        cumulative_sets_list = [running_set.update(s) or running_set.copy() for s in mult_set_ts]

                        band_mult_ts = pd.Series(cumulative_sets_list, index=master_index).apply(len)
                        mult_count_ts += band_mult_ts
                        per_band_mult_ts_dict[f"total_mults_{band}"] = band_mult_ts
     
        else: # once_per_log or once_per_mode
            all_cumulative_mults_ts = []
            for rule in log.contest_definition.multiplier_rules:
                mult_col = rule['value_column']
                if mult_col not in df_for_mults.columns: continue

                # Calculate the cumulative unique set for this multiplier type
                hourly_sets = df_for_mults.groupby(pd.Grouper(key='Datetime', freq='h'))[mult_col].apply(set).reindex(master_index)
                hourly_sets = hourly_sets.apply(lambda x: x if isinstance(x, set) else set())
                
                running_set_for_col = set()
                cumulative_sets_for_col = [running_set_for_col.update(s) or running_set_for_col.copy() for s in hourly_sets]
                
                # Convert the list of sets to a time series of counts
                cumulative_counts_for_col = pd.Series(cumulative_sets_for_col, index=master_index).apply(len)
                all_cumulative_mults_ts.append(cumulative_counts_for_col)

            if all_cumulative_mults_ts:
                # Sum the time series of counts for each multiplier type
                mult_count_ts = pd.concat(all_cumulative_mults_ts, axis=1).sum(axis=1)

        
        # --- Final Score Calculation (Score-Formula-Aware) ---
        score_formula = log.contest_definition.score_formula
        if score_formula == 'total_points':
            final_score_ts = cum_points_ts
        elif score_formula == 'qsos_times_mults':
            final_score_ts = cum_qso_ts * mult_count_ts
        else: # Default to points_times_mults
            final_score_ts = cum_points_ts * mult_count_ts
        run_ratio = (run_points_ts / cum_points_ts).fillna(0)
        sp_unk_ratio = (sp_unk_points_ts / cum_points_ts).fillna(0)
        run_score_ts = final_score_ts * run_ratio
        sp_unk_score_ts = final_score_ts * sp_unk_ratio

        result_df = pd.DataFrame({
            'run_qso_count': run_qso_ts,
            'sp_unk_qso_count': sp_unk_qso_ts,
            'run_score': run_score_ts,
            'sp_unk_score': sp_unk_score_ts,
            'score': final_score_ts,
            'total_mults': mult_count_ts,
        }, index=master_index)
        
        # Add the per-band multiplier time-series to the final result
        for col_name, series in per_band_mult_ts_dict.items():
            result_df[col_name] = series

        return result_df.astype(int)