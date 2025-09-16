# Contest Log Analyzer/contest_tools/contest_specific_annotations/iaru_hf_multiplier_resolver.py
#
# Author: Gemini AI
# Date: 2025-09-16
# Version: 0.88.2-Beta
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
# Purpose: Provides a custom, contest-specific multiplier resolver for the
#          IARU HF World Championship contest. It parses the received exchange
#          to identify and categorize the three distinct multiplier types:
#          ITU Zones, IARU HQ Stations, and IARU Officials.
#
# --- Revision History ---
## [0.88.2-Beta] - 2025-09-16
### Changed
# - Refactored module to be compliant with the new, data-driven resolver
#   architecture. The main function now accepts a ContestDefinition object
#   and uses it as a "blueprint" to populate the correct columns.
# - Reworked logic to be key-based instead of order-based for robustness.
## [0.70.25-Beta] - 2025-09-10
### Changed
# - Updated `resolve_multipliers` and `_load_officials_set` to accept
#   `root_input_dir` as a parameter, in compliance with Principle 15.
## [0.62.2-Beta] - 2025-09-08
### Changed
# - Updated script to read the new CONTEST_INPUT_DIR environment variable.
## [0.55.6-Beta] - 2025-08-30
### Changed
# - Added the standard copyright and MPL 2.0 license block to the header
#   to conform to project standards.
## [0.55.4-Beta] - 2025-08-29
### Fixed
# - Simplified logic to read the clean 'RcvdMult' column from the parser,
#   removing the incorrect string-splitting logic.
# - Updated the input column check from 'RcvdExchangeFull' to 'RcvdMult'.

import pandas as pd
import os
import re
import logging
from typing import Dict, Any, Set, Tuple, Optional

from ..contest_definitions import ContestDefinition

# Global cache for the officials set to avoid re-reading the file
_OFFICIALS_SET_CACHE: Set[str] = set()

def _load_officials_set(root_input_dir: str) -> Set[str]:
    """Loads the iaru_officials.dat file into a set for fast lookups."""
    global _OFFICIALS_SET_CACHE
    if _OFFICIALS_SET_CACHE:
        return _OFFICIALS_SET_CACHE

    try:
        root_dir = root_input_dir.strip().strip('"').strip("'")
        data_dir = os.path.join(root_dir, 'data')
        filepath = os.path.join(data_dir, 'iaru_officials.dat')
        with open(filepath, 'r', encoding='utf-8') as f:
            _OFFICIALS_SET_CACHE = {line.strip().upper() for line in f if line.strip()}
    except Exception as e:
        print(f"Warning: Could not load iaru_officials.dat file. Official multiplier check will be disabled. Error: {e}")
        _OFFICIALS_SET_CACHE = set()

    return _OFFICIALS_SET_CACHE

def _resolve_row(row: pd.Series, officials_set: Set[str]) -> Dict[str, Optional[str]]:
    """
    Parses the received exchange for a single QSO and returns the categorized
    multiplier value.
    """
    mult_zone, mult_hq, mult_official = None, None, None
    
    # Get the clean multiplier value from the 'RcvdMult' column provided by the parser.
    exchange = row.get('RcvdMult')
    
    if pd.notna(exchange):
        exchange = str(exchange).strip()
        
        # 1. Check if it's a numeric ITU Zone
        if exchange.isnumeric():
            mult_zone = exchange
        # 2. Check if it's an IARU Official
        elif exchange.upper() in officials_set:
            mult_official = exchange.upper()
        # 3. Assume it's an IARU HQ station if it's alphabetic
        elif exchange.isalpha():
            mult_hq = exchange.upper()

    return {'zone': mult_zone, 'hq': mult_hq, 'official': mult_official}

def resolve_multipliers(df: pd.DataFrame, my_location_type: str, root_input_dir: str, contest_def: ContestDefinition) -> pd.DataFrame:
    """
    Resolves multipliers for the IARU HF World Championship by parsing the
    RcvdMult column and populating the three distinct multiplier columns.
    """
    # This map provides a robust link between the rule name in the JSON
    # and the key returned by the _resolve_row helper function.
    RULE_TO_KEY_MAP = {
        'Zones': 'zone',
        'HQ Stations': 'hq',
        'IARU Officials': 'official'
    }

    if df.empty or 'RcvdMult' not in df.columns:
        # Ensure columns defined in the blueprint exist even if there's nothing to process
        for rule in contest_def.multiplier_rules:
            col = rule.get('value_column')
            if col and col not in df.columns:
                df[col] = pd.NA
        return df

    officials_set = _load_officials_set(root_input_dir)
    
    # Get the categorized multiplier data for all rows in a single pass.
    categorized_mults = df.apply(_resolve_row, axis=1, officials_set=officials_set)

    # Iterate through the rules from the JSON blueprint to assign data to the correct columns.
    for rule in contest_def.multiplier_rules:
        target_column = rule.get('value_column')
        data_key = RULE_TO_KEY_MAP.get(rule.get('name'))
        if target_column and data_key:
            df[target_column] = categorized_mults.apply(lambda x: x.get(data_key))
    
    return df