# Contest Log Analyzer/contest_tools/core_annotations/__init__.py
#
# Purpose: This module provides a unified interface for generic annotation
#          utilities (like Run/S&P and Country Lookup) to make them compatible
#          with the DataFrame-centric workflow of the ContestLog class.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-22
# Version: 0.13.0-Beta
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

## [0.13.0-Beta] - 2025-07-22
### Changed
# - 'process_dataframe_for_cty_data' now accepts a ContestDefinition object.
# - The function now uses the contest-specific country file (e.g., 'cqww.cty')
#   if one is defined, otherwise it falls back to the default 'cty.dat'.

import pandas as pd
import os
from typing import Dict, Any, List

# Import the core annotation functions to make them available at the package level
from .get_cty import CtyLookup
from .run_s_p import process_contest_log_for_run_s_p
from ..contest_definitions import ContestDefinition

def process_dataframe_for_cty_data(df: pd.DataFrame, contest_definition: ContestDefinition) -> pd.DataFrame:
    """
    Applies DXCC and WAE lookup to a DataFrame of QSO records using the
    appropriate country file (either default or contest-specific).

    Args:
        df (pd.DataFrame): The input DataFrame, expected to have a 'Call' column.
        contest_definition (ContestDefinition): The definition for the current contest.

    Returns:
        pd.DataFrame: The DataFrame with DXCC/WAE/Zone columns added/updated.
    """
    if df.empty:
        return df

    if 'Call' not in df.columns:
        raise KeyError("DataFrame must contain a 'Call' column for CTY data lookup.")

    # --- Determine which country file to use ---
    country_file_to_use = contest_definition.country_file_name
    
    base_cty_path = os.environ.get('CTY_DAT_PATH')
    if not base_cty_path:
        raise ValueError("Environment variable CTY_DAT_PATH is not set.")
    
    cleaned_base_path = base_cty_path.strip().strip('"').strip("'")
    
    if country_file_to_use:
        # If a specific file is defined, look for it in the same directory as the default cty.dat
        base_dir = os.path.dirname(cleaned_base_path)
        cty_dat_file_path = os.path.join(base_dir, country_file_to_use)
        print(f"Using contest-specific country file: {cty_dat_file_path}")
    else:
        # Otherwise, use the default file from the environment variable
        cty_dat_file_path = cleaned_base_path
        print(f"Using default country file: {cty_dat_file_path}")


    processed_df = df.copy()
    processed_df['Call'] = processed_df['Call'].fillna('').astype(str).str.strip().str.upper()

    try:
        cty_lookup_instance = CtyLookup(cty_dat_path=cty_dat_file_path, wae=True)
    except (FileNotFoundError, IOError) as e:
        print(f"Fatal Error initializing CtyLookup: {e}")
        raise

    temp_results = processed_df['Call'].apply(
        lambda call: cty_lookup_instance.get_cty_DXCC_WAE(call)._asdict()
    ).tolist()

    temp_df = pd.DataFrame(temp_results, index=processed_df.index)

    cty_columns = ['DXCCName', 'DXCCPfx', 'CQZone', 'ITUZone', 'Continent', 'WAEName', 'WAEPfx', 'Lat', 'Lon', 'Tzone']

    for col in cty_columns:
        if col in temp_df:
            processed_df[col] = temp_df[col]

    for col in ['CQZone', 'ITUZone']:
        if col in processed_df.columns:
            processed_df[col] = pd.to_numeric(processed_df[col], errors='coerce').astype('Int64')

    return processed_df
