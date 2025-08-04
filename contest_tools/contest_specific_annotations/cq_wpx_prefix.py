# Contest Log Analyzer/contest_tools/contest_specific_annotations/cq_wpx_prefix.py
#
# Purpose: Provides a contest-specific function to determine the WPX prefix
#          for a given callsign according to the CQ WPX contest rules.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-04
# Version: 0.29.5-Beta
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
## [0.29.5-Beta] - 2025-08-04
### Changed
# - Replaced all `print` statements with calls to the new logging framework.
## [0.28.13-Beta] - 2025-08-03
### Added
# - Added a final validation check to set any calculated prefix that is a
#   single digit to "Unknown".
### Fixed
# - Corrected the logic for the `call/digit` portable case to simply and
#   reliably identify the root callsign, fixing the bug with IZ5TJD/7.
#
## [0.28.6-Beta] - 2025-08-02
### Fixed
# - Refined the non-portable override rule to only apply when the DXCCPfx
#   is *longer* than the default "up-to-the-last-digit" prefix. This
#   correctly resolves ambiguity between special and standard prefixes.
#
import pandas as pd
import re
import logging

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

def _get_wpx_prefix_from_row(row: pd.Series) -> str:
    """
    Main logic to determine a WPX prefix from a full DataFrame row.
    """
    raw_call = row.get('Call')
    dxc_pfx = row.get('DXCCPfx')
    portable_id = row.get('portableid')
    prefix_result = "Unknown" # Default value

    if not raw_call:
        return "Unknown"

    # WPX Rule: Maritime mobile does not count as a prefix. This is the highest priority.
    if raw_call.upper().strip().endswith('/MM'):
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
        return "Unknown"
    
    return prefix_result

def calculate_wpx_prefixes(df: pd.DataFrame) -> pd.Series:
    """
    Calculates the WPX prefix for every QSO in a DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame of QSOs. Must contain 'Call', 'DXCCPfx',
                           and 'portableid' columns.

    Returns:
        pd.Series: A Pandas Series containing the calculated WPX prefix for each QSO.
    """
    required_cols = ['Call', 'DXCCPfx', 'portableid']
    for col in required_cols:
        if col not in df.columns:
            logging.error(f"Input DataFrame for WPX prefix calculation must contain a '{col}' column. Returning Unknowns.")
            return pd.Series("Unknown", index=df.index)

    return df.apply(_get_wpx_prefix_from_row, axis=1)