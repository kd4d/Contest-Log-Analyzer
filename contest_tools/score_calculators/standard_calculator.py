# Contest Log Analyzer/contest_tools/score_calculators/standard_calculator.py
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
# Purpose: This module provides the default time-series score calculator
#          for all standard contests that do not have complex, stateful
#          scoring rules like QTCs or weighted multipliers.
#
# --- Revision History ---
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
    cumulative sum of QSO points over time.
    """
    def calculate(self, log: 'ContestLog') -> pd.DataFrame:
        """
        Calculates a cumulative, time-series score based on QSO points.
        """
        df = log.get_processed_data()
        
        if df.empty or 'QSOPoints' not in df.columns or 'Datetime' not in df.columns:
            return pd.DataFrame(columns=['score'])

        # Ensure we're working with a clean, sorted DataFrame
        df_sorted = df.dropna(subset=['Datetime', 'QSOPoints']).sort_values(by='Datetime')
        
        if df_sorted.empty:
            return pd.DataFrame(columns=['score'])
            
        # Set datetime as the index for time-series operations
        ts_df = df_sorted.set_index('Datetime')
        
        # Calculate the cumulative sum of points
        cumulative_score = ts_df['QSOPoints'].cumsum()
        
        # Return a DataFrame with the final score column
        time_series_score_df = pd.DataFrame({'score': cumulative_score})
        
        return time_series_score_df