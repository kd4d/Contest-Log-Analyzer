# Contest Log Analyzer/contest_tools/contest_specific_annotations/cq_wpx_prefix.py
#
# Purpose: Provides contest-specific logic to resolve WPX prefix multipliers.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-10
# Version: 0.31.51-Beta
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
from typing import Optional

def _get_prefix(call: str) -> Optional[str]:
    """
    Extracts the WPX prefix from a given callsign.
    Follows the rules outlined in WPXPrefixLookupAlgorithm.md.
    """
    if not call or pd.isna(call):
        return None

    # Step 1: Remove Portable Indicators
    call = re.split(r'/[AMP]{1,2}$', call)[0]

    # Step 2: Determine the standard prefix (initial letter/digit/letter block)
    # This pattern captures the first group of letters, first group of digits,
    # and the immediately following group of letters.
    match = re.match(r'([A-Z]+)(\d+)([A-Z]*)', call)
    if not match:
        return None

    standard_prefix = "".join(match.groups())

    # Step 3: Apply the special Letter-Digit-Letter (LDL) case.
    # Check if the standard prefix matches the LDL pattern (e.g., K3M, N8S).
    ldl_match = re.match(r'^[A-Z]\d[A-Z]$', standard_prefix)
    if ldl_match:
        # If it's an LDL prefix, the final prefix is the Letter-Digit part.
        return standard_prefix[:-1]
    else:
        # Otherwise, the standard prefix is the final prefix.
        return standard_prefix

def calculate_wpx_prefixes(df: pd.DataFrame) -> pd.Series:
    """
    Calculates the WPX prefix for each QSO, returning a sparse Series that
    contains the prefix only for the first time it was worked on each band.
    """
    if 'Call' not in df.columns or 'Datetime' not in df.columns or 'Band' not in df.columns:
        return pd.Series([None] * len(df), index=df.index, dtype=object)

    # Create a temporary DataFrame to calculate prefixes for all QSOs first
    df_temp = df[['Datetime', 'Call', 'Band']].copy()
    df_temp['Prefix'] = df_temp['Call'].apply(_get_prefix)
    
    # Sort by time to process QSOs chronologically
    df_temp.sort_values(by='Datetime', inplace=True)
    
    seen_prefix_band_combos = set()
    results_dict = {}

    for index, row in df_temp.iterrows():
        prefix = row.get('Prefix')
        band = row.get('Band')
        
        if pd.notna(prefix) and pd.notna(band):
            combo = (prefix, band)
            if combo not in seen_prefix_band_combos:
                seen_prefix_band_combos.add(combo)
                results_dict[index] = prefix # Store prefix for this "first on band" QSO
            else:
                results_dict[index] = None # Subsequent QSOs for this combo get None
        else:
            results_dict[index] = None

    # Reconstruct the Series in the original DataFrame's order
    final_series = pd.Series(results_dict, index=df.index)
    
    return final_series