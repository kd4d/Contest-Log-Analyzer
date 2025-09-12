# Contest Log Analyzer/contest_tools/score_calculators/calculator_interface.py
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
# Purpose: This module defines the abstract base class (interface) that all
#          time-series score calculator modules must implement.
#
# --- Revision History ---
## [1.0.1-Beta] - 2025-09-12
### Changed
# - Updated the docstring for the `calculate` method to reflect the new,
#   richer DataFrame structure required to support detailed reports.
## [1.0.0-Beta] - 2025-09-12
# - Initial release.

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import pandas as pd

# Use a forward reference to avoid a circular import with ContestLog
if TYPE_CHECKING:
    from ..contest_log import ContestLog

class TimeSeriesCalculator(ABC):
    """
    Abstract base class (interface) for all time-series score calculators.
    """
    
    @abstractmethod
    def calculate(self, log: 'ContestLog') -> pd.DataFrame:
        """
        Calculates a cumulative, time-series score for the given log.

        Args:
            log (ContestLog): The ContestLog object containing all processed
                              QSO and QTC data.

        Returns:
            pd.DataFrame: A DataFrame with a DatetimeIndex and columns for
                          score and QSO count breakdowns by operating style.
                          Required columns: 'run_score', 'sp_unk_score',
                          'total_score', 'run_qso_count', 'sp_unk_qso_count'.
        """
        pass