# Contest Log Analyzer/contest_tools/contest_specific_annotations/arrl_10_parser.py
#
# Version: 0.32.0-Beta
# Date: 2025-08-12
#
# Purpose: Provides a custom, contest-specific parser for the ARRL 10 Meter
#          contest to handle its asymmetric sent exchange format.
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
# - Initial release of the custom parser for the ARRL 10 Meter contest.

import pandas as pd
import re
import logging
import os
from typing import Dict, Any, List, Tuple, Optional

from ..contest_definitions import ContestDefinition
from ..core_annotations import CtyLookup

def _get_logger_location(filepath: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Performs a pre-scan of the Cabrillo header to find the callsign and determine location.
    """
    callsign = None
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip().upper()
                if line.startswith('CALLSIGN:'):
                    callsign = line.split(':', 1)[1].strip()
                    break
                if line.startswith('QSO:'): # Stop if we exit the header
                    break
    except Exception:
        return None, None

    if not callsign:
        return None, None

    root_dir = os.environ.get('CONTEST_LOGS_REPORTS').strip().strip('"').strip("'")
    data_dir = os.path.join(root_dir, 'data')
    cty_dat_path = os.path.join(data_dir, 'cty.dat')
    cty_lookup = CtyLookup(cty_dat_path=cty_dat_path)
    info = cty_lookup.get_cty(callsign)
    
    location_type = "W/VE" if info.name in ["United States", "Canada"] else "DX"
    return location_type, callsign

def parse_log(filepath: str, contest_definition: ContestDefinition) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Custom parser for the ARRL 10 Meter contest.
    """
    log_metadata: Dict[str, Any] = {}
    qso_records: List[Dict[str, Any]] = []
    
    # --- Step 1: Determine logger's location to select the correct primary regex ---
    logger_location, logger_callsign = _get_logger_location(filepath)
    if not logger_location:
        raise ValueError(f"Could not determine logger location from CALLSIGN: in header of {filepath}")

    if logger_location == "W/VE":
        rule_key = "ARRL-10-WVE-LOGGER"
    else:
        rule_key = "ARRL-10-DX-LOGGER"
    
    parsing_rule = contest_definition.exchange_parsing_rules.get(rule_key)
    if not parsing_rule:
        raise ValueError(f"Parsing rule '{rule_key}' not found in JSON definition.")
        
    qso_regex = re.compile(parsing_rule['regex'])
    qso_groups = parsing_rule['groups']
    
    common_fields_regex = re.compile(contest_definition.qso_common_fields_regex)

    # --- Step 2: Parse the file line-by-line ---
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        raise IOError(f"Error reading Cabrillo file {filepath}: {e}")

    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue
            
        # Handle header lines
        if cleaned_line.upper().startswith('QSO:'):
            # First, match the generic common fields to get metadata
            common_match = common_fields_regex.match(cleaned_line)
            if not common_match:
                logging.warning(f"Skipping malformed QSO line: {cleaned_line}")
                continue
            
            common_data = dict(zip(contest_definition.qso_common_field_names, common_match.groups()))
            
            # Now, use the contest-specific regex on the full exchange part
            full_exchange = f"{common_data.get('MyCallRaw','')} {common_data.get('ExchangeRest','')}".strip()
            
            qso_match = qso_regex.match(full_exchange)
            if qso_match:
                qso_data = dict(zip(qso_groups, qso_match.groups()))
                qso_data.update(common_data) # Add common fields like DateRaw, TimeRaw
                qso_records.append(qso_data)
            else:
                logging.warning(f"Skipping QSO line that did not match '{rule_key}' rule: {cleaned_line}")
        
        # Parse header fields
        else:
            for cabrillo_tag, df_key in contest_definition.header_field_map.items():
                if cleaned_line.upper().startswith(f"{cabrillo_tag}:"):
                    value = cleaned_line[len(f"{cabrillo_tag}:"):].strip()
                    log_metadata[df_key] = value
                    break

    if not qso_records:
        raise ValueError(f"No valid QSO lines found in Cabrillo file: {filepath}")

    df = pd.DataFrame(qso_records)
    return df, log_metadata