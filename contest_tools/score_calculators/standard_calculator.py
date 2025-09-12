# Contest Log Analyzer/contest_tools/score_calculators/standard_calculator.py
#
# Author: Gemini AI
# Date: 2025-09-12
# Version: 1.0.3-Beta
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
## [1.0.3-Beta] - 2025-09-12
### Fixed
# - Renamed 'total_score' column to 'score' for consistency with reports.
## [1.0.2-Beta] - 2025-09-12
### Changed
# - Rewrote calculate method to return a detailed DataFrame with score
#   and QSO count breakdowns by operating style (Run vs. S&P).
## [1.0.1-Beta] - 2025-09-12
### Changed
# - Renamed class to `StandardCalculator` to align with the new,
#   simplified naming convention.
## [1.0.0-Beta] - 2025-09-12
# - Initial release.

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
        master_index = getattr(log, '_log_manager_ref', None).master_time_index

        required_cols = ['QSOPoints', 'Datetime', 'Run', 'Call']
        if df.empty or not all(c in df.columns for c in required_cols) or master_index is None:
            return pd.DataFrame()

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
        result_df = pd.DataFrame({
            'run_qso_count': run_qso_count,
            'sp_unk_qso_count': sp_unk_qso_count,
            'run_score': run_score,
            'sp_unk_score': sp_unk_score,
        }).reindex(master_index, method='ffill').fillna(0)
        
        result_df['score'] = result_df['run_score'] + result_df['sp_unk_score']
        
        return result_df.astype(int)