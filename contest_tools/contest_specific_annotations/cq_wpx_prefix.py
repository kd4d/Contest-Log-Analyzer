# Contest Log Analyzer/contest_tools/contest_specific_annotations/cq_wpx_prefix.py
#
# Purpose: Provides contest-specific logic for calculating WPX (Worked All Prefixes)
#          contest multipliers from callsigns. It uses pre-processed CTY data.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-05
# Version: 0.30.0-Beta
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
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
# - Standardized all project files to a common baseline version.
import pandas as pd
import re
from typing import List, Any

# Define suffixes to be stripped from callsigns before processing
SUFFIXES_TO_STRIP = ['/QRP', '/P', '/M', '/B']

def _clean_callsign(call: str) -> str:
    """
    Cleans a callsign by removing common suffixes and parts after a hyphen.
    """
    if not isinstance(call, str):
        return ""
    
    call_upper = call.upper()
    
    # Strip specific suffixes first
    for suffix in SUFFIXES_TO_STRIP:
        if call_upper.endswith(suffix):
            call_upper = call_upper[:-len(suffix)]
            break # Stop after the first match
            
    # Strip anything after a hyphen
    return call_upper.split('-')[0].strip()

def _get_prefix(row: pd.Series) -> str:
    """
    Derives the WPX prefix for a single QSO (row) based on a strict ruleset.
    """
    call = row.get('Call', '')
    dxcc_pfx = row.get('DXCCPfx', 'Unknown')
    portable_id = row.get('portableid', '')
    
    # Rule 1: Highest priority for Maritime Mobile
    if call.endswith('/MM'):
        return "Unknown"

    cleaned_call = _clean_callsign(call)

    # --- Portable Call Processing ---
    if portable_id:
        if dxcc_pfx == "Unknown":
            return "Unknown"
        
        # Rule: "call/digit" (e.g., WN5N/7)
        if len(portable_id) == 1 and portable_id.isdigit():
            # Find the root call by removing the portable part from the original call
            root_call_part = call.split('/')[0]
            # Find the prefix of the root call
            match = re.match(r'([A-Z]+[0-9]+)', root_call_part)
            if match:
                root_prefix = match.group(1)
                # Replace the digit in the root prefix with the portable digit
                return root_prefix[:-1] + portable_id

        # Rule: "letters-only" (e.g., LX/KD4D)
        if portable_id.isalpha():
            return portable_id + '0'
        
        # Default portable rule (e.g., VP2V/KD4D)
        return portable_id

    # --- Non-Portable Call Processing ---
    # Default prefix calculation: all chars up to and including the last digit
    match = re.match(r'(.*\d)', cleaned_call)
    if match:
        default_prefix = match.group(1)
    # Handle calls with no numbers (e.g., RAEM)
    else:
        default_prefix = cleaned_call[:2] + '0' if len(cleaned_call) >= 2 else "Unknown"

    # DXCCPfx Override Rule: Use the CTY.DAT prefix if it is more specific
    if cleaned_call.startswith(dxcc_pfx) and len(dxcc_pfx) > len(default_prefix):
        return dxcc_pfx
        
    # Final validation: a single digit is not a valid prefix
    if len(default_prefix) == 1 and default_prefix.isdigit():
        return "Unknown"

    return default_prefix

def calculate_wpx_prefixes(df: pd.DataFrame) -> pd.Series:
    """
    Calculates the WPX prefix for each QSO in a DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame of QSOs. Must contain 'Call', 'DXCCPfx',
                           and 'portableid' columns.
                           
    Returns:
        pd.Series: A Series containing the calculated WPX prefix for each QSO.
    """
    if df.empty:
        return pd.Series(dtype=str)
        
    return df.apply(_get_prefix, axis=1)