# Contest Log Analyzer/contest_tools/contest_specific_annotations/naqp_multiplier_resolver.py
#
# Purpose: Provides contest-specific logic to resolve NAQP multipliers
#          (States/Provinces and North American DXCC entities).
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-17
# Version: 0.37.3-Beta
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
## [0.37.3-Beta] - 2025-08-17
### Fixed
# - Corrected the hardcoded prefix for Alaska from KL7 to KL to ensure
#   it is correctly classified as a State/Province multiplier.
## [0.37.2-Beta] - 2025-08-17
### Fixed
# - Corrected multiplier logic to align with official NAQP rules by
#   removing the 'XE' prefix from the State/Province check, ensuring
#   Mexican stations are correctly classified as NA DXCC multipliers.
## [0.37.1-Beta] - 2025-08-17
### Changed
# - Refactored resolver to populate two separate columns (`Mult_STPROV` and
#   `Mult_NADXCC`) to enable distinct multiplier reporting.
## [0.32.21-Beta] - 2025-08-14
### Fixed
# - Corrected the primary conditional check to include KH6 and KL7, ensuring
#   Alaska and Hawaii are treated as State multipliers per NAQP rules.
## [0.32.20-Beta] - 2025-08-14
### Fixed
# - Rewrote multiplier logic to correctly handle the three NAQP multiplier
#   types (State/Prov, NA DXCC, Unknown) and consolidate them into the
#   single 'Mult1' column for proper scoring.
## [0.31.46-Beta] - 2025-08-11
### Fixed
# - Corrected multiplier logic to handle the special cases for Alaska and
#   Hawaii, ensuring they are always processed as State/Province multipliers.
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
from typing import Optional, Any, Tuple

def _get_naqp_multiplier(row: pd.Series, alias_lookup: AliasLookup) -> Tuple[Any, Any]:
    """
    Applies the NAQP multiplier logic to a single QSO row, returning separate
    values for State/Province and NA DXCC multipliers.
    """
    stprov_mult = pd.NA
    nadxcc_mult = pd.NA
    
    dxcc_pfx = row.get('DXCCPfx')
    continent = row.get('Continent')
    rcvd_location = row.get('RcvdLocation')

    # 1. Initial Sanity Check
    if pd.isna(dxcc_pfx) or dxcc_pfx == 'Unknown':
        return "Unknown", pd.NA

    # 2. Check for US (including AK/HI) or Canada (State/Province mults)
    if dxcc_pfx in ['K', 'KH6', 'KL', 'VE']:
        mult, _ = alias_lookup.get_multiplier(rcvd_location)
        stprov_mult = mult if pd.notna(mult) else "Unknown"

    # 3. Check for Other North American DXCC
    elif continent == 'NA':
        nadxcc_mult = dxcc_pfx

    return stprov_mult, nadxcc_mult


def resolve_multipliers(df: pd.DataFrame, my_location_type: Optional[str]) -> pd.DataFrame:
    """
    Resolves multipliers for the NAQP contest by identifying the multiplier
    for each QSO and placing it into the appropriate new column.
    """
    if df.empty:
        return df

    # Ensure required columns exist before proceeding
    required_cols = ['DXCCPfx', 'Continent', 'RcvdLocation']
    for col in required_cols:
        if col not in df.columns:
            df['Mult_STPROV'] = pd.NA
            df['Mult_NADXCC'] = pd.NA
            return df

    # Initialize the alias lookup utility for NAQP multipliers.
    root_dir = os.environ.get('CONTEST_LOGS_REPORTS', '').strip().strip('"').strip("'")
    data_dir = os.path.join(root_dir, 'data')
    alias_lookup = AliasLookup(data_dir, 'NAQPmults.dat')

    # Apply the logic to each row and assign the results to two new columns
    df[['Mult_STPROV', 'Mult_NADXCC']] = df.apply(
        _get_naqp_multiplier, axis=1, result_type='expand', alias_lookup=alias_lookup
    )
    
    # Clean up old columns if they exist from previous versions
    cols_to_drop = ['Mult1', 'STPROV_Mult', 'NADXCC_Mult', 'NADXCC_MultName']
    df.drop(columns=[col for col in cols_to_drop if col in df.columns], inplace=True)

    return df
