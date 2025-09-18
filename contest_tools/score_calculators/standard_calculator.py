# Contest Log Analyzer/contest_tools/score_calculators/standard_calculator.py
#
# Author: Gemini AI
# Date: 2025-09-18
# Version: 0.88.1-Beta
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
## [0.88.1-Beta] - 2025-09-18
### Fixed
# - Modified multiplier counting logic to explicitly filter out "Unknown"
#   multipliers, fixing a score discrepancy with text reports.
## [0.88.0-Beta] - 2025-09-18
### Fixed
# - Corrected multiplier counting logic to ensure unique column names are
#   processed, fixing a double-counting bug for asymmetric contests like
#   ARRL DX.
## [0.87.0-Beta] - 2025-09-18
### Fixed
# - Modified the `calculate` method to be "score-formula-aware". It now
#   correctly applies the scoring logic from the contest's JSON definition.
## [0.86.12-Beta] - 2025-09-14
### Fixed
# - Corrected a TypeError by replacing an invalid `.fillna(set())` call
#   with a valid `.apply()` method to handle hours with no multiplier
#   activity.
## [0.86.11-Beta] - 2025-09-14
### Fixed
# - Corrected a major regression in score calculation. The module now
#   inspects the multiplier totaling_method from the contest
#   definition and correctly applies either `sum_by_band` or
#   `once_per_log` logic.
## [0.86.10-Beta] - 2025-09-14
### Changed
# - Refactored multiplier logic to be data-driven. It now dynamically
#   reads multiplier columns from the contest definition instead of
#   using a hardcoded list, fixing a systemic bug.
## [0.86.9-Beta] - 2025-09-14
### Fixed
# - Removed the redundant timezone localization check, which caused a
#   TypeError when receiving an already-aware DataFrame.
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

        # Create a filtered DataFrame for multiplier counting, excluding "Unknown"
        df_for_mults = df_sorted.copy()
        for col in multiplier_columns:
            if col in df_for_mults.columns:
                df_for_mults = df_for_mults[df_for_mults[col] != 'Unknown']

        totaling_method = log.contest_definition.multiplier_rules[0].get('totaling_method', 'sum_by_band') if log.contest_definition.multiplier_rules else 'sum_by_band'

        if totaling_method == 'sum_by_band':
            mult_count_ts = pd.Series(0.0, index=master_index)
            for mult_col in multiplier_columns:
                if mult_col in df_for_mults.columns:
                    per_band_groups = df_for_mults.groupby('Band')
                    for band, group_df in per_band_groups:
                        mult_set_ts = group_df.groupby(pd.Grouper(key='Datetime', freq='h'))[mult_col].apply(set).reindex(master_index)
                        mult_set_ts = mult_set_ts.apply(lambda x: x if isinstance(x, set) else set())
                        
                        running_set = set()
                        cumulative_sets_list = []
                        for current_set in mult_set_ts:
                            running_set.update(current_set)
                            cumulative_sets_list.append(running_set.copy())
                        
                        mult_count_ts += pd.Series(cumulative_sets_list, index=master_index).apply(len)
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
            'score': final_score_ts
        }, index=master_index)
        
        return result_df.astype(int)