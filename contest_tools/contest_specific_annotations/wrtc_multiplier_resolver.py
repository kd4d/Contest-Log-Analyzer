# contest_tools/contest_specific_annotations/wrtc_multiplier_resolver.py
#
# Purpose: Provides the custom multiplier resolver for the WRTC contest series.
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
from typing import Dict, Any, Optional
from ..contest_definitions import ContestDefinition
from ..core_annotations._iaru_mult_utils import load_officials_set, resolve_iaru_hq_official

def resolve_multipliers(df: pd.DataFrame, my_location_type: str, root_input_dir: str, contest_def: ContestDefinition) -> pd.DataFrame:
    """
    Resolves multipliers for WRTC contests.
    Multipliers: DXCC Countries, HQ Stations, IARU Officials.
    Rule: Counted once per band, regardless of mode.
    
    Rule 8.2: HQ Stations and Officials do not count for DXCC multipliers.
    """
    if df.empty:
        return df

    # Initialize multiplier columns with object dtype to allow string values
    # Use df.index to ensure proper alignment and dtype
    if 'Mult_DXCC' not in df.columns:
        df['Mult_DXCC'] = pd.Series(index=df.index, dtype='object')
    else:
        df['Mult_DXCC'] = df['Mult_DXCC'].astype('object')
    if 'Mult_DXCCName' not in df.columns:
        df['Mult_DXCCName'] = pd.Series(index=df.index, dtype='object')
    else:
        df['Mult_DXCCName'] = df['Mult_DXCCName'].astype('object')
    if 'Mult_HQ' not in df.columns:
        df['Mult_HQ'] = pd.Series(index=df.index, dtype='object')
    else:
        df['Mult_HQ'] = df['Mult_HQ'].astype('object')
    if 'Mult_Official' not in df.columns:
        df['Mult_Official'] = pd.Series(index=df.index, dtype='object')
    else:
        df['Mult_Official'] = df['Mult_Official'].astype('object')
    
    # Load officials set for HQ/Official parsing
    officials_set = load_officials_set(root_input_dir)
    
    # Process each row
    for idx, row in df.iterrows():
        exchange = row.get('RcvdMult')
        
        # Use shared utility for HQ/Official parsing
        if pd.notna(exchange):
            hq_official = resolve_iaru_hq_official(exchange, officials_set)
            if hq_official['hq']:
                df.loc[idx, 'Mult_HQ'] = hq_official['hq']
            if hq_official['official']:
                df.loc[idx, 'Mult_Official'] = hq_official['official']
        
        # DXCC multiplier (WRTC-specific, not used in IARU-HF)
        dxcc_pfx = row.get('DXCCPfx')
        dxcc_name = row.get('DXCCName')
        
        if pd.notna(dxcc_pfx) and pd.notna(dxcc_name):
            df.loc[idx, 'Mult_DXCC'] = dxcc_pfx
            df.loc[idx, 'Mult_DXCCName'] = dxcc_name
    
    # Rule 8.2: HQ/Officials do not count for DXCC.
    # We nullify the DXCC multiplier if an HQ or Official multiplier is present.
    hq_or_official_mask = df['Mult_HQ'].notna() | df['Mult_Official'].notna()
    df.loc[hq_or_official_mask, ['Mult_DXCC', 'Mult_DXCCName']] = pd.NA
    
    return df
