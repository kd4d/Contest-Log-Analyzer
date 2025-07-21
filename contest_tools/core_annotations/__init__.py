# Contest Log Analyzer/contest_tools/core_annotations/__init__.py
#
# Purpose: This module provides a unified interface for generic annotation
#          utilities (like Run/S&P and Country Lookup) to make them compatible
#          with the DataFrame-centric workflow of the ContestLog class.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-21
# Version: 0.10.0-Beta
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

## [0.10.0-Beta] - 2025-07-21
# - Updated version for consistency with new reporting structure.

### Changed
# - (None)

### Fixed
# - (None)

### Removed
# - (None)

import pandas as pd
import os
from typing import Dict, Any, List

# Import the core annotation functions to make them available at the package level
from .get_cty import CtyLookup
from .run_s_p import process_contest_log_for_run_s_p

def process_dataframe_for_cty_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies DXCC and WAE lookup to a DataFrame of QSO records.

    This function is a wrapper to integrate get_cty.py's functionality
    into a DataFrame-centric pipeline. It reads the CTY.DAT file path from
    the CTY_DAT_PATH environment variable.

    Args:
        df (pd.DataFrame): The input DataFrame, expected to have a 'Call' column.

    Returns:
        pd.DataFrame: The DataFrame with DXCC/WAE/Zone columns added/updated.

    Raises:
        KeyError: If the 'Call' column is missing from the input DataFrame.
        ValueError: If the CTY_DAT_PATH environment variable is not set.
        FileNotFoundError: If the file specified by CTY_DAT_PATH does not exist.
    """
    if df.empty:
        return df

    if 'Call' not in df.columns:
        raise KeyError("DataFrame must contain a 'Call' column for CTY data lookup.")

    # Get the environment variable and strip any surrounding quotes
    raw_path = os.environ.get('CTY_DAT_PATH')
    if not raw_path:
        raise ValueError("Environment variable CTY_DAT_PATH is not set. Cannot perform country lookup.")
    
    cty_dat_file_path = raw_path.strip().strip('"').strip("'")

    processed_df = df.copy()
    processed_df['Call'] = processed_df['Call'].fillna('').astype(str).str.strip().str.upper()

    try:
        cty_lookup_instance = CtyLookup(cty_dat_path=cty_dat_file_path, wae=True)
    except (FileNotFoundError, IOError) as e:
        print(f"Fatal Error initializing CtyLookup: {e}")
        raise

    # Apply the comprehensive lookup and convert the resulting namedtuples to dicts
    temp_results = processed_df['Call'].apply(
        lambda call: cty_lookup_instance.get_cty_DXCC_WAE(call)._asdict()
    ).tolist()

    # Convert the list of dictionaries to a temporary DataFrame
    temp_df = pd.DataFrame(temp_results, index=processed_df.index)

    # Define the columns we want to update/add from the lookup
    cty_columns = ['DXCCName', 'DXCCPfx', 'CQZone', 'ITUZone', 'Continent', 'WAEName', 'WAEPfx', 'Lat', 'Lon', 'Tzone']

    # Update the main DataFrame with the results
    for col in cty_columns:
        if col in temp_df:
            processed_df[col] = temp_df[col]

    # Ensure correct data types for numeric columns
    for col in ['CQZone', 'ITUZone']:
        if col in processed_df.columns:
            processed_df[col] = pd.to_numeric(processed_df[col], errors='coerce').astype('Int64')

    return processed_df
