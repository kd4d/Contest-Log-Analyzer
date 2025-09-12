# Contest Log Analyzer/contest_tools/score_calculators/wae_calculator.py
#
# Author: Gemini AI
# Date: 2025-09-12
# Version: 1.0.1-Beta
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
## [1.0.1-Beta] - 2025-09-12
### Changed
# - Renamed class to `WaeCalculator` to align with the new, simplified
#   naming convention.
## [1.0.0-Beta] - 2025-09-12
# - Initial release.

import pandas as pd
from typing import TYPE_CHECKING

from .calculator_interface import TimeSeriesCalculator

if TYPE_CHECKING:
    from ..contest_log import ContestLog

class WaeCalculator(TimeSeriesCalculator):
    """
    Calculates the time-series score for the WAE contest, handling QSOs,
    QTCs, and weighted multipliers.
    """
    _BAND_WEIGHTS = {'80M': 4, '40M': 3, '20M': 2, '15M': 2, '10M': 2}
    
    def calculate(self, log: 'ContestLog') -> pd.DataFrame:
        """
        Calculates a cumulative, time-series score for a WAE log.
        Score = (Total QSOs + Total QTCs) * Total Weighted Multipliers
        """
        qsos_df = log.get_processed_data()
        qtcs_df = getattr(log, 'qtcs_df', pd.DataFrame())
        master_index = getattr(log, '_log_manager_ref', None).master_time_index

        if master_index is None or qsos_df.empty:
            return pd.DataFrame()

        # --- 1. Calculate Cumulative QSO Points (1 point per QSO) ---
        qsos_df_sorted = qsos_df.dropna(subset=['Datetime']).sort_values('Datetime')
        ts_qso_points = pd.Series(1, index=qsos_df_sorted['Datetime']).resample('h').count().cumsum()
        ts_qso_points = ts_qso_points.reindex(master_index, method='ffill').fillna(0)

        # --- 2. Calculate Cumulative QTC Points (1 point per QTC) ---
        if not qtcs_df.empty:
            qtcs_df['Datetime'] = pd.to_datetime(
                qtcs_df['QTC_DATE'] + ' ' + qtcs_df['QTC_TIME'],
                format='%Y-%m-%d %H%M',
                errors='coerce'
            )
            # Ensure timezone-awareness to match master_index
            if qtcs_df['Datetime'].dt.tz is None:
                 qtcs_df['Datetime'] = qtcs_df['Datetime'].dt.tz_localize('UTC')
            
            qtcs_df_sorted = qtcs_df.dropna(subset=['Datetime']).sort_values('Datetime')
            ts_qtc_points = pd.Series(1, index=qtcs_df_sorted['Datetime']).resample('h').count().cumsum()
            ts_qtc_points = ts_qtc_points.reindex(master_index, method='ffill').fillna(0)
        else:
            ts_qtc_points = pd.Series(0, index=master_index)

        # --- 3. Calculate Cumulative Weighted Multipliers ---
        mult_cols = ['Mult1', 'Mult2']
        df_mults = qsos_df_sorted[qsos_df_sorted[mult_cols].notna().any(axis=1)]
        
        new_mults_events = []
        for col in mult_cols:
            if col in df_mults.columns:
                # Find the first time each (band, multiplier) combo was worked
                first_worked = df_mults.drop_duplicates(subset=['Band', col], keep='first')
                
                # Get the band weights for these new multiplier events
                weights = first_worked['Band'].map(self._BAND_WEIGHTS)
                
                # Create a series of weights indexed by datetime
                new_mults_ts = pd.Series(weights.values, index=first_worked['Datetime'])
                new_mults_events.append(new_mults_ts)
        
        if new_mults_events:
            combined_mults_ts = pd.concat(new_mults_events)
            hourly_weighted_mults = combined_mults_ts.resample('h').sum()
            ts_weighted_mults = hourly_weighted_mults.cumsum().reindex(master_index, method='ffill').fillna(0)
        else:
            ts_weighted_mults = pd.Series(0, index=master_index)

        # --- 4. Calculate Final Score ---
        total_qsos_and_qtcs = ts_qso_points + ts_qtc_points
        final_score = total_qsos_and_qtcs * ts_weighted_mults

        # --- 5. Assemble Final DataFrame ---
        result_df = pd.DataFrame({
            'qso_points': ts_qso_points,
            'qtc_points': ts_qtc_points,
            'contact_total': total_qsos_and_qtcs,
            'weighted_mults': ts_weighted_mults,
            'score': final_score
        })

        return result_df.astype(int)