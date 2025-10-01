# Contest Log Analyzer/contest_tools/contest_specific_annotations/arrl_dx_scoring.py
#
# Purpose: Provides contest-specific scoring logic for the ARRL DX contest.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-09-30
# Version: 0.90.1-Beta
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
## [0.90.1-Beta] - 2025-09-30
### Changed
# - Refactored scoring logic to be compliant with official rules, basing
#   points on the worked station's DXCC entity instead of the exchange.
# - Reverted function signature to the standard two-argument version.
## [0.90.16-Beta] - 2025-09-30
### Changed
# - Refactored `calculate_points` to accept `root_input_dir` as a
#   parameter, removing the direct environment variable call.
## [0.62.4-Beta] - 2025-09-08
### Changed
# - Updated script to read the new CONTEST_INPUT_DIR environment variable.
## [0.33.4-Beta] - 2025-08-22
### Fixed
# - Corrected a SyntaxError in a logging f-string by refactoring the
#   message into a temporary variable.
## [0.33.3-Beta] - 2025-08-22
### Added
# - Added a diagnostic warning to flag when the K-prefix scoring
#   override is triggered.
## [0.33.2-Beta] - 2025-08-21
### Added
# - Added a temporary diagnostic log to print the source row for any
#   40M SD, NF, or YT multipliers at the point of resolution.
## [0.33.0-Beta] - 2025-08-21
### Changed
# - Refactored to use the new shared StateAndProvinceLookup utility.
# - Implemented the final, precise two-path algorithm for the "exchange
#   override", correctly handling US/VE, US-affiliated DX, and foreign
#   stations to ensure points are awarded consistently with multipliers.
## [0.32.0-Beta] - 2025-08-21
### Changed
# - The "exchange override" logic is now only applied if the worked
#   station's DXCC Identifier (e.g., "K", "KP4") begins with "K".
## [0.31.0-Beta] - 2025-08-21
### Changed
# - Reworked scoring logic to be "exchange-first", prioritizing the
#   received State/Province over the callsign's DXCC entity to align
#   with the multiplier resolver's logic.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
# - Standardized all project files to a common baseline version.
import pandas as pd
import logging
from typing import Dict, Any

def _calculate_single_qso_points(row: pd.Series, my_location_type: str) -> int:
    """
    Calculates the point value for a single QSO based on the official ARRL DX rules.
    """
    if row['Dupe']:
        return 0

    worked_dxcc_pfx = row.get('DXCCPfx')
    worked_dxcc_name = row.get('DXCCName')
    
    # Determine worked station's location type based on DXCC entity
    if worked_dxcc_pfx in ['KH6', 'KL7', 'CY9', 'CY0']:
        worked_location_type = "DX"
    elif worked_dxcc_name in ["United States", "Canada"]:
        worked_location_type = "W/VE"
    else:
        worked_location_type = "DX"

    # --- Final Scoring Rules ---
    if my_location_type == "W/VE":
        return 3 if worked_location_type == "DX" else 0
    elif my_location_type == "DX":
        return 3 if worked_location_type == "W/VE" else 0
    
    return 0

def calculate_points(df: pd.DataFrame, my_call_info: Dict[str, Any]) -> pd.Series:
    """
    Calculates QSO points for an entire DataFrame based on ARRL DX rules.
    """
    my_entity_name = my_call_info.get('DXCCName')
    if not my_entity_name:
        raise ValueError("Logger's own DXCC Name must be provided for scoring.")

    my_location_type = "W/VE" if my_entity_name in ["United States", "Canada"] else "DX"

    return df.apply(
        _calculate_single_qso_points, 
        axis=1,
        my_location_type=my_location_type
    )