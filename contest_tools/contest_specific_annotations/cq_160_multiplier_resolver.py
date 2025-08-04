# Contest Log Analyzer/contest_tools/contest_specific_annotations/cq_160_multiplier_resolver.py
#
# Purpose: Provides contest-specific logic to resolve CQ 160 multipliers
#          (States/Provinces/DXCC) from the log exchange and CTY data.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-04
# Version: 0.29.5-Beta
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
## [0.29.5-Beta] - 2025-08-04
### Changed
# - Replaced all `print` statements with calls to the new logging framework.
## [0.29.3-Beta] - 2025-08-04
### Changed
# - Updated the import path for the AliasLookup class to point to the new
#   _core_utils module, resolving a circular dependency.
## [0.29.2-Beta] - 2025-08-04
### Changed
# - Reworked the resolver to be the single source of truth for multipliers.
# - The resolver now outputs two distinct, clean columns (STPROV_Mult, DXCC_Mult)
#   to permanently fix all double-counting and mis-categorization bugs.
import pandas as pd
import os
from typing import Dict, Tuple, Optional
from ..core_annotations._core_utils import AliasLookup

def resolve_multipliers(df: pd.DataFrame, my_location_type: Optional[str]) -> pd.DataFrame:
    """
    Resolves multipliers for CQ 160, creating separate columns for the two
    distinct multiplier types and their corresponding names.
    """
    if df.empty:
        df['STPROV_Mult'] = pd.NA
        df['DXCC_Mult'] = pd.NA
        df['DXCC_MultName'] = pd.NA
        return df

    data_dir = os.environ.get('CONTEST_DATA_DIR').strip().strip('"').strip("'")
    alias_lookup = AliasLookup(data_dir, 'CQ160mults.dat')
    
    stprov_mults = []
    dxcc_mults = []
    dxcc_mult_names = []

    for index, row in df.iterrows():
        stprov_val = pd.NA
        dxcc_val = pd.NA
        dxcc_name_val = pd.NA

        # Logic for all stations: check for State/Province multiplier first.
        location = row.get('RcvdLocation', '')
        st_prov_mult, st_prov_name = alias_lookup.get_multiplier(location)
        
        if pd.notna(st_prov_mult):
            stprov_val = st_prov_mult
        else:
            # If it's not a State/Province, it might be a DXCC multiplier.
            # This is only valid for W/VE stations.
            if my_location_type == "W/VE":
                worked_entity = row.get('DXCCName', '')
                if worked_entity not in ["United States", "Canada"]:
                    # Per CQ rules, check for a WAE prefix first, then fall back to DXCC.
                    wae_pfx = row.get('WAEPfx')
                    if pd.notna(wae_pfx) and wae_pfx != '':
                         dxcc_val = wae_pfx
                         dxcc_name_val = row.get('WAEName', '')
                    else:
                         dxcc_val = row.get('DXCCPfx', pd.NA)
                         dxcc_name_val = row.get('DXCCName', pd.NA)

        stprov_mults.append(stprov_val)
        dxcc_mults.append(dxcc_val)
        dxcc_mult_names.append(dxcc_name_val)

    df['STPROV_Mult'] = stprov_mults
    df['DXCC_Mult'] = dxcc_mults
    df['DXCC_MultName'] = dxcc_mult_names
    
    return df