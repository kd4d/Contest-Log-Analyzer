# contest_tools/score_calculators/standard_calculator.py
#
# Purpose: This module provides the default time-series score calculator
#          for all standard contests that do not have complex, stateful
#          scoring rules like QTCs or weighted multipliers.
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

        # --- Multiplier Counting: Handle different totaling_methods ---
        # Process each multiplier rule according to its totaling_method
        all_cumulative_mults_ts = []
        
        for rule in log.contest_definition.multiplier_rules:
            mult_col = rule['value_column']
            if mult_col not in df_for_mults.columns:
                continue
            
            totaling_method = rule.get('totaling_method', 'sum_by_band')
            
            if totaling_method == 'once_per_log':
                # Count unique multipliers globally (once per log)
                # Filter out NaN values before applying set (NaN is a placeholder, not a valid multiplier)
                hourly_sets = df_for_mults.groupby(pd.Grouper(key='Datetime', freq='h'))[mult_col].apply(lambda x: set(x.dropna())).reindex(master_index)
                hourly_sets = hourly_sets.apply(lambda x: x if isinstance(x, set) else set())
                
                running_set_for_col = set()
                cumulative_sets_for_col = [running_set_for_col.update(s) or running_set_for_col.copy() for s in hourly_sets]
                
                cumulative_counts_for_col = pd.Series(cumulative_sets_for_col, index=master_index).apply(len)
                all_cumulative_mults_ts.append(cumulative_counts_for_col)
                
            elif totaling_method == 'once_per_mode':
                # Count unique multipliers per mode, then sum across modes (matches ScoreStatsAggregator logic)
                # Group by mode, then for each mode calculate unique multipliers over time
                mode_cumulative_counts = []
                
                for mode in df_for_mults['Mode'].unique():
                    df_mode = df_for_mults[df_for_mults['Mode'] == mode]
                    # Filter out NaN values before applying set (NaN is a placeholder, not a valid multiplier)
                    hourly_sets = df_mode.groupby(pd.Grouper(key='Datetime', freq='h'))[mult_col].apply(lambda x: set(x.dropna())).reindex(master_index)
                    hourly_sets = hourly_sets.apply(lambda x: x if isinstance(x, set) else set())
                    
                    running_set_for_mode = set()
                    cumulative_sets_for_mode = [running_set_for_mode.update(s) or running_set_for_mode.copy() for s in hourly_sets]
                    mode_counts = pd.Series(cumulative_sets_for_mode, index=master_index).apply(len)
                    mode_cumulative_counts.append(mode_counts)
                
                # Sum across all modes
                if mode_cumulative_counts:
                    rule_total_ts = pd.concat(mode_cumulative_counts, axis=1).sum(axis=1)
                    all_cumulative_mults_ts.append(rule_total_ts)
                    
            elif totaling_method == 'once_per_band_no_mode':
                # Count unique multipliers per band (ignoring mode)
                for band in df_for_mults['Band'].unique():
                    df_band = df_for_mults[df_for_mults['Band'] == band]
                    # Filter out NaN values before applying set (NaN is a placeholder, not a valid multiplier)
                    mult_set_ts = df_band.groupby(pd.Grouper(key='Datetime', freq='h'))[mult_col].apply(lambda x: set(x.dropna())).reindex(master_index)
                    mult_set_ts = mult_set_ts.apply(lambda x: x if isinstance(x, set) else set())
                    
                    running_set = set()
                    cumulative_sets_list = [running_set.update(s) or running_set.copy() for s in mult_set_ts]
                    
                    band_mult_ts = pd.Series(cumulative_sets_list, index=master_index).apply(len)
                    mult_count_ts += band_mult_ts
                    per_band_mult_ts_dict[f"total_mults_{band}"] = band_mult_ts
                    
            else:  # Default: sum_by_band
                # Count unique multipliers per band, then sum across bands (matches ScoreStatsAggregator logic)
                for band in df_for_mults['Band'].unique():
                    df_band = df_for_mults[df_for_mults['Band'] == band]
                    # Filter out NaN values before applying set (NaN is a placeholder, not a valid multiplier)
                    mult_set_ts = df_band.groupby(pd.Grouper(key='Datetime', freq='h'))[mult_col].apply(lambda x: set(x.dropna())).reindex(master_index)
                    mult_set_ts = mult_set_ts.apply(lambda x: x if isinstance(x, set) else set())
                    
                    running_set = set()
                    cumulative_sets_list = [running_set.update(s) or running_set.copy() for s in mult_set_ts]
                    
                    band_mult_ts = pd.Series(cumulative_sets_list, index=master_index).apply(len)
                    mult_count_ts += band_mult_ts
                    per_band_mult_ts_dict[f"total_mults_{band}"] = band_mult_ts

        # Sum all multiplier rules that were calculated per-rule (once_per_log, once_per_mode)
        if all_cumulative_mults_ts:
            rule_based_mults_ts = pd.concat(all_cumulative_mults_ts, axis=1).sum(axis=1)
            mult_count_ts += rule_based_mults_ts

        
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