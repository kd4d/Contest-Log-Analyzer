# Contest Log Analyzer/contest_tools/contest_specific_annotations/naqp_multiplier_resolver.py
#
# Purpose: Provides contest-specific logic to resolve NAQP multipliers
#          (States/Provinces and North American DXCC entities).
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
    Resolves multipliers for the NAQP contest.
    - Differentiates between US/VE State/Province multipliers and other North American DXCC multipliers.
    """
    if df.empty:
        return df

    # Initialize output columns
    df['STPROV_Mult'] = pd.NA
    df['NADXCC_Mult'] = pd.NA
    df['NADXCC_MultName'] = pd.NA

    data_dir = os.environ.get('CONTEST_DATA_DIR', '').strip().strip('"').strip("'")
    alias_lookup = AliasLookup(data_dir, 'NAQPmults.dat')

    # All stations can work all other North American stations.
    # The multiplier type depends on the location of the *worked* station.

    def get_mults(row):
        stprov_mult = pd.NA
        nadxcc_mult = pd.NA
        nadxcc_mult_name = pd.NA

        # We only care about QSOs where the worked station is in North America.
        # The 'WAEName' field from cty.dat is used to identify North American entities.
        if row.get('WAEName') != 'North America':
            return stprov_mult, nadxcc_mult, nadxcc_mult_name

        # For stations inside the US/Canada, the multiplier is the State or Province.
        if row.get('DXCCName') in ["United States", "Canada"]:
            location = row.get('RcvdLocation', '')
            mult_abbr, _ = alias_lookup.get_multiplier(location)
            stprov_mult = mult_abbr
        
        # For other North American stations, the multiplier is their DXCC entity.
        else:
            nadxcc_mult = row.get('DXCCName')
            nadxcc_mult_name = row.get('DXCCName')
            
        return stprov_mult, nadxcc_mult, nadxcc_mult_name

    # Apply the logic to each row
    mult_results = df.apply(get_mults, axis=1, result_type='expand')
    df[['STPROV_Mult', 'NADXCC_Mult', 'NADXCC_MultName']] = mult_results
    
    return df