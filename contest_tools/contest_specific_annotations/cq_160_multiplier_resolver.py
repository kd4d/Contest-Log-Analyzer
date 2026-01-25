# contest_tools/contest_specific_annotations/cq_160_multiplier_resolver.py
#
# Purpose: Provides contest-specific logic to resolve CQ 160 contest multipliers
#          (States/Provinces for all stations, DXCC+WAE for W/VE stations).
#          Multipliers are symmetric - both sides of a QSO get the same multiplier values.
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
from typing import Optional, Tuple
from ..contest_definitions import ContestDefinition

def resolve_multipliers(df: pd.DataFrame, my_location_type: Optional[str], root_input_dir: str, contest_def: ContestDefinition) -> pd.DataFrame:
    """
    Resolves multipliers for the CQ 160 contest.
    """
    if df.empty:
        return df
        
    # --- Dynamically get column names from the JSON blueprint ---
    try:
        stprov_rule = next((r for r in contest_def.multiplier_rules if r['name'] == 'STPROV'), None)
        dxcc_rule = next((r for r in contest_def.multiplier_rules if r['name'] == 'DXCC'), None)
        if not stprov_rule or not dxcc_rule:
            raise ValueError("Could not find STPROV or DXCC rules in definition.")
            
        stprov_col = stprov_rule['source_column']
        stprov_name_col = stprov_rule['source_name_column']
        dxcc_col = dxcc_rule['source_column']
        dxcc_name_col = dxcc_rule['source_name_column']
    except (AttributeError, KeyError, IndexError, ValueError) as e:
        logging.error(f"Could not extract CQ-160 column names from ContestDefinition: {e}. Aborting resolver.")
        return df

    data_dir = os.path.join(root_input_dir, 'data')
    alias_lookup = AliasLookup(data_dir, 'CQ160mults.dat')

    def get_stprov_mult(row) -> Tuple[Optional[str], Optional[str]]:
        if row.get('DXCCName') in ["United States", "Canada"]:
            location = row.get('RcvdLocation', '')
            mult_abbr, mult_name = alias_lookup.get_multiplier(location)
            return mult_abbr, mult_name
        return pd.NA, pd.NA

    df[[stprov_col, stprov_name_col]] = df.apply(get_stprov_mult, axis=1, result_type='expand')

    # --- Ensure multiplier columns are object type to avoid dtype warnings ---
    if dxcc_col not in df.columns:
        df[dxcc_col] = pd.Series(dtype='object')
    else:
        df[dxcc_col] = df[dxcc_col].astype('object')
    if dxcc_name_col not in df.columns:
        df[dxcc_name_col] = pd.Series(dtype='object')
    else:
        df[dxcc_name_col] = df[dxcc_name_col].astype('object')

    # --- DXCC/WAE Multiplier Assignment ---
    # Rules: "DXCC countries and including WAE countries"
    # - WAE entities use WAE identifiers (WAEPfx/WAEName) when available
    # - Non-WAE DXCC entities use DXCC identifiers (DXCCPfx/DXCCName)
    # - K and VE are excluded (they get STPROV multipliers only)
    # - IG9/IH9 are not on WAE list (they're in Africa, Zone 33) so use DXCC
    
    # Identify IG9/IH9 stations (check both WAEPfx and DXCCPfx to catch all cases)
    # IG9/IH9 are Italian stations operating from Africa (Zone 33)
    # For CQ 160, *IG9 is a legitimate multiplier and does NOT count as I (Italy)
    # They should use their WAE identifier (*IG9/*IH9) as the multiplier, NOT their DXCCPfx (I)
    # This allows them to be counted separately from regular Italy (I) multipliers
    is_ig9_ih9 = (
        (df['WAEPfx'].notna() & df['WAEPfx'].isin(['IG9', 'IH9', '*IG9', '*IH9'])) |
        (df['DXCCPfx'].notna() & df['DXCCPfx'].isin(['IG9', 'IH9']))
    )
    
    # Start with DXCC assignment for all (excluding K/VE and IG9/IH9)
    # IG9/IH9 will be handled separately to use their WAE identifier
    dxcc_mask = df['DXCCPfx'].notna() & (df['DXCCPfx'] != 'K') & (df['DXCCPfx'] != 'VE') & ~is_ig9_ih9
    df.loc[dxcc_mask, dxcc_col] = df.loc[dxcc_mask, 'DXCCPfx']
    df.loc[dxcc_mask, dxcc_name_col] = df.loc[dxcc_mask, 'DXCCName']
    
    # Handle IG9/IH9 separately: Use their WAE identifier AS-IS (keep asterisk, e.g., '*IG9')
    # This allows them to be counted separately from regular Italy (I) multipliers
    # For CQ 160, *IG9 is a legitimate multiplier and does NOT count as I
    # According to CTY.DAT, *IG9 is "African Italy" (Zone 33, Africa), a separate entity from Italy
    if is_ig9_ih9.sum() > 0:
        # Use WAEPfx as-is (keep the asterisk, so '*IG9' stays '*IG9')
        df.loc[is_ig9_ih9, dxcc_col] = df.loc[is_ig9_ih9, 'WAEPfx']
        df.loc[is_ig9_ih9, dxcc_name_col] = df.loc[is_ig9_ih9, 'WAEName']
    
    # Override with WAE for other WAE entities (excluding IG9/IH9 which are already handled)
    # Note: WAEPfx can be stored as "*IG9"/"*IH9" (with asterisk) or "IG9"/"IH9" (without)
    # Only apply WAE override when WAEName is set (indicating a valid WAE entity)
    # and WAEPfx is not empty (to avoid overwriting with empty strings)
    # and it's NOT IG9/IH9 (already handled separately above)
    wae_mask = (
        df['WAEName'].notna() &  # WAEName only set for valid WAE entities
        (df['WAEPfx'].notna()) &  # WAEPfx must exist
        (df['WAEPfx'] != '') &    # WAEPfx must not be empty string
        ~is_ig9_ih9  # Exclude IG9/IH9 - already handled separately above
    )
    df.loc[wae_mask, dxcc_col] = df.loc[wae_mask, 'WAEPfx']
    df.loc[wae_mask, dxcc_name_col] = df.loc[wae_mask, 'WAEName']
    
    # K and VE stations remain as pd.NA (they get STPROV multipliers only)

    return df