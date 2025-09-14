# Contest Log Analyzer/contest_tools/score_calculators/standard_calculator.py
#
# Author: Gemini AI
# Date: 2025-09-14
# Version: 0.86.7-Beta
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
## [0.86.7-Beta] - 2025-09-14
### Fixed
# - Replaced the incompatible .expanding().apply() method with a manual
#   loop to correctly perform a cumulative union of sets, fixing a DataError.
## [0.86.6-Beta] - 2025-09-14
### Fixed
# - Corrected a ValueError by removing the non-scalar `fill_value` from
#   the reindex call and handling NaN values afterward.
## [0.86.5-Beta] - 2025-09-14
### Fixed
# - Re-introduced the timezone localization check that was accidentally
#   removed, fixing a regression that caused a TypeError.
## [0.86.4-Beta] - 2025-09-13
### Changed
# - Rewrote the calculate() method to use the new pre-filtered DataFrame
#   and to correctly calculate the final score using multipliers.
### Fixed
# - Corrected logic to no longer include duplicate QSOs in its counts.
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

        # Ensure the Datetime column is timezone-aware before processing
        if df_non_dupes['Datetime'].dt.tz is None:
            df_non_dupes['Datetime'] = df_non_dupes['Datetime'].dt.tz_localize('UTC')

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
        
        # Cumulative Multipliers
        mult1_set = df_sorted.groupby(pd.Grouper(key='Datetime', freq='h'))['Mult1'].apply(set)
        mult2_set = df_sorted.groupby(pd.Grouper(key='Datetime', freq='h'))['Mult2'].apply(set)

        all_mult_sets = (mult1_set | mult2_set).reindex(master_index)
        all_mult_sets = all_mult_sets.apply(lambda x: x if isinstance(x, set) else set())

        # Replace incompatible .expanding().apply() with a manual loop
        cumulative_sets_list = []
        running_set = set()
        for current_set in all_mult_sets:
            running_set.update(current_set)
            cumulative_sets_list.append(running_set.copy())
        
        cumulative_mult_sets = pd.Series(cumulative_sets_list, index=master_index)
        mult_count_ts = cumulative_mult_sets.apply(len)
        
        # Final Score Calculation
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
            'score': final_score_ts
        }, index=master_index)
        
        return result_df.astype(int)