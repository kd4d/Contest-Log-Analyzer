# Contest Log Analyzer/contest_tools/score_calculators/wae_calculator.py
#
# Author: Gemini AI
# Date: 2025-09-13
# Version: 0.87.1-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Purpose: This module provides the complex, contest-specific time-series
#          score calculator for the Worked All Europe (WAE) Contest.
#
# --- Revision History ---
## [0.87.1-Beta] - 2025-09-13
### Fixed
# - Fixed a TypeError by localizing the timezone of the main QSO DataFrame
#   to UTC before performing time-based operations.
## [0.85.2-Beta] - 2025-09-13
# - Initial release.
#
import pandas as pd
import numpy as np
from typing import TYPE_CHECKING

from .calculator_interface import TimeSeriesCalculator

if TYPE_CHECKING:
    from ..contest_log import ContestLog

class WaeCalculator(TimeSeriesCalculator):
    """
    Calculates the time-series score for the WAE contest, handling QSOs,
    QTCs, and weighted multipliers, and providing a breakdown by operating style.
    """
    _BAND_WEIGHTS = {'80M': 4, '40M': 3, '20M': 2, '15M': 2, '10M': 2}
    
    def calculate(self, log: 'ContestLog') -> pd.DataFrame:
        """
        Calculates a cumulative, time-series score for a WAE log.
        Score = (Total QSOs + Total QTCs) * Total Weighted Multipliers
        """
        qsos_df = log.get_processed_data()
        qtcs_df = getattr(log, 'qtcs_df', pd.DataFrame()).copy()
        log_manager = getattr(log, '_log_manager_ref', None)
        master_index = getattr(log_manager, 'master_time_index', None)

        if master_index is None or qsos_df.empty:
            return pd.DataFrame()

        # Ensure the Datetime column is timezone-aware before processing
        if qsos_df['Datetime'].dt.tz is None:
            qsos_df['Datetime'] = qsos_df['Datetime'].dt.tz_localize('UTC')

        qsos_df_sorted = qsos_df.dropna(subset=['Datetime']).sort_values('Datetime')

        # --- 1. Calculate Cumulative Contact Counts (QSOs + QTCs) ---
        ts_qso_count = pd.Series(1, index=qsos_df_sorted['Datetime']).resample('h').count().cumsum()
        ts_qso_count = ts_qso_count.reindex(master_index, method='ffill').fillna(0)

        if not qtcs_df.empty:
            qtcs_df['Datetime'] = pd.to_datetime(
                qtcs_df['QTC_DATE'] + ' ' + qtcs_df['QTC_TIME'],
                format='%Y-%m-%d %H%M', errors='coerce'
            )
            if qtcs_df['Datetime'].dt.tz is None:
                 qtcs_df['Datetime'] = qtcs_df['Datetime'].dt.tz_localize('UTC')
            
            qtcs_df_sorted = qtcs_df.dropna(subset=['Datetime']).sort_values('Datetime')
            ts_qtc_count = pd.Series(1, index=qtcs_df_sorted['Datetime']).resample('h').count().cumsum()
            ts_qtc_count = ts_qtc_count.reindex(master_index, method='ffill').fillna(0)
        else:
            ts_qtc_count = pd.Series(0, index=master_index)
        
        ts_contact_total = ts_qso_count + ts_qtc_count

        # --- 2. Calculate Cumulative Weighted Multipliers ---
        mult_cols = ['Mult1', 'Mult2']
        df_mults = qsos_df_sorted[qsos_df_sorted[mult_cols].notna().any(axis=1)]
        
        new_mults_events = []
        for col in mult_cols:
            if col in df_mults.columns:
                first_worked = df_mults.drop_duplicates(subset=['Band', col], keep='first')
                weights = first_worked['Band'].map(self._BAND_WEIGHTS)
                new_mults_ts = pd.Series(weights.values, index=first_worked['Datetime'])
                new_mults_events.append(new_mults_ts)
        
        if new_mults_events:
            combined_mults_ts = pd.concat(new_mults_events)
            hourly_weighted_mults = combined_mults_ts.resample('h').sum()
            ts_weighted_mults = hourly_weighted_mults.cumsum().reindex(master_index, method='ffill').fillna(0)
        else:
            ts_weighted_mults = pd.Series(0, index=master_index)

        # --- 3. Calculate Total Score ---
        ts_total_score = ts_contact_total * ts_weighted_mults
        
        # --- 4. Apportion Score by Operating Style (Run vs. S&P) ---
        is_run = qsos_df_sorted['Run'] == 'Run'
        is_sp_unk = ~is_run
        
        run_qso_count = qsos_df_sorted[is_run].set_index('Datetime')['Call'].resample('h').count().cumsum()
        sp_unk_qso_count = qsos_df_sorted[is_sp_unk].set_index('Datetime')['Call'].resample('h').count().cumsum()

        run_qso_count = run_qso_count.reindex(master_index, method='ffill').fillna(0)
        sp_unk_qso_count = sp_unk_qso_count.reindex(master_index, method='ffill').fillna(0)
        total_qso_count = run_qso_count + sp_unk_qso_count

        # Calculate ratios, handling division by zero
        run_ratio = (run_qso_count / total_qso_count).fillna(0)
        sp_unk_ratio = (sp_unk_qso_count / total_qso_count).fillna(0)

        # Apportion the total score
        ts_run_score = ts_total_score * run_ratio
        ts_sp_unk_score = ts_total_score * sp_unk_ratio

        # --- 5. Assemble Final DataFrame ---
        result_df = pd.DataFrame({
            'run_qso_count': run_qso_count,
            'sp_unk_qso_count': sp_unk_qso_count,
            'run_score': ts_run_score,
            'sp_unk_score': ts_sp_unk_score,
            'score': ts_total_score,
        })

        return result_df.astype(int)