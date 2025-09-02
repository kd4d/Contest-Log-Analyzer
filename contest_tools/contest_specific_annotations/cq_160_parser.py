# Contest Log Analyzer/contest_tools/contest_specific_annotations/cq_160_parser.py
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-31
# Version: 0.56.20-Beta
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
# Purpose: This module provides a custom parser for the CQ 160-Meter Contest,
#          which has a complex exchange format that can include a state,
#          province, or "DX".
#
# --- Revision History ---
## [0.56.20-Beta] - 2025-08-31
### Fixed
# - Added the `RawQSO` field to the parser's output to ensure it provides
#   the necessary data for downstream diagnostic logging.
## [0.56.11-Beta] - 2025-08-31
### Fixed
# - Corrected a logic error where the parser used a generic key to look
#   up parsing rules. It now pre-scans the header to get the specific
#   contest ID (e.g., CQ-160-CW) and uses it to retrieve the correct rules.
## [0.55.11-Beta] - 2025-08-31
### Changed
# - Refactored to use the new, centralized `parse_qso_common_fields`
#   helper from the main cabrillo_parser, eliminating duplicated logic.
## [0.35.15-Beta] - 2025-08-15
### Fixed
# - Corrected the regex for state/province exchanges to properly handle
#   two-letter abbreviations, which also resolved an issue with the
#   NAQP multiplier resolver.
## [0.35.14-Beta] - 2025-08-15
### Fixed
# - Corrected a logic error where the parser would fail if a log
#   contained only DX QSOs by ensuring the loop continued after a
#   failed match on the state/province-specific regex.
## [0.35.13-Beta] - 2025-08-14
### Added
# - Added a second regex to the parser to correctly handle DX stations
#   that send "DX" as their exchange, a format the original regex
#   could not parse.
## [0.35.12-Beta] - 2025-08-14
### Added
# - Added a custom parser for the CQ 160-Meter Contest to handle its
#   unique exchange format, which can be either a state/province or "DX".
import pandas as pd
import re
from typing import Dict, Any, List, Tuple
import os
import logging

from ..contest_definitions import ContestDefinition
from ..cabrillo_parser import parse_qso_common_fields

def parse_log(filepath: str, contest_definition: ContestDefinition) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Custom parser for the CQ 160-Meter Contest.
    """
    log_metadata: Dict[str, Any] = {}
    qso_records: List[Dict[str, Any]] = []

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        raise ValueError(f"Error reading Cabrillo file {filepath}: {e}")

    # --- Pre-scan header to determine the specific contest ID (e.g., CQ-160-CW) ---
    contest_id_from_header = ''
    for line in lines[:30]: # Check first 30 lines for the header
        if line.upper().startswith('CONTEST:'):
            contest_id_from_header = line.split(':', 1)[1].strip()
            log_metadata['ContestName'] = contest_id_from_header
            break
    
    if not contest_id_from_header:
        raise ValueError("CONTEST: tag not found in Cabrillo header.")

    rules_for_contest = contest_definition.exchange_parsing_rules.get(contest_id_from_header, [])
    if not isinstance(rules_for_contest, list):
        rules_for_contest = [rules_for_contest]

    for line in lines:
        cleaned_line = line.replace('\u00a0', ' ').strip()
        line_to_process = cleaned_line.upper() if cleaned_line.upper().startswith('QSO:') else cleaned_line
        
        if not line_to_process:
            continue
        elif line_to_process.startswith('END-OF-LOG:'):
            break
        elif line_to_process.startswith('QSO:'):
            common_data = parse_qso_common_fields(line_to_process)
            if not common_data:
                continue

            exchange_rest = common_data.pop('ExchangeRest', '').strip()
            
            for rule_info in rules_for_contest:
                exchange_match = re.match(rule_info['regex'], exchange_rest)
                if exchange_match:
                    exchange_data = dict(zip(rule_info['groups'], exchange_match.groups()))
                    common_data.update(exchange_data)
                    common_data['RawQSO'] = line_to_process
                    qso_records.append(common_data)
                    break
        
        elif not line_to_process.startswith('START-OF-LOG:'):
            for cabrillo_tag, df_key in contest_definition.header_field_map.items():
                if line_to_process.startswith(f"{cabrillo_tag}:"):
                    value = line_to_process[len(f"{cabrillo_tag}:"):].strip()
                    log_metadata[df_key] = value
                    break

    if not qso_records:
        raise ValueError(f"No valid QSO lines found in Cabrillo file: {filepath}")
    
    df = pd.DataFrame(qso_records)
    return df, log_metadata