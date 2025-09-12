# Contest Log Analyzer/contest_tools/contest_specific_annotations/wae_multiplier_resolver.py
#
# Author: Gemini AI
# Date: 2025-09-12
# Version: 1.0.0-Beta
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
## [1.0.0-Beta] - 2025-09-12
# - Initial release.
#
import pandas as pd
import re
from typing import Dict, Any, Optional

# [cite_start]Prefixes for which call area districts count as multipliers [cite: 3586]
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

    # --- Rule Set for DX Loggers ---
    if my_location_type == 'DX':
        # [cite_start]Multipliers are WAE countries only [cite: 3584]
        df['Mult1'] = df['WAEPfx']
        df['Mult1Name'] = df['WAEName']
        df['Mult2'] = pd.NA
        df['Mult2Name'] = pd.NA

    # --- Rule Set for EU Loggers ---
    elif my_location_type == 'W/VE': # Note: W/VE here means European
        # [cite_start]Multiplier 1: Non-European DXCC entities [cite: 3585]
        non_eu_mask = df['Continent'] != 'EU'
        df.loc[non_eu_mask, 'Mult1'] = df.loc[non_eu_mask, 'DXCCPfx']
        df.loc[non_eu_mask, 'Mult1Name'] = df.loc[non_eu_mask, 'DXCCName']

        # [cite_start]Multiplier 2: Special Call Area Districts [cite: 3586]
        districts = df.apply(_get_call_area_district, axis=1)
        df['Mult2'] = districts
        df['Mult2Name'] = districts # For districts, the name is the same as the ID
    
    else:
        # Default case if location type is unknown
        df['Mult1'] = pd.NA
        df['Mult1Name'] = pd.NA
        df['Mult2'] = pd.NA
        df['Mult2Name'] = pd.NA

    return df