# Contest Log Analyzer/contest_tools/contest_specific_annotations/arrl_dx_multiplier_resolver.py
#
# Purpose: Provides contest-specific logic to resolve ARRL DX Contest multipliers
#          (States/Provinces) from callsigns or explicit exchange fields.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-24
# Version: 0.40.2-Beta
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
## [0.40.2-Beta] - 2025-08-24
### Changed
# - Refactored to use the standard AliasLookup utility.
# - Added logic to populate multiplier name columns (STPROV_MultName,
#   Mult_DXCCName) to support enhanced reporting.
## [0.33.2-Beta] - 2025-08-21
### Added
# - Added a temporary diagnostic log to print the source row for any
#   40M SD, NF, or YT multipliers at the point of resolution.
## [0.33.0-Beta] - 2025-08-21
### Changed
# - Refactored to use the new shared StateAndProvinceLookup utility.
# - Implemented the final, precise two-path algorithm for the "exchange
#   override", correctly handling US/VE, US-affiliated DX, and foreign
#   stations.
## [0.31.1-Beta] - 2025-08-21
### Fixed
# - Corrected a SyntaxError on line 66 by adding a missing colon.
import pandas as pd
import os
import logging
from ..core_annotations._core_utils import AliasLookup
from typing import Dict

def resolve_multipliers(df: pd.DataFrame, my_location_type: str) -> pd.DataFrame:
    """
    Resolves multipliers for ARRL DX based on the logger's location, prioritizing
    the received exchange over the callsign's prefix according to refined rules.
    """
    if df.empty:
        return df

    root_dir = os.environ.get('CONTEST_LOGS_REPORTS').strip().strip('"').strip("'")
    data_dir = os.path.join(root_dir, 'data')
    lookup = AliasLookup(data_dir, 'ARRLDXmults.dat')

    # Initialize new columns
    df['Mult_STPROV'] = pd.NA
    df['STPROV_MultName'] = pd.NA
    df['Mult_DXCC'] = pd.NA
    df['Mult_DXCCName'] = pd.NA
    df['STPROV_IsNewMult'] = 0
    df['DXCC_IsNewMult'] = 0
    
    seen_stprov_per_band = {band: set() for band in df['Band'].unique() if pd.notna(band)}
    seen_dxcc_per_band = {band: set() for band in df['Band'].unique() if pd.notna(band)}
    
    NON_CONTIGUOUS_STATES = {'AK', 'HI'}

    df_sorted = df.sort_values(by='Datetime')

    for idx, row in df_sorted.iterrows():
        band = row.get('Band')
        if not band: continue
             
        dxcc_id = str(row.get('DXCCPfx', ''))
        rcvd_location = row.get('RcvdLocation', '')
        
        # --- Apply rules based on LOGGER's location ---
        if my_location_type == 'DX':
            resolved_stprov = pd.NA
            resolved_stprov_name = pd.NA

            if dxcc_id in ['K', 'VE']:
                resolved_stprov, resolved_stprov_name = lookup.get_multiplier(rcvd_location)
            elif dxcc_id.startswith('K'):
                # Check if the received location is a valid US State/DC
                temp_abbr, _ = lookup.get_multiplier(rcvd_location)
                if pd.notna(temp_abbr):
                    category = lookup.get_category(temp_abbr)
                    if category and 'US States' in category:
                        resolved_stprov, resolved_stprov_name = temp_abbr, _
            
            if pd.notna(resolved_stprov) and resolved_stprov != "Unknown" and resolved_stprov not in NON_CONTIGUOUS_STATES:
                df.loc[idx, 'Mult_STPROV'] = resolved_stprov
                df.loc[idx, 'STPROV_MultName'] = resolved_stprov_name
                if resolved_stprov not in seen_stprov_per_band[band]:
                    df.loc[idx, 'STPROV_IsNewMult'] = 1
                    seen_stprov_per_band[band].add(resolved_stprov)
                    
                    # --- Temporary Diagnostic Logic ---
                    if band == '40M' and resolved_stprov in ['SD', 'NF', 'YT']:
                        logging.info("\n" + "="*60)
                        logging.info(f"--- DEBUG: 40M '{resolved_stprov}' Multiplier Source Row (resolver) ---")
                        logging.info(row.to_string())
                        logging.info("="*60 + "\n")
        
        elif my_location_type == 'W/VE':
            worked_dxcc_name = row.get('DXCCName', 'Unknown')
            is_dx_multiplier = worked_dxcc_name not in ["United States", "Canada"]

            if is_dx_multiplier:
                dxcc_mult = row.get('DXCCPfx')
                df.loc[idx, 'Mult_DXCC'] = dxcc_mult
                df.loc[idx, 'Mult_DXCCName'] = worked_dxcc_name
                if pd.notna(dxcc_mult) and dxcc_mult not in seen_dxcc_per_band[band]:
                    df.loc[idx, 'DXCC_IsNewMult'] = 1
                    seen_dxcc_per_band[band].add(dxcc_mult)
    
    return df