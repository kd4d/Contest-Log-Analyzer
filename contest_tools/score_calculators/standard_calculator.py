# Contest Log Analyzer/contest_tools/score_calculators/standard_calculator.py
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
# Purpose: This module provides the default time-series score calculator
#          for all standard contests that do not have complex, stateful
#          scoring rules like QTCs or weighted multipliers.
#
# --- Revision History ---
## [0.87.1-Beta] - 2025-09-13
### Fixed
# - Fixed a TypeError by localizing the timezone of the internal DataFrame
#   to UTC before reindexing against the timezone-aware master index.
## [0.85.1-Beta] - 2025-09-13
# - Initial release.
#
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
    def calculate(self, log: 'ContestLog') -> pd.DataFrame:
        """
        Calculates a cumulative, time-series score based on QSO points,
        with a breakdown for Run vs. S&P+Unknown operating styles.
        """
        df = log.get_processed_data()
        log_manager = getattr(log, '_log_manager_ref', None)
        master_index = getattr(log_manager, 'master_time_index', None)

        required_cols = ['QSOPoints', 'Datetime', 'Run', 'Call']
        if df.empty or not all(c in df.columns for c in required_cols) or master_index is None:
            return pd.DataFrame()

        # Ensure the Datetime column is timezone-aware before processing
        if df['Datetime'].dt.tz is None:
            df['Datetime'] = df['Datetime'].dt.tz_localize('UTC')

        df_sorted = df.dropna(subset=['Datetime', 'QSOPoints']).sort_values(by='Datetime')
        
        # Create masks for operating style
        is_run = df_sorted['Run'] == 'Run'
        is_sp_unk = ~is_run
        
        # --- Calculate Cumulative Counts and Scores for each category ---
        
        # QSO Counts
        run_qso_count = df_sorted[is_run].set_index('Datetime')['Call'].resample('h').count().cumsum()
        sp_unk_qso_count = df_sorted[is_sp_unk].set_index('Datetime')['Call'].resample('h').count().cumsum()
        
        # Scores
        run_score = df_sorted[is_run].set_index('Datetime')['QSOPoints'].resample('h').sum().cumsum()
        sp_unk_score = df_sorted[is_sp_unk].set_index('Datetime')['QSOPoints'].resample('h').sum().cumsum()

        # --- Assemble Final DataFrame and align to master index ---
        result_df_naive = pd.DataFrame({
            'run_qso_count': run_qso_count,
            'sp_unk_qso_count': sp_unk_qso_count,
            'run_score': run_score,
            'sp_unk_score': sp_unk_score,
        })
        
        # Ensure the index is timezone-aware before reindexing
        if result_df_naive.index.tz is None:
            result_df_naive.index = result_df_naive.index.tz_localize('UTC')

        result_df = result_df_naive.reindex(master_index, method='ffill').fillna(0)
        
        result_df['score'] = result_df['run_score'] + result_df['sp_unk_score']
        
        return result_df.astype(int)