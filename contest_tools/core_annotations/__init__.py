# Contest Log Analyzer/contest_tools/core_annotations/__init__.py
#
# Purpose: This module provides a unified interface for generic annotation
#          utilities (like Run/S&P and Country Lookup) to make them compatible
#          with the DataFrame-centric workflow of the ContestLog class.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-09-30
# Version: 0.90.3-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
#
# License: Mozilla Public License, v. 2.0
#          https://www.mozilla.org/MPL/2.0/
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# --- Revision History ---
## [0.90.3-Beta] - 2025-09-30
### Changed
# - Refactored `process_dataframe_for_cty_data` to accept an explicit
#   `cty_dat_path`, removing the hardcoded path logic to fix a bug.
## [0.70.3-Beta] - 2025-09-09
### Changed
# - Refactored `process_dataframe_for_cty_data` to accept `root_input_dir`
#   as a parameter, in compliance with Principle 15.
## [0.62.1-Beta] - 2025-09-08
### Changed
# - Updated script to read the new CONTEST_INPUT_DIR environment variable.
## [0.43.0-Beta] - 2025-08-21
### Added
# - Exposed the new BandAllocator class through the package initializer.
## [0.30.40-Beta] - 2025-08-06
### Fixed
# - Updated all references to the old CONTEST_DATA_DIR environment variable
#   to use the correct CONTEST_LOGS_REPORTS variable.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
import pandas as pd
import os
import logging
from typing import Dict, Any, List

# Import the core annotation functions to make them available at the package level
from .get_cty import CtyLookup
from .run_s_p import process_contest_log_for_run_s_p
from ._band_allocator import BandAllocator

def process_dataframe_for_cty_data(df: pd.DataFrame, cty_dat_path: str) -> pd.DataFrame:
    """
    Applies universal DXCC and WAE lookup to a DataFrame of QSO records.
    """
    if df.empty:
        return df

    if 'Call' not in df.columns:
        raise KeyError("DataFrame must contain a 'Call' column for CTY data lookup.")

    logging.info(f"Using country file for universal annotations: {cty_dat_path}")

    processed_df = df.copy()
    processed_df['Call'] = processed_df['Call'].fillna('').astype(str).str.strip().str.upper()

    try:
        cty_lookup_instance = CtyLookup(cty_dat_path=cty_dat_path)
    except (FileNotFoundError, IOError) as e:
        logging.critical(f"Fatal Error initializing CtyLookup for universal annotations: {e}")
        raise

    temp_results = processed_df['Call'].apply(
        lambda call: cty_lookup_instance.get_cty_DXCC_WAE(call)._asdict()
    ).tolist()

    temp_df = pd.DataFrame(temp_results, index=processed_df.index)

    for col in temp_df.columns:
        processed_df[col] = temp_df[col]

    for col in ['CQZone', 'ITUZone']:
        if col in processed_df.columns:
            processed_df[col] = pd.to_numeric(processed_df[col], errors='coerce').astype('Int64')

    return processed_df