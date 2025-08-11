# Contest Log Analyzer/contest_tools/contest_specific_annotations/naqp_multiplier_resolver.py
#
# Purpose: Provides contest-specific logic to resolve NAQP multipliers
#          (States/Provinces and North American DXCC entities).
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-11
# Version: 0.31.45-Beta
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
## [0.31.45-Beta] - 2025-08-11
### Fixed
# - Corrected multiplier logic to properly handle Alaska (AK) and Hawaii (HI)
#   as State/Province multipliers instead of DXCC entities.
## [0.31.44-Beta] - 2025-08-11
### Fixed
# - Corrected logic to assign the DXCC Prefix (DXCCPfx) instead of the
#   full DXCC Name to the NADXCC_Mult column.
## [0.31.43-Beta] - 2025-08-10
### Changed
# - Refactored logic to use the 'Continent' field ('NA') instead of
#   'WAEName' for identifying North American stations.
## [0.30.40-Beta] - 2025-08-06
### Fixed
# - Updated all references to the old CONTEST_DATA_DIR environment variable
#   to use the correct CONTEST_LOGS_REPORTS variable.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
import pandas as pd
import os
from ..core_annotations._core_utils import AliasLookup
from typing import Optional

def resolve_multipliers(df: pd.DataFrame, my_location_type: Optional[str]) -> pd.DataFrame:
    """
    Resolves multipliers for the NAQP contest.
    """
    if df.empty:
        return df

    df['STPROV_Mult'] = pd.NA
    df['NADXCC_Mult'] = pd.NA
    df['NADXCC_MultName'] = pd.NA

    root_dir = os.environ.get('CONTEST_LOGS_REPORTS', '').strip().strip('"').strip("'")
    data_dir = os.path.join(root_dir, 'data')
    alias_lookup = AliasLookup(data_dir, 'NAQPmults.dat')

    def get_mults(row):
        stprov_mult = pd.NA
        nadxcc_mult = pd.NA
        nadxcc_mult_name = pd.NA

        if row.get('Continent') != 'NA':
            return stprov_mult, nadxcc_mult, nadxcc_mult_name

        if row.get('DXCCName') in ["United States", "Canada", "Alaska", "Hawaii"]:
            location = row.get('RcvdLocation', '')
            mult_abbr, _ = alias_lookup.get_multiplier(location)
            stprov_mult = mult_abbr
        else:
            nadxcc_mult = row.get('DXCCPfx')
            nadxcc_mult_name = row.get('DXCCName')
            
        return stprov_mult, nadxcc_mult, nadxcc_mult_name

    mult_results = df.apply(get_mults, axis=1, result_type='expand')
    df[['STPROV_Mult', 'NADXCC_Mult', 'NADXCC_MultName']] = mult_results
    
    return df