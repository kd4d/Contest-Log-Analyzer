# Contest Log Analyzer/contest_tools/contest_specific_annotations/cq_wpx_prefix.py
#
# Purpose: Provides a contest-specific function to determine the WPX prefix
#          for a given callsign according to the CQ WPX contest rules.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-02
# Version: 0.28.2-Beta
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
## [0.28.2-Beta] - 2025-08-02
### Changed
# - Complete rewrite of the prefix determination logic to implement a new,
#   comprehensive, and hierarchical set of rules based on user specification.
# - The routine now accepts the full DataFrame row and uses the `DXCCPfx` and
#   a new `portableid` field from `get_cty.py` to resolve ambiguity.
### Added
# - A standalone cleaning function to strip suffixes like /P, /M, etc.
# - Logic to handle all portable cases: `call/digit` (e.g., WN5N/7->WN7),
#   `call/letters` (e.g., LX/KD4D->LX0), and `call/prefix` (e.g., WN5N/KQ7->KQ7).
# - Logic for non-portable calls, including an override for `DXCCPfx` matches
#   (e.g., VP2VMM->VP2V) and a default "up to last digit" rule.
### Fixed
# - All previously identified bugs related to incorrect prefix determination
#   for portable and complex callsigns are resolved by the new algorithm.
#
## [0.22.0-Beta] - 2025-07-30
# - Initial release of the WPX prefix calculation module.
import pandas as pd
import re

def _clean_callsign(call: str) -> str:
    """
    Strips common non-prefix suffixes and cleans the callsign for analysis.
    This logic is intentionally kept separate from get_cty.py.
    """
    if not isinstance(call, str) or not call:
        return ""
    
    call = call.upper().strip()
    call = call.partition('-')[0]
    
    # This list is for suffixes that are NOT part of a portable designator
    suffixes_to_strip = ['/P', '/M', '/A', '/E', '/J', '/B', '/QRP']
    for suffix in suffixes_to_strip:
        if call.endswith(suffix):
            call = call[:-len(suffix)]
            break
    return call

def _get_prefix_for_non_portable(call: str, dxc_pfx: str) -> str:
    """
    Determines the WPX prefix for a standard, non-portable callsign.
    """
    # Rule 1: Override - if the call starts with its DXCC prefix, use that.
    if dxc_pfx and dxc_pfx != "Unknown" and call.startswith(dxc_pfx):
        return dxc_pfx

    # Rule 2: Default - everything up to and including the last digit.
    match = re.search(r'\d(?!.*\d)', call)
    if match:
        last_digit_index = match.start()
        return call[:last_digit_index + 1]
    
    # Rule 3: No number fallback - first two letters plus a zero.
    if len(call) >= 2:
        return call[:2] + '0'
    
    return "Unknown"

def _get_wpx_prefix_from_row(row: pd.Series) -> str:
    """
    Main logic to determine a WPX prefix from a full DataFrame row.
    """
    raw_call = row.get('Call')
    dxc_pfx = row.get('DXCCPfx')
    portable_id = row.get('portableid')

    if not raw_call:
        return "Unknown"

    # WPX Rule: Maritime mobile does not count as a prefix. Highest priority.
    if raw_call.upper().strip().endswith('/MM'):
        return "Unknown"

    cleaned_call = _clean_callsign(raw_call)

    # --- Portable Call Logic ---
    if portable_id:
        if dxc_pfx == "Unknown":
            return "Unknown"

        # Rule: call/digit (e.g., WN5N/7 -> WN7)
        if len(portable_id) == 1 and portable_id.isdigit():
            root_call = cleaned_call.split('/')[0]
            # We need the DXCC of the root call to properly find its prefix
            # This is a complex dependency we assume is handled by get_cty
            root_prefix = _get_prefix_for_non_portable(root_call, dxc_pfx)
            
            match = re.search(r'\d(?!.*\d)', root_prefix)
            if match:
                last_digit_index = match.start()
                return root_prefix[:last_digit_index] + portable_id
            return root_prefix + portable_id

        # Rule: call/letters (e.g., LX/KD4D -> LX0)
        if portable_id.isalpha():
            return portable_id + '0'

        # Rule: call/prefix (e.g., VP2V/KD4D -> VP2V)
        return portable_id

    # --- Non-Portable Call Logic ---
    else:
        return _get_prefix_for_non_portable(cleaned_call, dxc_pfx)

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
            raise ValueError(f"Input DataFrame must contain a '{col}' column.")

    return df.apply(_get_wpx_prefix_from_row, axis=1)