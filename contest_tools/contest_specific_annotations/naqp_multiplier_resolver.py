# Contest Log Analyzer/contest_tools/contest_specific_annotations/naqp_multiplier_resolver.py
#
# Purpose: Provides contest-specific logic to resolve NAQP multipliers
#          (States/Provinces/NA DXCC) from the log exchange.
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
# - Renamed the DXCC multiplier column to `NADXCC_Mult` for clarity and
#   accuracy, as NAQP only allows North American DXCC entities as multipliers.
## [0.29.1-Beta] - 2025-08-04
### Changed
# - Rewrote resolver to use the shared AliasLookup class and create two
#   distinct, clean output columns (STPROV_Mult, DXCC_Mult) to fix the
#   double-counting bug.
## [0.29.0-Beta] - 2025-08-03
### Added
# - Initial release of the NAQP multiplier resolver module.
import pandas as pd
import os
from typing import Optional
from ..core_annotations._core_utils import AliasLookup

def resolve_multipliers(df: pd.DataFrame, my_location_type: Optional[str]) -> pd.DataFrame:
    """
    Resolves multipliers for NAQP, creating separate columns for State/Province
    and other North American DXCC entities to prevent double-counting.
    """
    if df.empty or 'RcvdLocation' not in df.columns:
        df['STPROV_Mult'] = pd.NA
        df['NADXCC_Mult'] = pd.NA
        df['NADXCC_MultName'] = pd.NA
        return df

    data_dir = os.environ.get('CONTEST_DATA_DIR').strip().strip('"').strip("'")
    alias_lookup = AliasLookup(data_dir, 'NAQPmults.dat')
    
    stprov_mults = []
    nadxcc_mults = []
    nadxcc_mult_names = []

    for index, row in df.iterrows():
        stprov_val = pd.NA
        nadxcc_val = pd.NA
        nadxcc_name_val = pd.NA
        
        location = row.get('RcvdLocation', '')
        st_prov_mult, st_prov_name = alias_lookup.get_multiplier(location)
        
        if pd.notna(st_prov_mult):
            stprov_val = st_prov_mult
        else:
            continent = row.get('Continent')
            if continent == 'NA':
                nadxcc_val = row.get('DXCCPfx', pd.NA)
                nadxcc_name_val = row.get('DXCCName', pd.NA)

        stprov_mults.append(stprov_val)
        nadxcc_mults.append(nadxcc_val)
        nadxcc_mult_names.append(nadxcc_name_val)

    df['STPROV_Mult'] = stprov_mults
    df['NADXCC_Mult'] = nadxcc_mults
    df['NADXCC_MultName'] = nadxcc_mult_names
    
    return df