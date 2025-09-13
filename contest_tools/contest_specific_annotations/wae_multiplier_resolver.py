# Contest Log Analyzer/contest_tools/contest_specific_annotations/wae_multiplier_resolver.py
#
# Author: Gemini AI
# Date: 2025-09-13
# Version: 0.85.4-Beta
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

# Prefixes for which call area districts count as multipliers
SPECIAL_DISTRICT_PREFIXES = {'K', 'W', 'VE', 'VK', 'ZL', 'ZS', 'JA', 'BY', 'PY', 'RA'}

def _get_call_area_district(row: pd.Series) -> Optional[str]:
    """
    Parses a callsign to find the call area district if it's from a
    special country for WAE multipliers.
    """
    call = row.get('Call', '')
    dxcc_pfx = row.get('DXCCPfx', '')

    if not call or not dxcc_pfx:
        return None

    # Check if the base DXCC prefix is one of the special ones
    base_pfx = re.match(r'[A-Z]+', dxcc_pfx)
    if not base_pfx or base_pfx.group(0) not in SPECIAL_DISTRICT_PREFIXES:
        return None

    # Handle the specific RA8, RA9, RA0 case
    if base_pfx.group(0) == 'RA':
        match = re.search(r'RA([890])', call)
        if match:
            return f"RA{match.group(1)}"
        return None # Other RA districts don't count

    # General case for other special prefixes
    match = re.search(r'[A-Z]+(\d)', call)
    if match:
        district_num = match.group(1)
        # Use the base prefix (e.g., 'W' for a 'K' call) for the multiplier ID
        return f"{base_pfx.group(0)}{district_num}"
        
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

    # This resolver now ONLY handles the special case for European loggers
    # working specific DX stations for call-area multipliers (Mult2).
    # The primary multiplier (Mult1) is handled by the 'wae_dxcc' source
    # key in contest_log.py.
    if my_location_type == 'DX':
        # Filter for QSOs with non-European stations
        non_eu_df = df[df['Continent'] != 'EU'].copy()
        if not non_eu_df.empty:
            districts = non_eu_df.apply(_get_call_area_district, axis=1)
            df.loc[districts.index, 'Mult2'] = districts
            df.loc[districts.index, 'Mult2Name'] = districts
            
    return df