# Contest Log Analyzer/contest_tools/core_annotations/__init__.py
#
# Purpose: This module provides a unified interface for generic annotation
#          utilities (like Run/S&P and Country Lookup) to make them compatible
#          with the DataFrame-centric workflow of the ContestLog class.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-04
# Version: 0.29.5-Beta
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
# All notable changes to this project will be documented in this file.
## [0.29.5-Beta] - 2025-08-04
### Changed
# - Replaced all `print` statements with calls to the new logging framework.
## [0.28.5-Beta] - 2025-08-02
### Changed
# - Refactored the column merging logic to be fully dynamic. It now iterates
#   through the columns of the CTY lookup results instead of using a
#   hardcoded list, preventing future scalability issues.
#
## [0.28.4-Beta] - 2025-08-02
### Fixed
# - Updated the hardcoded `cty_columns` list to include the new `portableid`
#   field, ensuring it is correctly merged into the main dataframe after lookup.
#
## [0.27.0-Beta] - 2025-08-02
### Fixed
# - Corrected the instantiation of the CtyLookup class to align with the
#   refactored get_cty.py module, removing the unexpected 'wae' keyword
#   argument that was causing a TypeError.
import pandas as pd
import os
import logging
from typing import Dict, Any, List

# Import the core annotation functions to make them available at the package level
from .get_cty import CtyLookup
from .run_s_p import process_contest_log_for_run_s_p

def process_dataframe_for_cty_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies universal DXCC and WAE lookup to a DataFrame of QSO records
    using the main cty.dat file specified by the CONTEST_DATA_DIR environment variable.

    Args:
        df (pd.DataFrame): The input DataFrame, expected to have a 'Call' column.

    Returns:
        pd.DataFrame: The DataFrame with universal DXCC/WAE/Zone columns added/updated.
    """
    if df.empty:
        return df

    if 'Call' not in df.columns:
        raise KeyError("DataFrame must contain a 'Call' column for CTY data lookup.")

    data_dir = os.environ.get('CONTEST_DATA_DIR')
    if not data_dir:
        raise ValueError("Environment variable CONTEST_DATA_DIR is not set.")
    
    cty_dat_file_path = os.path.join(data_dir.strip().strip('"').strip("'"), 'cty.dat')
    logging.info(f"Using country file for universal annotations: {cty_dat_file_path}")

    processed_df = df.copy()
    processed_df['Call'] = processed_df['Call'].fillna('').astype(str).str.strip().str.upper()

    try:
        cty_lookup_instance = CtyLookup(cty_dat_path=cty_dat_file_path)
    except (FileNotFoundError, IOError) as e:
        logging.critical(f"Fatal Error initializing CtyLookup for universal annotations: {e}")
        raise

    temp_results = processed_df['Call'].apply(
        lambda call: cty_lookup_instance.get_cty_DXCC_WAE(call)._asdict()
    ).tolist()

    temp_df = pd.DataFrame(temp_results, index=processed_df.index)

    # --- FIX: Dynamically merge all columns from the CTY lookup result ---
    # This prevents bugs if new fields are added to the CtyInfo tuple in the future.
    for col in temp_df.columns:
        processed_df[col] = temp_df[col]

    for col in ['CQZone', 'ITUZone']:
        if col in processed_df.columns:
            processed_df[col] = pd.to_numeric(processed_df[col], errors='coerce').astype('Int64')

    return processed_df