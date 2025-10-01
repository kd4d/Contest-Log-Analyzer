# Contest Log Analyzer/contest_tools/contest_specific_annotations/arrl_fd_parser.py
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-10-01
# Version: 0.90.0-Beta
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
# Purpose: This module provides a custom parser for the ARRL Field Day
#          contest, which has a unique exchange format and uses both HF
#          frequencies and VHF+ band designators.
#
# --- Revision History ---
## [0.90.0-Beta] - 2025-10-01
### Fixed
# - Updated the parse_log function signature to the standard four-argument
#   contract to resolve a TypeError during invocation.
## [0.70.17-Beta] - 2025-09-10
### Changed
# - Updated `parse_log` signature to accept `root_input_dir` to align
#   with the standardized parser contract, fixing a TypeError.
## [0.56.20-Beta] - 2025-08-31
### Fixed
# - Added the `RawQSO` field to the parser's output to ensure it provides
#   the necessary data for downstream diagnostic logging.
## [0.55.11-Beta] - 2025-08-31
### Changed
# - Refactored to use the new, centralized `parse_qso_common_fields`
#   helper from the main cabrillo_parser, eliminating duplicated logic.
## [0.39.8-Beta] - 2025-08-18
### Fixed
# - Fixed a bug that caused the parser to fail on `SAT` (satellite)
#   QSOs by ensuring the band designator regex correctly handled
#   alphabetic-only strings.
## [0.39.7-Beta] - 2025-08-18
### Fixed
# - Corrected a logic error where the parser would fail if a log
#   contained only VHF QSOs by ensuring the loop continued after a
#   failed match on the HF-specific regex.
## [0.39.6-Beta] - 2025-08-18
### Fixed
# - Added a `continue` statement to the main parsing loop to correctly
#   skip lines that do not match any known QSO format, preventing a
#   crash when encountering malformed lines.
## [0.39.5-Beta] - 2025-08-18
### Added
# - Added detailed INFO-level logging to the `parse_log` function to
#   provide better diagnostic feedback during execution.
## [0.39.4-Beta] - 2025-08-18
# - Initial release of the ARRL Field Day custom parser.
import pandas as pd
import re
from typing import Dict, Any, List, Tuple
import os
import logging

from ..contest_definitions import ContestDefinition
from ..cabrillo_parser import parse_qso_common_fields

def parse_log(filepath: str, contest_definition: ContestDefinition, root_input_dir: str, cty_dat_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Custom parser for the ARRL Field Day contest.
    """
    log_metadata: Dict[str, Any] = {}
    qso_records: List[Dict[str, Any]] = []

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        raise ValueError(f"Error reading Cabrillo file {filepath}: {e}")

    rule_info = contest_definition.exchange_parsing_rules.get("ARRL-FD", {})
    exchange_regex = re.compile(rule_info.get('regex', ''))
    exchange_groups = rule_info.get('groups', [])

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
            
            exchange_match = exchange_regex.match(exchange_rest)
            if exchange_match:
                exchange_data = dict(zip(exchange_groups, exchange_match.groups()))
                common_data.update(exchange_data)
                common_data['RawQSO'] = line_to_process
                qso_records.append(common_data)
            else:
                logging.warning(f"Skipping ARRL-FD QSO line (unrecognized exchange): {line_to_process}")
        
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