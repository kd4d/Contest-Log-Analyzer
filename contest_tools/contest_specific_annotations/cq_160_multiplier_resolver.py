# Contest Log Analyzer/contest_tools/contest_specific_annotations/cq_160_multiplier_resolver.py
#
# Purpose: Provides contest-specific logic to resolve CQ 160 contest multipliers
#          (States/Provinces for DX, DXCC for W/VE).
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-06
# Version: 0.30.40-Beta
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
## [0.30.40-Beta] - 2025-08-06
### Fixed
# - Updated all references to the old CONTEST_DATA_DIR environment variable
#   to use the correct CONTEST_LOGS_REPORTS variable.
## [0.30.9-Beta] - 2025-08-05
### Fixed
# - Rewrote the multiplier logic to correctly reflect the CQ 160 rules.
import pandas as pd
import os
from ..core_annotations._core_utils import AliasLookup
from typing import Optional

def resolve_multipliers(df: pd.DataFrame, my_location_type: Optional[str]) -> pd.DataFrame:
    """
    Resolves multipliers for the CQ 160 contest.
    """
    if df.empty:
        return df

    df['STPROV_Mult'] = pd.NA
    df['DXCC_Mult'] = pd.NA
    df['DXCC_MultName'] = pd.NA

    root_dir = os.environ.get('CONTEST_LOGS_REPORTS', '').strip().strip('"').strip("'")
    data_dir = os.path.join(root_dir, 'data')
    alias_lookup = AliasLookup(data_dir, 'NAQPmults.dat')

    def get_stprov_mult(row):
        if row.get('DXCCName') in ["United States", "Canada"]:
            location = row.get('RcvdLocation', '')
            mult_abbr, _ = alias_lookup.get_multiplier(location)
            return mult_abbr
        return pd.NA

    df['STPROV_Mult'] = df.apply(get_stprov_mult, axis=1)

    df['DXCC_Mult'] = df['DXCCName']
    df['DXCC_MultName'] = df['DXCCName']

    return df