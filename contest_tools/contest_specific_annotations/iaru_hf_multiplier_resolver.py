# contest_tools/contest_specific_annotations/iaru_hf_multiplier_resolver.py
#
# Purpose: Provides a custom, contest-specific multiplier resolver for the
#          IARU HF World Championship contest. It parses the received exchange
#          to identify and categorize the three distinct multiplier types:
#          ITU Zones, IARU HQ Stations, and IARU Officials.
#
# Copyright (c) 2025 Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pandas as pd
import os
import re
import logging
from typing import Dict, Any, Set, Tuple, Optional

from ..contest_definitions import ContestDefinition
from ..core_annotations._iaru_mult_utils import load_officials_set, resolve_iaru_hq_official
from ..core_annotations._core_utils import normalize_zone

def _resolve_row(row: pd.Series, officials_set: Set[str]) -> Dict[str, Optional[str]]:
    """
    Parses the received exchange for a single QSO and returns the categorized
    multiplier value.
    """
    mult_zone, mult_hq, mult_official = None, None, None
    
    # Get the clean multiplier value from the 'RcvdMult' column provided by the parser.
    exchange = row.get('RcvdMult')
    
    if pd.notna(exchange):
        exchange = str(exchange).strip()
        
        # 1. Check if it's a numeric ITU Zone (IARU-HF specific)
        if exchange.isnumeric():
            mult_zone = exchange
        else:
            # 2. Use shared utility for HQ/Official parsing
            hq_official = resolve_iaru_hq_official(exchange, officials_set)
            mult_hq = hq_official['hq']
            mult_official = hq_official['official']

    return {'zone': mult_zone, 'hq': mult_hq, 'official': mult_official}

def resolve_multipliers(df: pd.DataFrame, my_location_type: str, root_input_dir: str, contest_def: ContestDefinition) -> pd.DataFrame:
    """
    Resolves multipliers for the IARU HF World Championship by parsing the
    RcvdMult column and populating the three distinct multiplier columns.
    """
    # This map provides a robust link between the rule name in the JSON
    # and the key returned by the _resolve_row helper function.
    RULE_TO_KEY_MAP = {
        'Zones': 'zone',
        'HQ Stations': 'hq',
        'IARU Officials': 'official'
    }

    if df.empty or 'RcvdMult' not in df.columns:
        # Ensure columns defined in the blueprint exist even if there's nothing to process
        for rule in contest_def.multiplier_rules:
            col = rule.get('value_column')
            if col and col not in df.columns:
                df[col] = pd.NA
        return df

    officials_set = load_officials_set(root_input_dir)
    
    # Get the categorized multiplier data for all rows in a single pass.
    categorized_mults = df.apply(_resolve_row, axis=1, officials_set=officials_set)

    # Iterate through the rules from the JSON blueprint to assign data to the correct columns.
    for rule in contest_def.multiplier_rules:
        target_column = rule.get('value_column')
        data_key = RULE_TO_KEY_MAP.get(rule.get('name'))
        if target_column and data_key:
            zone_values = categorized_mults.apply(lambda x: x.get(data_key))
            
            # Normalize zone values to two-digit format (IARU HF uses ITU Zones: 1-90)
            if data_key == 'zone':
                df[target_column] = zone_values.apply(lambda x: normalize_zone(x, zone_type='itu'))
            else:
                df[target_column] = zone_values
    
    return df
