# Contest Log Analyzer/contest_tools/contest_specific_annotations/arrl_10_multiplier_resolver.py
#
# Version: 0.32.0-Beta
# Date: 2025-08-12
#
# Purpose: Provides contest-specific logic to resolve ARRL 10 Meter contest
#          multipliers by parsing the asymmetric received exchange.
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
## [0.32.0-Beta] - 2025-08-12
### Added
# - Initial release of the custom multiplier resolver for the ARRL 10 Meter contest.

import pandas as pd
import os
import re
import logging
from typing import Dict, Any, Tuple

from ..core_annotations._core_utils import AliasLookup
from ..contest_definitions import ContestDefinition

def _resolve_row(row: pd.Series, alias_lookup: AliasLookup, rules: Dict) -> pd.Series:
    """
    Parses the received exchange and determines the multiplier for a single QSO row.
    """
    # Initialize results
    mult_state, mult_ve, mult_xe, mult_dxcc, mult_itu = pd.NA, pd.NA, pd.NA, pd.NA, pd.NA
    rcvd_location, rcvd_serial, rcvd_itu = pd.NA, pd.NA, pd.NA
    
    worked_call = row.get('Call', '')
    worked_dxcc = row.get('DXCCName', 'Unknown')
    rcvd_exchange_full = str(row.get('RcvdExchangeFull', '')).strip()

    # --- Step 1: Determine which parsing rule to use based on station type ---
    rule_key = None
    if worked_call.endswith('/MM'):
        rule_key = "ARRL-10-RCVD-MM"
    elif worked_dxcc in ["United States", "Canada", "Mexico", "Alaska", "Hawaii"]:
        rule_key = "ARRL-10-RCVD-WVE"
    else:
        rule_key = "ARRL-10-RCVD-DX"

    # --- Step 2: Parse the raw exchange string with the selected rule ---
    rule = rules.get(rule_key)
    if rule:
        match = re.match(rule['regex'], rcvd_exchange_full)
        if match:
            parsed_data = dict(zip(rule['groups'], match.groups()))
            rcvd_location = parsed_data.get('RcvdLocation')
            rcvd_serial = parsed_data.get('RcvdSerial')
            rcvd_itu = parsed_data.get('RcvdITU')

    # --- Step 3: Populate the final multiplier columns ---
    if pd.notna(rcvd_itu):
        mult_itu = f"ITU {rcvd_itu}"
    elif pd.notna(rcvd_location):
        mult_abbr, mult_full_name = alias_lookup.get_multiplier(rcvd_location)
        if pd.notna(mult_abbr):
            # Categorize based on the full name from the alias file
            if any(k in mult_full_name.upper() for k in ['ALABAMA', 'ALASKA', 'ARIZONA', 'ARKANSAS', 'CALIFORNIA', 'COLORADO', 'CONNECTICUT', 'DISTRICT OF COLUMBIA', 'DELAWARE', 'FLORIDA', 'GEORGIA', 'HAWAII', 'IDAHO', 'ILLINOIS', 'INDIANA', 'IOWA', 'KANSAS', 'KENTUCKY', 'LOUISIANA', 'MAINE', 'MARYLAND', 'MASSACHUSETTS', 'MICHIGAN', 'MINNESOTA', 'MISSISSIPPI', 'MISSOURI', 'MONTANA', 'NEBRASKA', 'NEVADA', 'NEW HAMPSHIRE', 'NEW JERSEY', 'NEW MEXICO', 'NEW YORK', 'NORTH CAROLINA', 'NORTH DAKOTA', 'OHIO', 'OKLAHOMA', 'OREGON', 'PENNSYLVANIA', 'RHODE ISLAND', 'SOUTH CAROLINA', 'SOUTH DAKOTA', 'TENNESSEE', 'TEXAS', 'UTAH', 'VERMONT', 'VIRGINIA', 'WASHINGTON', 'WEST VIRGINIA', 'WISCONSIN', 'WYOMING']):
                mult_state = mult_abbr
            elif any(k in mult_full_name.upper() for k in ['ALBERTA', 'BRITISH COLUMBIA', 'LABRADOR', 'MANITOBA', 'NEW BRUNSWICK', 'NEWFOUNDLAND', 'NOVA SCOTIA', 'NORTHWEST TERRITORIES', 'NUNAVUT', 'ONTARIO', 'PRINCE EDWARD ISLAND', 'QUEBEC', 'SASKATCHEWAN', 'YUKON']):
                mult_ve = mult_abbr
            else: # Must be a Mexican State
                mult_xe = mult_abbr
    else: # Fallback to DXCC
        if worked_dxcc != 'Unknown':
            mult_dxcc = worked_dxcc

    return pd.Series([rcvd_location, rcvd_serial, rcvd_itu, mult_state, mult_ve, mult_xe, mult_dxcc, mult_itu])


def resolve_multipliers(df: pd.DataFrame, my_call_info: Dict[str, Any]) -> pd.DataFrame:
    """
    Resolves multipliers for the ARRL 10 Meter contest.
    """
    if df.empty:
        return df

    # Initialize alias lookup
    root_dir = os.environ.get('CONTEST_LOGS_REPORTS', '').strip().strip('"').strip("'")
    data_dir = os.path.join(root_dir, 'data')
    alias_lookup = AliasLookup(data_dir, 'arrl_10_mults.dat')

    # Load exchange parsing rules from the contest definition
    contest_def = ContestDefinition.from_json("ARRL-10")
    rules = contest_def.exchange_parsing_rules

    # --- Step 1: Parse exchange and determine multiplier category for every QSO ---
    parsed_cols = ['RcvdLocation', 'RcvdSerial', 'RcvdITU']
    mult_cols = ['Mult_State', 'Mult_VE', 'Mult_XE', 'Mult_DXCC', 'Mult_ITU']
    
    df[parsed_cols + mult_cols] = df.apply(_resolve_row, axis=1, alias_lookup=alias_lookup, rules=rules)

    # --- Step 2: Apply "once per mode" logic ---
    df_sorted = df.sort_values(by='Datetime')
    
    worked_cw = set()
    worked_ph = set()

    for col in mult_cols:
        # Process CW QSOs
        cw_mask = (df_sorted['Mode'] == 'CW') & (df_sorted[col].notna())
        for idx, row in df_sorted[cw_mask].iterrows():
            mult_tuple = (col, row[col])
            if mult_tuple in worked_cw:
                df.loc[idx, col] = pd.NA  # Invalidate subsequent contacts
            else:
                worked_cw.add(mult_tuple)

        # Process Phone QSOs
        ph_mask = ((df_sorted['Mode'] == 'PH') | (df_sorted['Mode'] == 'SSB')) & (df_sorted[col].notna())
        for idx, row in df_sorted[ph_mask].iterrows():
            mult_tuple = (col, row[col])
            if mult_tuple in worked_ph:
                df.loc[idx, col] = pd.NA  # Invalidate subsequent contacts
            else:
                worked_ph.add(mult_tuple)
                
    return df