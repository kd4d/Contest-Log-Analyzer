# Contest Log Analyzer/contest_tools/contest_specific_annotations/naqp_parser.py
#
# Version: 0.35.8-Beta
# Date: 2025-08-13
#
# Purpose: Provides a custom, contest-specific parser for the NAQP contest
#          to handle its specific exchange format.
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
## [0.35.8-Beta] - 2025-08-13
### Added
# - Initial release of the custom parser for the NAQP contest to restore
#   correct parsing functionality.

import pandas as pd
import re
import logging
from typing import Dict, Any, List, Tuple

from ..contest_definitions import ContestDefinition

def parse_log(filepath: str, contest_definition: ContestDefinition) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Custom parser for the NAQP contest.
    """
    log_metadata: Dict[str, Any] = {}
    qso_records: List[Dict[str, Any]] = []
    
    # --- Step 1: Get the parsing rule for the specific contest mode ---
    contest_name_from_log = ""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                if i > 30: break # Limit scan to header
                line = line.strip().upper()
                if line.startswith('CONTEST:'):
                    contest_name_from_log = line.split(':', 1)[1].strip()
                    break
    except Exception:
        pass

    if not contest_name_from_log:
        raise ValueError(f"Could not find CONTEST: tag in header of {filepath}")

    parsing_rule = contest_definition.exchange_parsing_rules.get(contest_name_from_log)
    if not parsing_rule:
        raise ValueError(f"Parsing rule for '{contest_name_from_log}' not found in JSON definition.")
        
    qso_regex = re.compile(parsing_rule['regex'])
    qso_groups = parsing_rule['groups']
    common_fields_regex = re.compile(contest_definition.qso_common_fields_regex)

    # --- Step 2: Parse the file line-by-line ---
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    for line in lines:
        sanitized_line = line.replace('\u00a0', ' ').strip()
        if not sanitized_line:
            continue

        line_to_process = sanitized_line
        if sanitized_line.upper().startswith('QSO:'):
            line_to_process = sanitized_line.upper()
            
        if line_to_process.startswith('QSO:'):
            common_match = common_fields_regex.match(line_to_process)
            if not common_match:
                logging.warning(f"Skipping malformed QSO line: {line_to_process}")
                continue
            
            common_data = dict(zip(contest_definition.qso_common_field_names, common_match.groups()))
            exchange_rest = common_data.get('ExchangeRest','').strip()
            
            # For NAQP, the sent exchange is part of the "rest"
            full_exchange_string = f"{common_data.get('MyCallRaw','')} {exchange_rest}"
            
            qso_match = qso_regex.match(full_exchange_string)
            if qso_match:
                qso_data = dict(zip(qso_groups, qso_match.groups()))
                qso_data.update(common_data)
                qso_records.append(qso_data)
            else:
                logging.warning(f"Skipping QSO line that did not match '{contest_name_from_log}' rule: {line_to_process}")
        
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