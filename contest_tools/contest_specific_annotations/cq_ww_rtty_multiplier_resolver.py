# contest_tools/contest_specific_annotations/cq_ww_rtty_multiplier_resolver.py
#
# Purpose: Provides contest-specific logic to resolve CQ WW RTTY multipliers
#          (W/VE QTHs) from exchange data.
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

import pandas as pd
import os
import logging
from ..core_annotations._core_utils import AliasLookup
from typing import Optional
from ..contest_definitions import ContestDefinition

def resolve_multipliers(
    df: pd.DataFrame, 
    my_location_type: Optional[str], 
    root_input_dir: str, 
    contest_def: ContestDefinition
) -> pd.DataFrame:
    """
    Resolves multipliers for CQ WW RTTY contest.
    
    Multipliers:
    - Mult1: Countries (DXCC/WAE) - handled by standard rules
    - Mult2: Zones (CQ Zones) - handled by standard rules
    - Mult3: W/VE QTHs - custom logic here
    
    Rules:
    - All loggers (US/VE/DX) can earn W/VE QTH multipliers when working US/VE stations
    - Exchange RcvdLocation takes priority over cty.dat
    - AK/HI do not count as W/VE QTH multipliers (country multipliers only)
    - "DX" in exchange = no W/VE QTH multiplier
    - Missing QTH = error (flag as "Unknown")
    """
    if df.empty:
        return df
    
    # Get multiplier rule for W/VE QTHs
    wve_rule = next((r for r in contest_def.multiplier_rules if r['name'] == 'W/VE QTHs'), None)
    if not wve_rule:
        raise ValueError("W/VE QTHs multiplier rule not found in contest definition")
    
    mult3_col = wve_rule['value_column']
    mult3_name_col = wve_rule['name_column']
    
    # Initialize columns
    df[mult3_col] = pd.NA
    df[mult3_name_col] = pd.NA
    
    # Load alias lookup
    data_dir = os.path.join(root_input_dir, 'data')
    alias_lookup = AliasLookup(data_dir, 'ARRLDXmults.dat')
    
    # Constants
    NON_CONTIGUOUS_STATES = {'AK', 'HI'}
    
    # Process each row
    for idx, row in df.iterrows():
        rcvd_location = row.get('RcvdLocation', '')
        dxcc_pfx = row.get('DXCCPfx', '')
        
        # Validate: QTH cannot be missing
        if pd.isna(rcvd_location) or not rcvd_location or not str(rcvd_location).strip():
            # This is an error - flag it (similar to X-QSO)
            logging.warning(f"Missing QTH in exchange for QSO with {row.get('Call', 'Unknown')} - line should be flagged")
            df.loc[idx, mult3_col] = "Unknown"
            continue
        
        rcvd_location = str(rcvd_location).strip().upper()
        
        # Case 1: "DX" in exchange = no W/VE QTH multiplier
        if rcvd_location == "DX":
            df.loc[idx, mult3_col] = pd.NA
            df.loc[idx, mult3_name_col] = pd.NA
            continue
        
        # Case 2: AK/HI = no W/VE QTH multiplier (country multiplier only)
        if rcvd_location in NON_CONTIGUOUS_STATES:
            df.loc[idx, mult3_col] = pd.NA
            df.loc[idx, mult3_name_col] = pd.NA
            continue
        
        # Case 3: Valid US/VE state/province
        # Check if this is a US/VE contact (for W/VE QTH multiplier eligibility)
        # Note: All loggers can earn these multipliers, but only when working US/VE stations
        is_us_ve_contact = (
            dxcc_pfx in ['K', 'VE'] or 
            (isinstance(dxcc_pfx, str) and dxcc_pfx.startswith('K')) or 
            (isinstance(dxcc_pfx, str) and dxcc_pfx.startswith('VE')) or
            dxcc_pfx in ['KL', 'KH6']  # AK/HI are US but don't get state mults
        )
        
        if is_us_ve_contact:
            # Resolve via alias lookup
            resolved_mult, resolved_name = alias_lookup.get_multiplier(rcvd_location)
            
            if pd.notna(resolved_mult) and resolved_mult != "Unknown":
                # Double-check: resolved multiplier should not be AK/HI
                if resolved_mult not in NON_CONTIGUOUS_STATES:
                    df.loc[idx, mult3_col] = resolved_mult
                    df.loc[idx, mult3_name_col] = resolved_name
                else:
                    # Resolved to AK/HI - no multiplier
                    df.loc[idx, mult3_col] = pd.NA
                    df.loc[idx, mult3_name_col] = pd.NA
            else:
                # Unresolvable location
                df.loc[idx, mult3_col] = "Unknown"
                df.loc[idx, mult3_name_col] = pd.NA
        else:
            # Not a US/VE contact - no W/VE QTH multiplier
            df.loc[idx, mult3_col] = pd.NA
            df.loc[idx, mult3_name_col] = pd.NA
    
    return df
