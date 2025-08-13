# Contest Log Analyzer/contest_tools/contest_specific_annotations/arrl_10_parser.py
#
# Version: 0.32.7-Beta
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
## [0.32.7-Beta] - 2025-08-12
### Fixed
# - Added robust data sanitization to handle non-breaking spaces and to
#   convert QSO lines to uppercase before parsing to prevent regex failures.
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
            # Limit the pre-scan to the first 20 lines for efficiency
            for i, line in enumerate(f):
                if i > 20 and not callsign: break
                line = line.strip().upper()
                if line.startswith('CALLSIGN:'):
                    callsign = line.split(':', 1)[1].strip()
                    break
    except Exception:
        return None, None

    if not callsign:
        return None, None

    # This requires the environment variable to be set to find the data files
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
    
    # Use the common regex to split the line into pre-exchange and exchange parts
    common_fields_regex = re.compile(contest_definition.qso_common_fields_regex)

    # --- Step 2: Parse the file line-by-line ---
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    for line in lines:
        # Sanitize the line to handle non-breaking spaces
        sanitized_line = line.replace('\u00a0', ' ').strip()
        if not sanitized_line:
            continue

        # Conditionally convert QSO lines to uppercase for robust regex matching
        temp_upper_line = sanitized_line.upper()
        line_to_process = sanitized_line
        if temp_upper_line.startswith('QSO:'):
            line_to_process = temp_upper_line
            
        if line_to_process.startswith('QSO:'):
            # First, match generic fields to get date, time, mode, etc.
            common_match = common_fields_regex.match(line_to_process)
            if not common_match:
                logging.warning(f"Skipping malformed QSO line: {line_to_process}")
                continue
            
            common_data = dict(zip(contest_definition.qso_common_field_names, common_match.groups()))
            
            # Now, use the selected contest-specific regex on the full exchange part
            exchange_rest = common_data.get('ExchangeRest','').strip()
            
            qso_match = qso_regex.match(exchange_rest)
            if qso_match:
                qso_data = dict(zip(qso_groups, qso_match.groups()))
                qso_data.update(common_data)
                qso_records.append(qso_data)
            else:
                logging.warning(f"Skipping QSO line that did not match '{rule_key}' rule: {line_to_process}")
        
        # Parse header fields
        elif not line_to_process.startswith('START-OF-LOG') and not line_to_process.startswith('END-OF-LOG'):
            for cabrillo_tag, df_key in contest_definition.header_field_map.items():
                if line_to_process.upper().startswith(f"{cabrillo_tag}:"):
                    value = line_to_process[len(f"{cabrillo_tag}:"):].strip()
                    log_metadata[df_key] = value
                    break

    if not qso_records:
        raise ValueError(f"Custom parser found no valid QSO lines in Cabrillo file: {filepath}")

    df = pd.DataFrame(qso_records)
    return df, log_metadata