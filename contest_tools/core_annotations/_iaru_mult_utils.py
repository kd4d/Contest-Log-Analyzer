# contest_tools/core_annotations/_iaru_mult_utils.py
#
# Purpose: Shared utilities for IARU HQ Stations and IARU Officials multipliers.
#          Used by both IARU-HF and WRTC contests.
#
# Copyright (c) 2025 Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import pandas as pd
from typing import Set, Optional, Dict

# Global cache for the officials set to avoid re-reading the file
_OFFICIALS_SET_CACHE: Set[str] = set()

def load_officials_set(root_input_dir: str) -> Set[str]:
    """
    Loads the iaru_officials.dat file into a set for fast lookups.
    
    The file contains IARU official multiplier abbreviations:
    - AC (Administrative Council)
    - R1, R2, R3 (Regional Representatives)
    
    Args:
        root_input_dir: Root directory containing the data/ subdirectory
        
    Returns:
        Set containing official abbreviations (e.g., {'AC', 'R1', 'R2', 'R3'})
    """
    global _OFFICIALS_SET_CACHE
    if _OFFICIALS_SET_CACHE:
        return _OFFICIALS_SET_CACHE

    try:
        root_dir = root_input_dir.strip().strip('"').strip("'")
        data_dir = os.path.join(root_dir, 'data')
        filepath = os.path.join(data_dir, 'iaru_officials.dat')
        with open(filepath, 'r', encoding='utf-8') as f:
            _OFFICIALS_SET_CACHE = {line.strip().upper() for line in f if line.strip() and not line.strip().startswith('#')}
    except Exception as e:
        print(f"Warning: Could not load iaru_officials.dat file. Official multiplier check will be disabled. Error: {e}")
        _OFFICIALS_SET_CACHE = set()

    return _OFFICIALS_SET_CACHE

def resolve_iaru_hq_official(exchange: str, officials_set: Set[str]) -> Dict[str, Optional[str]]:
    """
    Parses exchange to identify HQ Station or IARU Official.
    
    This function identifies IARU multipliers from the received exchange:
    - If exchange matches an IARU official (AC, R1, R2, R3) → Official multiplier
    - If exchange is alphabetic (not numeric, not official) → HQ Station multiplier
    - Otherwise → No multiplier
    
    Args:
        exchange: Received exchange value (from RcvdMult column)
        officials_set: Set of valid IARU official abbreviations (from load_officials_set)
    
    Returns:
        Dict with keys 'hq' and 'official':
        - 'hq': HQ station abbreviation (uppercase) or None
        - 'official': Official abbreviation (AC, R1, R2, R3) or None
    """
    if not exchange or pd.isna(exchange):
        return {'hq': None, 'official': None}
    
    exchange = str(exchange).strip()
    
    # Check if it's an IARU Official (AC, R1, R2, R3)
    if exchange.upper() in officials_set:
        return {'hq': None, 'official': exchange.upper()}
    
    # Assume it's an IARU HQ station if it's alphabetic
    # (not numeric, not an official)
    if exchange.isalpha():
        return {'hq': exchange.upper(), 'official': None}
    
    return {'hq': None, 'official': None}
