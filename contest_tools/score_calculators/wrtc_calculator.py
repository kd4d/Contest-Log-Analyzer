# contest_tools/score_calculators/wrtc_calculator.py
#
# Purpose: This module provides the contest-specific time-series
#          score calculator for the WRTC Contest series.
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
import logging
from typing import TYPE_CHECKING

from .calculator_interface import TimeSeriesCalculator

if TYPE_CHECKING:
    from ..contest_log import ContestLog

class WrtcCalculator(TimeSeriesCalculator):
    """
    Calculates the time-series score for WRTC contests.
    Score = (Total Points) * (Total Multipliers)
    Multipliers = Sum of unique multipliers worked on each band, ignoring mode.
    """
    def calculate(self, log: 'ContestLog', df_non_dupes: pd.DataFrame) -> pd.DataFrame:
        log_manager = getattr(log, '_log_manager_ref', None)
        master_index = getattr(log_manager, 'master_time_index', None)

        required_cols = ['QSOPoints', 'Datetime', 'Run', 'Call']
        if df_non_dupes.empty or not all(c in df_non_dupes.columns for c in required_cols) or master_index is None:
            return pd.DataFrame()

        df_sorted = df_non_dupes.dropna(subset=['Datetime', 'QSOPoints']).sort_values(by='Datetime')

        # --- Multiplier Counting ---
        # For WRTC, multipliers are mutually exclusive (DXCC, HQ, Official)
        # Count unique multipliers per band (once_per_band_no_mode), then sum across bands
        multiplier_columns = sorted(list(set([rule['value_column'] for rule in log.contest_definition.multiplier_rules])))

        df_for_mults = df_sorted.copy()
        # Filter out 'Unknown' values
        for col in multiplier_columns:
            if col in df_for_mults.columns:
                df_for_mults = df_for_mults[df_for_mults[col] != 'Unknown']
        # Keep rows where at least one multiplier column has a value (mutually exclusive)
        df_for_mults.dropna(subset=multiplier_columns, how='all', inplace=True)

        mult_count_ts = pd.Series(0.0, index=master_index)
        per_band_mult_ts_dict = {}

        # For once_per_band_no_mode: Count unique multipliers per band, then sum across bands
        # Process each multiplier rule separately, then sum the results
        for mult_col in multiplier_columns:
            if mult_col not in df_for_mults.columns:
                continue
                
            # Filter to rows where this multiplier column has a value
            df_col_mults = df_for_mults[df_for_mults[mult_col].notna()].copy()
            
            if df_col_mults.empty:
                continue
            
            # Group by band and count unique multipliers per band over time
            per_band_groups = df_col_mults.groupby('Band')
            for band, group_df in per_band_groups:
                # Count unique multipliers per hour for this band and column
                mult_set_ts = group_df.groupby(pd.Grouper(key='Datetime', freq='h'))[mult_col].apply(lambda x: set(x.dropna())).reindex(master_index)
                mult_set_ts = mult_set_ts.apply(lambda x: x if isinstance(x, set) else set())
                
                # Build cumulative set of unique multipliers seen so far
                running_set = set()
                cumulative_sets_list = []
                for s in mult_set_ts:
                    running_set.update(s)
                    cumulative_sets_list.append(running_set.copy())

                band_mult_ts = pd.Series(cumulative_sets_list, index=master_index).apply(len)
                
                # Accumulate multiplier counts across all columns and bands
                mult_count_ts += band_mult_ts
                
                # Track per-band totals (accumulate across multiplier columns)
                if f"total_mults_{band}" not in per_band_mult_ts_dict:
                    per_band_mult_ts_dict[f"total_mults_{band}"] = pd.Series(0.0, index=master_index)
                per_band_mult_ts_dict[f"total_mults_{band}"] += band_mult_ts
        
        # --- QSO Points & Counts ---
        hourly_groups = df_sorted.set_index('Datetime').groupby(pd.Grouper(freq='h'))
        cum_points_ts = hourly_groups['QSOPoints'].sum().cumsum().reindex(master_index, method='ffill').fillna(0)
        run_points_ts = df_sorted[df_sorted['Run'] == 'Run'].set_index('Datetime')['QSOPoints'].resample('h').sum().cumsum().reindex(master_index, method='ffill').fillna(0)
        sp_unk_points_ts = cum_points_ts - run_points_ts
        
        cum_qso_ts = hourly_groups.size().cumsum().reindex(master_index, method='ffill').fillna(0)
        run_qso_ts = df_sorted[df_sorted['Run'] == 'Run'].set_index('Datetime')['Call'].resample('h').count().cumsum().reindex(master_index, method='ffill').fillna(0)
        sp_unk_qso_ts = cum_qso_ts - run_qso_ts

        # --- Final Score Calculation ---
        final_score_ts = cum_points_ts * mult_count_ts
        run_ratio = (run_points_ts / cum_points_ts).fillna(0)
        sp_unk_ratio = (sp_unk_points_ts / cum_points_ts).fillna(0)
        run_score_ts = final_score_ts * run_ratio
        sp_unk_score_ts = final_score_ts * sp_unk_ratio

        result_df = pd.DataFrame({
            'run_qso_count': run_qso_ts, 'sp_unk_qso_count': sp_unk_qso_ts,
            'run_score': run_score_ts, 'sp_unk_score': sp_unk_score_ts,
            'score': final_score_ts, 'total_mults': mult_count_ts,
        }, index=master_index)
        
        for col_name, series in per_band_mult_ts_dict.items():
            result_df[col_name] = series

        return result_df.astype(int)