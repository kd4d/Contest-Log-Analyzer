# Contest Log Analyzer/contest_tools/contest_specific_annotations/cq_wpx_prefix.py
#
# Purpose: Provides contest-specific logic to resolve WPX prefix multipliers.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-11
# Version: 0.31.59-Beta
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
## [0.31.59-Beta] - 2025-08-11
### Added
# - Added detailed INFO-level logging to the _get_prefix helper function
#   to provide a clear trace of the prefix calculation logic for debugging.
## [0.31.58-Beta] - 2025-08-11
### Fixed
# - Replaced the logic in the _get_prefix helper function with the
#   correct, multi-stage algorithm from the user-provided working file
#   to fix all known prefix calculation errors.
## [0.31.57-Beta] - 2025-08-11
### Changed
# - Providing the definitive, correct version of the file to resolve
#   environmental state mismatch issues.
## [0.31.54-Beta] - 2025-08-11
### Changed
# - Simplified multiplier logic to count prefixes once per contest instead
#   of once per band, per user instruction.
## [0.31.53-Beta] - 2025-08-11
### Fixed
# - Corrected the _get_prefix helper function to handle all known callsign
#   formats, including prefix-style portables, as per the working example.
## [0.31.52-Beta] - 2025-08-10
### Fixed
# - Rewrote _get_prefix function to precisely follow the 3-step logic in
#   WPXPrefixLookupAlgorithm.md.
## [0.31.51-Beta] - 2025-08-10
### Changed
# - Rewrote prefix calculation to identify the first time each prefix is
#   worked on each band, per user specification.
## [0.31.50-Beta] - 2025-08-10
### Fixed
# - Corrected the _get_prefix helper function to precisely implement the
#   algorithm from WPXPrefixLookupAlgorithm.md, including the special
#   Letter-Digit-Letter (LDL) case.
## [0.31.49-Beta] - 2025-08-10
### Changed
# - Rewrote prefix calculation logic to be stateful, identifying only the
#   first time each prefix is worked in the log.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
# - Standardized all project files to a common baseline version.
import pandas as pd
import re
import logging
from typing import Optional

def _clean_callsign(call: str) -> str:
    """
    Strips common non-prefix suffixes and cleans the callsign for analysis.
    This logic is intentionally kept separate from get_cty.py.
    """
    if not isinstance(call, str) or not call:
        return ""
    
    call = call.upper().strip()
    call = call.partition('-')[0]
    
    suffixes_to_strip = ['/P', '/M', '/A', '/E', '/J', '/B', '/QRP']
    for suffix in suffixes_to_strip:
        if call.endswith(suffix):
            call = call[:-len(suffix)]
            break
    return call

def _get_prefix_for_non_portable(call: str, dxc_pfx: str) -> str:
    """
    Determines the WPX prefix for a standard, non-portable callsign using
    the refined two-step logic.
    """
    # First, determine the default prefix ("everything up to last digit").
    default_prefix = "Unknown"
    match = re.search(r'\d(?!.*\d)', call)
    if match:
        last_digit_index = match.start()
        default_prefix = call[:last_digit_index + 1]
    else:
        # No number fallback rule.
        if len(call) >= 2:
            default_prefix = call[:2] + '0'

    # Next, apply the override rule. It only triggers if the DXCCPfx is a
    # more specific (longer) prefix than the default.
    if (dxc_pfx and dxc_pfx != "Unknown" and
        call.startswith(dxc_pfx) and
        len(dxc_pfx) > len(default_prefix)):
        return dxc_pfx
    
    return default_prefix

def _get_prefix(row: pd.Series) -> str:
    """
    Main logic to determine a WPX prefix from a full DataFrame row.
    """
    raw_call = row.get('Call')
    dxc_pfx = row.get('DXCCPfx')
    portable_id = row.get('portableid')
    prefix_result = "Unknown" # Default value

    logging.info(f"--- PREFIX CALC ---")
    logging.info(f"  - Inputs: Call='{raw_call}', DXCCPfx='{dxc_pfx}', PortableID='{portable_id}'")

    if not raw_call:
        logging.info(f"  - Result: 'Unknown' (No raw callsign)")
        return "Unknown"

    # WPX Rule: Maritime mobile does not count as a prefix. This is the highest priority.
    if raw_call.upper().strip().endswith('/MM'):
        logging.info(f"  - Result: 'Unknown' (Maritime Mobile)")
        return "Unknown"

    cleaned_call = _clean_callsign(raw_call)

    # --- Portable Call Logic ---
    if portable_id:
        if dxc_pfx == "Unknown":
            prefix_result = "Unknown"
        # Rule: call/digit (e.g., WN5N/7 -> WN7)
        elif len(portable_id) == 1 and portable_id.isdigit():
            parts = cleaned_call.split('/')
            # The root call is the part that is NOT the single-digit portableid.
            root_call = parts[0] if len(parts) > 1 and parts[1] == portable_id else parts[-1]
            
            root_prefix = _get_prefix_for_non_portable(root_call, dxc_pfx)
            
            match = re.search(r'\d(?!.*\d)', root_prefix)
            if match:
                last_digit_index = match.start()
                prefix_result = root_prefix[:last_digit_index] + portable_id
            else:
                prefix_result = root_prefix + portable_id
        # Rule: call/letters (e.g., LX/KD4D -> LX0)
        elif portable_id.isalpha():
            prefix_result = portable_id + '0'
        # Rule: call/prefix (e.g., VP2V/KD4D -> VP2V)
        else:
            prefix_result = portable_id
    # --- Non-Portable Call Logic ---
    else:
        prefix_result = _get_prefix_for_non_portable(cleaned_call, dxc_pfx)

    # Final validation: a single digit is not a valid prefix.
    if len(prefix_result) == 1 and prefix_result.isdigit():
        logging.info(f"  - Result: 'Unknown' (Final validation failed - single digit)")
        return "Unknown"
    
    logging.info(f"  - Result: '{prefix_result}' (Final)")
    return prefix_result

def calculate_wpx_prefixes(df: pd.DataFrame) -> pd.Series:
    """
    Calculates the WPX prefix for each QSO, returning a sparse Series that
    contains the prefix only for the first time it was worked in the contest.
    """
    required_cols = ['Call', 'DXCCPfx', 'portableid', 'Datetime']
    for col in required_cols:
        if col not in df.columns:
            # Return an empty series if required columns are not present.
            return pd.Series(None, index=df.index, dtype=object)

    # Create a temporary DataFrame to calculate prefixes for all QSOs first
    df_temp = df[required_cols].copy()
    df_temp['Prefix'] = df_temp.apply(_get_prefix, axis=1)
    
    # Sort by time to process QSOs chronologically
    df_temp.sort_values(by='Datetime', inplace=True)
    
    seen_prefixes = set()
    results_dict = {}

    for index, row in df_temp.iterrows():
        prefix = row.get('Prefix')
        
        if pd.notna(prefix) and prefix != "Unknown":
            if prefix not in seen_prefixes:
                seen_prefixes.add(prefix)
                results_dict[index] = prefix # Store prefix for this "first ever" QSO
            else:
                results_dict[index] = None # Subsequent QSOs for this prefix get None
        else:
            results_dict[index] = None

    # Reconstruct the Series in the original DataFrame's order
    final_series = pd.Series(results_dict, index=df.index)
    
    return final_series