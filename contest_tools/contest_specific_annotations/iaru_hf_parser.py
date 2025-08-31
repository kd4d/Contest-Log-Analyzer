# Contest Log Analyzer/contest_tools/contest_specific_annotations/iaru_hf_parser.py
#
# Author: Gemini AI
# Date: 2025-08-30
# Version: 0.55.6-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Purpose: Provides a custom, contest-specific parser for the IARU HF World
#          Championship contest to handle its asymmetric exchange format, which
#          differs based on whether the logger is an HQ or a Zone station.
#
# --- Revision History ---
## [0.55.6-Beta] - 2025-08-30
### Changed
# - Added the standard copyright and MPL 2.0 license block to the header
#   to conform to project standards.

import pandas as pd
import re
import logging
import os
from typing import Dict, Any, List, Tuple, Optional

from ..contest_definitions import ContestDefinition

def _get_logger_type(filepath: str) -> str:
    """
    Performs a pre-scan of the Cabrillo header to determine if the logging
    station is an HQ station or a regular (Zone) station.
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            # Limit the pre-scan to the first 30 lines for efficiency
            for i, line in enumerate(f):
                if i > 30: break
                line = line.strip().upper()
                if line.startswith('CATEGORY-STATION:'):
                    if line.split(':', 1)[1].strip() == 'HQ':
                        logging.info("Logger identified as HQ station.")
                        return "HQ"
    except Exception as e:
        logging.warning(f"Could not pre-scan log header to determine logger type: {e}")
    
    logging.info("Logger identified as ZONE station (default).")
    return "ZONE"

def parse_log(filepath: str, contest_definition: ContestDefinition) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Custom parser for the IARU HF World Championship contest.
    """
    log_metadata: Dict[str, Any] = {}
    qso_records: List[Dict[str, Any]] = []
    
    # --- Step 1: Determine logger's type to select the correct primary regex ---
    logger_type = _get_logger_type(filepath)

    if logger_type == "ZONE":
        rule_key = "IARU-HF-ZONE-LOGGER"
    else:
        rule_key = "IARU-HF-HQ-LOGGER"
    
    parsing_rule = contest_definition.exchange_parsing_rules.get(rule_key)
    if not parsing_rule:
        raise ValueError(f"Parsing rule '{rule_key}' not found in JSON definition.")
        
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

        line_to_process = sanitized_line.upper() if sanitized_line.upper().startswith('QSO:') else sanitized_line
            
        if line_to_process.startswith('QSO:'):
            common_match = common_fields_regex.match(line_to_process)
            if not common_match:
                logging.warning(f"Skipping malformed QSO line: {line_to_process}")
                continue
            
            common_data = dict(zip(contest_definition.qso_common_field_names, common_match.groups()))
            exchange_rest = common_data.get('ExchangeRest','').strip()
            
            qso_match = qso_regex.match(exchange_rest)
            if qso_match:
                qso_data = dict(zip(qso_groups, qso_match.groups()))
                qso_data.update(common_data)
                qso_data['RawQSO'] = line_to_process
                qso_records.append(qso_data)
            else:
                logging.warning(f"Skipping QSO line that did not match '{rule_key}' rule: {line_to_process}")
        
        elif not line_to_process.startswith(('START-OF-LOG', 'END-OF-LOG')):
            for cabrillo_tag, df_key in contest_definition.header_field_map.items():
                if line_to_process.upper().startswith(f"{cabrillo_tag}:"):
                    value = line_to_process[len(f"{cabrillo_tag}:"):].strip()
                    log_metadata[df_key] = value
                    break

    if not qso_records:
        raise ValueError(f"Custom parser found no valid QSO lines in Cabrillo file: {filepath}")

    df = pd.DataFrame(qso_records)
    return df, log_metadata