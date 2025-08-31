# Contest Log Analyzer/contest_tools/contest_specific_annotations/arrl_10_parser.py
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-31
# Version: 0.55.11-Beta
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
# Purpose: This module provides a custom parser for the ARRL 10-Meter Contest.
#
# --- Revision History ---
## [0.55.11-Beta] - 2025-08-31
### Changed
# - Refactored to use the new, centralized `parse_qso_common_fields`
#   helper from the main cabrillo_parser, eliminating duplicated logic.
## [0.32.7-Beta] - 2025-08-12
### Changed
# - Updated regex to correctly handle single-digit serial numbers in the
#   received exchange, fixing a parsing failure.
## [0.32.6-Beta] - 2025-08-12
### Added
# - Added a regex rule for DX stations to correctly parse state/province
#   abbreviations and serial numbers from W/VE stations.
## [0.32.5-Beta] - 2025-08-12
### Added
# - Added a regex rule for W/VE stations to correctly parse serial numbers
#   from DX stations.
## [0.32.0-Beta] - 2025-08-12
# - Initial release of Version 0.32.0-Beta.

import pandas as pd
import re
from typing import Dict, Any, List, Tuple
import os
import logging

from ..contest_definitions import ContestDefinition
from ..cabrillo_parser import parse_qso_common_fields

def parse_log(filepath: str, contest_definition: ContestDefinition) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Custom parser for the ARRL 10-Meter Contest.
    """
    log_metadata: Dict[str, Any] = {}
    qso_records: List[Dict[str, Any]] = []

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        raise ValueError(f"Error reading Cabrillo file {filepath}: {e}")

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
            
            rules_for_contest = contest_definition.exchange_parsing_rules.get("ARRL-10", [])
            if not isinstance(rules_for_contest, list):
                rules_for_contest = [rules_for_contest]

            for rule_info in rules_for_contest:
                exchange_match = re.match(rule_info['regex'], exchange_rest)
                if exchange_match:
                    exchange_data = dict(zip(rule_info['groups'], exchange_match.groups()))
                    common_data.update(exchange_data)
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