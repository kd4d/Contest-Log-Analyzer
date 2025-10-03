# contest_tools/score_calculators/naqp_calculator.py
#
# Purpose: This module provides the complex, contest-specific time-series
#          score calculator for the North American QSO Party (NAQP) Contest.
#
#
# Author: Gemini AI
# Date: 2025-10-01
# Version: 0.90.6-Beta
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
# [0.90.6-Beta] - 2025-10-01
# - Initial release of the dedicated calculator for NAQP.
# - Implements the correct scoring logic where the QSO count includes all
#   valid QSOs (including DX), while the multiplier count is derived only
#   from multiplier-eligible QSOs (NA + KH6).

import pandas as pd
from typing import TYPE_CHECKING

from .calculator_interface import TimeSeriesCalculator

if TYPE_CHECKING:
    from ..contest_log import ContestLog

class NaqpCalculator(TimeSeriesCalculator):
    """
    Calculates the time-series score for the NAQP contest, handling the
    unique rule where the set of QSOs for scoring is different from the
    set of QSOs that provide multipliers.
    """
    def calculate(self, log: 'ContestLog', df_non_dupes: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates a cumulative, time-series score for a NAQP log.
        Score = (Total QSOs) * (Total Multipliers)
        """
        log_manager = getattr(log, '_log_manager_ref', None)
        master_index = getattr(log_manager, 'master_time_index', None)

        required_cols = ['QSOPoints', 'Datetime', 'Run', 'Call', 'Continent', 'DXCCPfx']
        if df_non_dupes.empty or not all(c in df_non_dupes.columns for c in required_cols) or master_index is None:
            return pd.DataFrame()

        df_sorted = df_non_dupes.dropna(subset=['Datetime']).sort_values(by='Datetime')
        
        # --- 1. Calculate Cumulative QSO Counts from ALL valid QSOs ---
        hourly_groups_all = df_sorted.set_index('Datetime').groupby(pd.Grouper(freq='h'))
        cum_qso_ts = hourly_groups_all.size().cumsum().reindex(master_index, method='ffill').fillna(0)
        run_qso_ts = df_sorted[df_sorted['Run'] == 'Run'].set_index('Datetime')['Call'].resample('h').count().cumsum().reindex(master_index, method='ffill').fillna(0)
        sp_unk_qso_ts = cum_qso_ts - run_qso_ts
        
        # --- 2. Filter for Multiplier-Eligible QSOs ---
        # Per rules, multipliers are NA stations plus Hawaii (KH6).
        df_for_mults = df_sorted[(df_sorted['Continent'] == 'NA') | (df_sorted['DXCCPfx'] == 'KH6')].copy()
        
        # --- 3. Calculate Cumulative Multipliers from the filtered DataFrame ---
        multiplier_columns = sorted(list(set([rule['value_column'] for rule in log.contest_definition.multiplier_rules])))
        for col in multiplier_columns:
            if col in df_for_mults.columns:
                df_for_mults = df_for_mults[df_for_mults[col] != 'Unknown']
        df_for_mults.dropna(subset=multiplier_columns, how='all', inplace=True)
        
        mult_count_ts = pd.Series(0.0, index=master_index)
        per_band_mult_ts_dict = {}

        # For NAQP, the method is sum_by_band
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

        # --- 4. Calculate Final Score & Apportion by Run/S&P status ---
        final_score_ts = cum_qso_ts * mult_count_ts
        
        # Apportion score based on the ratio of Run vs S&P+Unk QSOs from the full QSO set
        run_ratio = (run_qso_ts / cum_qso_ts).fillna(0)
        sp_unk_ratio = (sp_unk_qso_ts / cum_qso_ts).fillna(0)
        
        run_score_ts = final_score_ts * run_ratio
        sp_unk_score_ts = final_score_ts * sp_unk_ratio

        # --- 5. Assemble Final DataFrame ---
        result_df = pd.DataFrame({
            'run_qso_count': run_qso_ts,
            'sp_unk_qso_count': sp_unk_qso_ts,
            'run_score': run_score_ts,
            'sp_unk_score': sp_unk_score_ts,
            'score': final_score_ts,
            'total_mults': mult_count_ts,
        }, index=master_index)
        
        for col_name, series in per_band_mult_ts_dict.items():
            result_df[col_name] = series

        return result_df.astype(int)