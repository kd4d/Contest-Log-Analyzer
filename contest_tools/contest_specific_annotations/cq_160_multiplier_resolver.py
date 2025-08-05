# Contest Log Analyzer/contest_tools/contest_specific_annotations/cq_160_multiplier_resolver.py
#
# Purpose: Provides contest-specific logic to resolve CQ 160 contest multipliers
#          (States/Provinces for DX, DXCC for W/VE).
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-05
# Version: 0.30.0-Beta
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
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
# - Standardized all project files to a common baseline version.
import pandas as pd
import os
from ..core_annotations._core_utils import AliasLookup
from typing import Optional

def resolve_multipliers(df: pd.DataFrame, my_location_type: Optional[str]) -> pd.DataFrame:
    """
    Resolves multipliers for the CQ 160 contest based on the logger's location.
    - W/VE stations get DXCC entities as multipliers.
    - DX stations get US States and Canadian Provinces as multipliers.
    """
    if df.empty or not my_location_type:
        return df

    # Initialize output columns
    df['STPROV_Mult'] = pd.NA
    df['DXCC_Mult'] = pd.NA
    df['DXCC_MultName'] = pd.NA

    # --- W/VE Logger Logic ---
    if my_location_type == "W/VE":
        # Rule: W/VE stations work the world. Multipliers are DXCC entities.
        # We need to explicitly exclude QSOs with other W/VE stations from counting as mults.
        worked_location_is_dx = ~df['DXCCName'].isin(["United States", "Canada"])
        
        # Populate DXCC multiplier columns only for valid DX contacts
        df.loc[worked_location_is_dx, 'DXCC_Mult'] = df.loc[worked_location_is_dx, 'DXCCName']
        df.loc[worked_location_is_dx, 'DXCC_MultName'] = df.loc[worked_location_is_dx, 'DXCCName']

    # --- DX Logger Logic ---
    elif my_location_type == "DX":
        # Rule: DX stations only work W/VE stations. Multipliers are US States / Canadian Provinces.
        data_dir = os.environ.get('CONTEST_DATA_DIR', '').strip().strip('"').strip("'")
        alias_lookup = AliasLookup(data_dir, 'NAQPmults.dat')

        # We only care about QSOs where the worked station is in the US or Canada
        is_w_ve_contact = df['DXCCName'].isin(["United States", "Canada"])
        
        def get_stprov_mult(row):
            if not is_w_ve_contact.get(row.name, False):
                return pd.NA
                
            # For W/VE contacts, the multiplier is in the 'RcvdLocation' field.
            location = row.get('RcvdLocation', '')
            mult_abbr, _ = alias_lookup.get_multiplier(location)
            return mult_abbr
            
        df['STPROV_Mult'] = df.apply(get_stprov_mult, axis=1)

    return df