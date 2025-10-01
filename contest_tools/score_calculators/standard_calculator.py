# contest_tools/score_calculators/standard_calculator.py
#
# Purpose: This module provides the default time-series score calculator
#          for all standard contests that do not have complex, stateful
#          scoring rules like QTCs or weighted multipliers.
#
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

        df_sorted = df_non_dupes.dropna(subset=['Datetime', 'QSOPoints']).sort_values(by='Datetime')
        
        # --- Time-series calculation ---
        hourly_groups = df_sorted.set_index('Datetime').groupby(pd.Grouper(freq='h'))
        
        # Cumulative QSO Points
        cum_points_ts = hourly_groups['QSOPoints'].sum().cumsum().reindex(master_index, method='ffill').fillna(0)
        run_points_ts = df_sorted[df_sorted['Run'] == 'Run'].set_index('Datetime')['QSOPoints'].resample('h').sum().cumsum().reindex(master_index, method='ffill').fillna(0)
        sp_unk_points_ts = cum_points_ts - run_points_ts
        
        # Cumulative QSO Counts
        cum_qso_ts = hourly_groups.size().cumsum().reindex(master_index, method='ffill').fillna(0)
        run_qso_ts = df_sorted[df_sorted['Run'] == 'Run'].set_index('Datetime')['Call'].resample('h').count().cumsum().reindex(master_index, method='ffill').fillna(0)
        sp_unk_qso_ts = cum_qso_ts - run_qso_ts
        
        # --- Multiplier Counting based on Contest Rules ---
        multiplier_columns = sorted(list(set([rule['value_column'] for rule in log.contest_definition.multiplier_rules])))

        per_band_mult_ts_dict = {}
        # Create a filtered DataFrame for multiplier counting, excluding "Unknown"
        df_for_mults = df_sorted.copy()
        for col in multiplier_columns:
            if col in df_for_mults.columns:
                df_for_mults = df_for_mults[df_for_mults[col] != 'Unknown']

        totaling_method = log.contest_definition.multiplier_rules[0].get('totaling_method', 'sum_by_band') if log.contest_definition.multiplier_rules else 'sum_by_band'

        mult_count_ts = pd.Series(0.0, index=master_index)
        if totaling_method == 'sum_by_band':
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
            all_mult_sets_list = []
            for mult_col in multiplier_columns:
                if mult_col in df_for_mults.columns:
                    mult_set_ts = df_for_mults.groupby(pd.Grouper(key='Datetime', freq='h'))[mult_col].apply(set)
                    all_mult_sets_list.append(mult_set_ts)

            if not all_mult_sets_list:
                all_mult_sets = pd.Series([set()] * len(master_index), index=master_index)
            else:
                combined_series = pd.concat(all_mult_sets_list, axis=1).fillna(0)
                all_mult_sets = combined_series.apply(lambda row: set.union(*[s for s in row if isinstance(s, set)]), axis=1)
            all_mult_sets = all_mult_sets.reindex(master_index)

            all_mult_sets = all_mult_sets.apply(lambda x: x if isinstance(x, set) else set())
            running_set = set()
            cumulative_sets_list = [running_set.update(s) or running_set.copy() for s in all_mult_sets]
            mult_count_ts = pd.Series(cumulative_sets_list, index=master_index).apply(len)
        
        
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
