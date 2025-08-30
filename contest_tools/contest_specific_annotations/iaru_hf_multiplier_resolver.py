# Contest Log Analyzer/contest_tools/contest_specific_annotations/iaru_hf_multiplier_resolver.py
#
# Author: Gemini AI
# Date: 2025-08-29
# Version: 0.55.4-Beta
#
# Purpose: Provides a custom, contest-specific multiplier resolver for the
#          IARU HF World Championship contest. It parses the received exchange
#          to identify and categorize the three distinct multiplier types:
#          ITU Zones, IARU HQ Stations, and IARU Officials.
#
# --- Revision History ---
## [0.55.4-Beta] - 2025-08-29
### Fixed
# - Simplified logic to read the clean 'RcvdMult' column from the parser,
#   removing the incorrect string-splitting logic.
# - Updated the input column check from 'RcvdExchangeFull' to 'RcvdMult'.
## [0.55.2-Beta] - 2025-08-29
### Added
# - Added temporary, verbose logging to the _resolve_row function to
#   diagnose a persistent multiplier resolution failure.
## [0.55.1-Beta] - 2025-08-29
### Fixed
# - Corrected resolver logic to parse the full received exchange string
#   (e.g., "599 06") by isolating the last element as the multiplier,
#   fixing the bug where no multipliers were being assigned.

import pandas as pd
import os
import re
from typing import Dict, Any, Set, Tuple

# Global cache for the officials set to avoid re-reading the file
_OFFICIALS_SET_CACHE: Set[str] = set()

def _load_officials_set() -> Set[str]:
    """Loads the iaru_officials.dat file into a set for fast lookups."""
    global _OFFICIALS_SET_CACHE
    if _OFFICIALS_SET_CACHE:
        return _OFFICIALS_SET_CACHE

    try:
        root_dir = os.environ.get('CONTEST_LOGS_REPORTS').strip().strip('"').strip("'")
        data_dir = os.path.join(root_dir, 'data')
        filepath = os.path.join(data_dir, 'iaru_officials.dat')
        with open(filepath, 'r', encoding='utf-8') as f:
            _OFFICIALS_SET_CACHE = {line.strip().upper() for line in f if line.strip()}
    except Exception as e:
        print(f"Warning: Could not load iaru_officials.dat file. Official multiplier check will be disabled. Error: {e}")
        _OFFICIALS_SET_CACHE = set()

    return _OFFICIALS_SET_CACHE

def _resolve_row(row: pd.Series, officials_set: Set[str]) -> pd.Series:
    """
    Parses the received exchange for a single QSO and returns the categorized
    multiplier value.
    """
    mult_zone, mult_hq, mult_official = pd.NA, pd.NA, pd.NA
    
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

    return pd.Series([mult_zone, mult_hq, mult_official])

def resolve_multipliers(df: pd.DataFrame, my_location_type: str) -> pd.DataFrame:
    """
    Resolves multipliers for the IARU HF World Championship by parsing the
    RcvdMult column and populating the three distinct multiplier columns.
    """
    if df.empty or 'RcvdMult' not in df.columns:
        # Ensure columns exist even if there's nothing to process
        df['Mult_Zone'] = pd.NA
        df['Mult_HQ'] = pd.NA
        df['Mult_Official'] = pd.NA
        return df

    officials_set = _load_officials_set()
    
    df[['Mult_Zone', 'Mult_HQ', 'Mult_Official']] = df.apply(
        _resolve_row,
        axis=1,
        officials_set=officials_set
    )
    
    return df