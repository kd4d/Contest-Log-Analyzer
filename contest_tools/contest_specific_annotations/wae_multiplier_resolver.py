# Contest Log Analyzer/contest_tools/contest_specific_annotations/wae_multiplier_resolver.py
#
# Author: Gemini AI
# Date: 2025-09-16
# Version: 0.87.5-Beta
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
# Purpose: This module provides a custom multiplier resolver for the WAE
#          Contest. It implements the asymmetric multiplier rules for
#          EU vs. non-EU stations and the special call area district logic.
#
# --- Revision History ---
## [0.87.5-Beta] - 2025-09-16
### Added
# - Added a high-priority logic block to the `_get_call_area_district`
#   function to correctly handle the special RA8/RA9/RA0 multipliers for
#   the UA9 (Asiatic Russia) DXCC entity.
## [0.87.4-Beta] - 2025-09-16
### Changed
# - Rewrote the `_get_call_area_district` function to correctly implement
#   the WAE multiplier rules. The new logic now uses the DXCCPfx for
#   eligibility and correctly parses both standard and portable callsigns.
## [0.87.1-Beta] - 2025-09-16
### Changed
# - Refactored module to be a self-contained, complete replacement for WAE
#   multiplier logic, in accordance with the new architectural contract.
# - The resolver now populates Mult1 with WAE/DXCC multipliers and Mult2
#   with Call Area Districts, correctly enforcing mutual exclusivity.
## [0.89.0-Beta] - 2025-09-15
### Fixed
# - Modified resolver to clear Mult1 when Mult2 is populated, making the multiplier types mutually exclusive to prevent double-counting.
## [0.88.2-Beta] - 2025-09-15
### Fixed
# - Corrected the primary conditional check from 'DX' to 'EU' to ensure multiplier logic runs for the correct station type.
## [0.85.4-Beta] - 2025-09-13
### Changed
# - Refactored module to only handle the special-case Mult2 (Call Area)
#   multiplier for European stations. Mult1 is now handled by the
#   'wae_dxcc' source key in the contest definition.
## [0.85.0-Beta] - 2025-09-13
### Fixed
# - Corrected a logical inversion where the rules for European and
#   non-European stations were swapped.
## [1.0.1-Beta] - 2025-09-12
### Fixed
# - Pre-initialized multiplier columns with dtype='object' to prevent
#   a pandas FutureWarning.
## [1.0.0-Beta] - 2025-09-12
# - Initial release.
#
import pandas as pd
import re
from typing import Dict, Any, Optional

# The canonical prefixes used to construct the final multiplier ID.
_CANONICAL_PREFIX_MAP = {
    'K': 'K', 'VE': 'VE', 'VK': 'VK', 'ZL': 'ZL',
    'ZS': 'ZS', 'JA': 'JA', 'BY': 'BY', 'PY': 'PY'
}
# The set of DXCC prefixes that are eligible for this special multiplier.
# Note that callsigns like W1AW have a DXCCPfx of 'K'.
ELIGIBLE_DXCC_PREFIXES = set(_CANONICAL_PREFIX_MAP.keys())


def _get_call_area_district(row: pd.Series) -> Optional[str]:
    """
    Parses a callsign to find the call area district if it's from a
    special country for WAE multipliers.
    """
    call = str(row.get('Call', ''))
    portable_id = str(row.get('portableid', ''))
    dxcc_pfx = str(row.get('DXCCPfx', ''))

    # --- Step 1: Handle high-priority UA9 (Asiatic Russia) case for RA8/9/0 ---
    if dxcc_pfx == 'UA9':
        digit = None
        if len(portable_id) == 1 and portable_id.isdigit():
            digit = portable_id
        else:
            match = re.match(r'[A-Z]+(\d)', call)
            if match:
                digit = match.group(1)
        
        if digit in ['8', '9', '0']:
            return f"UA9{digit}"
        elif digit is not None: # It's a UA9 station but not 8, 9, or 0
            return "UA99" # Fallback rule
        else:
            return None # No digit found

    # --- Step 2: General Eligibility Check for other special prefixes ---
    # A call is only eligible if its DXCC entity prefix is on the special list.
    # This correctly excludes entities like KH6, KL, etc.
    if dxcc_pfx not in ELIGIBLE_DXCC_PREFIXES:
        return None

    # --- Step 3: Determine Canonical Prefix ---
    canonical_prefix = _CANONICAL_PREFIX_MAP.get(dxcc_pfx)

    # --- Step 4: Find Call Area Digit (prioritizing portable suffix) ---
    call_area_digit = None
    if len(portable_id) == 1 and portable_id.isdigit():
        call_area_digit = portable_id
    else:
        # Parse the main callsign for the first digit after letters.
        # This correctly handles VK2004ABC -> 2
        match = re.match(r'[A-Z]+(\d)', call)
        if match:
            call_area_digit = match.group(1)

    # --- Step 5: Construct and Return Multiplier ---
    if call_area_digit:
        return f"{canonical_prefix}{call_area_digit}"
    
    return None


def resolve_multipliers(df: pd.DataFrame, my_location_type: str, root_input_dir: str) -> pd.DataFrame:
    """
    Resolves multipliers for the WAE Contest based on the logger's location.
    - Mult1: WAE Country or DXCC
    - Mult2: Call Area District
    """
    if df.empty:
        return df

    # Pre-initialize columns with a compatible dtype to prevent FutureWarnings
    for col in ['Mult1', 'Mult1Name', 'Mult2', 'Mult2Name']:
        if col not in df.columns:
            df[col] = pd.NA
            df[col] = df[col].astype('object')

    # --- Step 1: Populate Mult1 with WAE/DXCC for ALL applicable QSOs ---
    # This logic is moved here from contest_log.py to make this resolver self-contained.
    wae_mask = df['WAEName'].notna() & (df['WAEName'] != '')
    
    df.loc[wae_mask, 'Mult1'] = df.loc[wae_mask, 'WAEPfx']
    df.loc[wae_mask, 'Mult1Name'] = df.loc[wae_mask, 'WAEName']
    
    df.loc[~wae_mask, 'Mult1'] = df.loc[~wae_mask, 'DXCCPfx']
    df.loc[~wae_mask, 'Mult1Name'] = df.loc[~wae_mask, 'DXCCName']

    # --- Step 2: Handle special case for EU loggers working specific DX for Mult2 ---
    if my_location_type == 'EU':
        # Filter for QSOs with non-European stations
        non_eu_df = df[df['Continent'] != 'EU'].copy()
        if not non_eu_df.empty:
            districts = non_eu_df.apply(_get_call_area_district, axis=1)
            valid_districts = districts[districts.notna()]
            
            if not valid_districts.empty:
                df.loc[valid_districts.index, 'Mult2'] = valid_districts
                df.loc[valid_districts.index, 'Mult2Name'] = valid_districts
                # --- Step 3: Clear Mult1 where Mult2 was populated to enforce exclusivity ---
                df.loc[valid_districts.index, ['Mult1', 'Mult1Name']] = pd.NA
            
    return df