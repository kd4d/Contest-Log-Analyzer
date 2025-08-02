# Contest Log Analyzer/contest_tools/reports/report_interface.py
#
# Purpose: Defines the abstract base class for all report generators.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-02
# Version: 0.26.1-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# --- Revision History ---
# All notable changes to this project will be documented in this file.
# The format is based on "Keep a Changelog" (https://keepachangelog.com/en/1.0.0/),
# and this project aims to adhere to Semantic Versioning (https://semver.org/).

## [0.26.1-Beta] - 2025-08-02
### Fixed
# - Converted report_id, report_name, and report_type from @property methods
#   to simple class attributes. This fixes a bug where accessing these
#   attributes at the class level would return a property object instead of the
#   string value.

## [0.22.1-Beta] - 2025-07-31
### Changed
# - Replaced the boolean support properties with class attributes for a more
#   robust, class-level implementation.

## [0.22.0-Beta] - 2025-07-31
### Changed
# - Replaced the 'comparison_mode' property with three distinct boolean
#   properties ('supports_single', 'supports_pairwise', 'supports_multi')
#   to create a more explicit and extensible report generation system.

## [0.21.0-Beta] - 2025-07-28
### Removed
# - Removed the 'mult_type' argument from the generate() method's docstring
#   as it is no longer used.

## [0.15.0-Beta] - 2025-07-25
# - Standardized version for final review. No functional changes.

## [0.12.0-Beta] - 2025-07-22
### Changed
# - Refactored the generate() method to use **kwargs for flexible argument
#   passing, improving scalability for future reports with custom arguments.
# - Added 'mult_type' optional string argument to the generate() method
#   to allow reports to select between 'dxcc' and 'wae' multipliers.

## [0.11.0-Beta] - 2025-07-21
### Changed
# - Added 'include_dupes' optional boolean argument to the generate() method
#   signature to allow reports to optionally include duplicate QSOs.

## [0.10.0-Beta] - 2025-07-21
# - Initial release of the report interface.

from abc import ABC, abstractmethod
from typing import List
from ..contest_log import ContestLog

class ContestReport(ABC):
    """
    Abstract base class for all report generators.
    Ensures that every report has a consistent structure.
    """
    # --- Class attributes defining report metadata and behavior ---
    report_id: str = "abstract_report"
    report_name: str = "Abstract Report"
    report_type: str = "text"
    
    supports_single: bool = False
    supports_pairwise: bool = False
    supports_multi: bool = False

    def __init__(self, logs: List[ContestLog]):
        if not logs:
            raise ValueError("Cannot initialize a report with an empty list of logs.")
        self.logs = logs

    @abstractmethod
    def generate(self, output_path: str, **kwargs) -> str:
        """
        Generates the report content.

        Args:
            output_path (str): The directory where any output files should be saved.
            **kwargs: A dictionary for optional report-specific arguments.
                - include_dupes (bool): If True, include dupes. Defaults to False.
                - mult_name (str): The name of the multiplier to analyze.
                - metric (str): 'qsos' or 'points'.

        Returns:
            str: A summary message confirming the report generation.
        """
        pass