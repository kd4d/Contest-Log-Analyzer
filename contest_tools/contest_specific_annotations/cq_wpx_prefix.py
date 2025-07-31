# Contest Log Analyzer/contest_tools/contest_specific_annotations/cq_wpx_prefix.py
#
# Purpose: Provides a contest-specific function to determine the WPX prefix
#          for a given callsign according to the CQ WPX contest rules.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-30
# Version: 0.22.0-Beta
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

## [0.22.0-Beta] - 2025-07-30
# - Initial release of the WPX prefix calculation module.

import pandas as pd
import re

def _get_wpx_prefix(call: str) -> str:
    """
    Determines the WPX prefix for a single callsign based on contest rules.
    """
    if not isinstance(call, str) or not call:
        return "Unknown"

    call = call.upper().strip()

    # Rule: Maritime mobile, mobile, /A, /E, /J, /P do not count as prefixes.
    # We strip these common suffixes first.
    suffixes_to_strip = ['/MM', '/M', '/P', '/A', '/E', '/J']
    for suffix in suffixes_to_strip:
        if call.endswith(suffix):
            call = call[:-len(suffix)]
            break # Only strip one suffix

    # Rule: For portable operations, the portable designator becomes the prefix.
    if '/' in call:
        parts = call.split('/')
        prefix_part = parts[-1] # Standard international portable
        
        # Handle US/Canada portable where location is second
        home_call_pattern = re.compile(r'^(A[A-L]|K|N|W)[A-Z]?[0-9]')
        if home_call_pattern.match(parts[0]):
            prefix_part = parts[-1]
        else:
            prefix_part = parts[0]

        # Rule: Portable designators without numbers get a '0'
        if not any(char.isdigit() for char in prefix_part):
            # Find first letter sequence
            match = re.match(r'([A-Z]+)', prefix_part)
            if match and len(match.group(1)) >= 2:
                prefix_part = match.group(1)[:2] + '0'
            else: # Fallback for single-letter prefixes
                prefix_part += '0'
        
        call = prefix_part

    # Rule: The prefix is the letter/numeral combination before the first letter of the suffix.
    match = re.match(r'([A-Z0-9]+[0-9])', call)
    if match:
        return match.group(1)
    
    # Rule: Calls without numbers get a '0' after the first two letters.
    match = re.match(r'([A-Z]{2})', call)
    if match:
        return match.group(1) + '0'

    return "Unknown"

def calculate_wpx_prefixes(df: pd.DataFrame) -> pd.Series:
    """
    Calculates the WPX prefix for every QSO in a DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame of QSOs, must contain a 'Call' column.

    Returns:
        pd.Series: A Pandas Series containing the calculated WPX prefix for each QSO.
    """
    if 'Call' not in df.columns:
        raise ValueError("Input DataFrame must contain a 'Call' column.")

    return df['Call'].apply(_get_wpx_prefix)
