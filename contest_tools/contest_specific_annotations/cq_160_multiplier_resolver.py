# Contest Log Analyzer/contest_tools/contest_specific_annotations/cq_160_multiplier_resolver.py
#
# Purpose: Provides contest-specific logic to resolve CQ 160 contest multipliers
#          (States/Provinces for DX, DXCC for W/VE).
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-09-08
# Version: 0.62.0-Beta
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
## [0.62.0-Beta] - 2025-09-08
### Changed
# - Updated script to read the new CONTEST_INPUT_DIR environment variable.
## [0.40.0-Beta] - 2025-08-24
### Changed
# - Modified resolver to create and populate a STPROV_MultName column
#   to provide full names for State/Province multipliers.
## [0.30.41-Beta] - 2025-08-24
### Fixed
# - Corrected logic to populate the DXCC multiplier value column with the
#   DXCC Prefix instead of the full DXCC Name, fixing the redundant name
#   bug in downstream reports.
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
from typing import Optional, Tuple

def resolve_multipliers(df: pd.DataFrame, my_location_type: Optional[str]) -> pd.DataFrame:
    """
    Resolves multipliers for the CQ 160 contest.
    """
    if df.empty:
        return df

    df['STPROV_Mult'] = pd.NA
    df['STPROV_MultName'] = pd.NA
    df['DXCC_Mult'] = pd.NA
    df['DXCC_MultName'] = pd.NA

    root_dir = os.environ.get('CONTEST_INPUT_DIR', '').strip().strip("'").strip('"')
    data_dir = os.path.join(root_dir, 'data')
    alias_lookup = AliasLookup(data_dir, 'NAQPmults.dat')

    def get_stprov_mult(row) -> Tuple[Optional[str], Optional[str]]:
        if row.get('DXCCName') in ["United States", "Canada"]:
            location = row.get('RcvdLocation', '')
            mult_abbr, mult_name = alias_lookup.get_multiplier(location)
            return mult_abbr, mult_name
        return pd.NA, pd.NA

    df[['STPROV_Mult', 'STPROV_MultName']] = df.apply(get_stprov_mult, axis=1, result_type='expand')

    df['DXCC_Mult'] = df['DXCCPfx']
    df['DXCC_MultName'] = df['DXCCName']

    return df