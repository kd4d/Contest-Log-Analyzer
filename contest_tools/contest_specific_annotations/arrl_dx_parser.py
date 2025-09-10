# Contest Log Analyzer/contest_tools/contest_specific_annotations/arrl_dx_parser.py
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-09-10
# Version: 0.70.16-Beta
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
# Purpose: This module provides a custom parser for the ARRL DX Contest, which
#          has a highly asymmetric exchange format.
#
# --- Revision History ---
## [0.70.16-Beta] - 2025-09-10
### Changed
# - Updated `parse_log` signature to accept `root_input_dir` to align
#   with the standardized parser contract, fixing a TypeError.
## [0.62.3-Beta] - 2025-09-08
### Changed
# - Updated script to read the new CONTEST_INPUT_DIR environment variable.
## [0.56.24-Beta] - 2025-08-31
### Fixed
# - Corrected a typo in a variable name (`logger` to `logger_call`) that
#   was causing a `NameError` during the header pre-scan.
## [0.56.18-Beta] - 2025-08-31
### Fixed
# - Added the `RawQSO` field to the parser's output to ensure it provides
#   the necessary data for downstream diagnostic logging.
## [0.56.13-Beta] - 2025-08-31
### Fixed
# - Corrected a logic error where the parser used an incomplete key to
#   look up parsing rules. It now pre-scans for the full contest ID
#   and combines it with the logger's location to get the correct rules.
## [0.55.11-Beta] - 2025-08-31
### Changed
# - Refactored to use the new, centralized `parse_qso_common_fields`
#   helper from the main cabrillo_parser, eliminating duplicated logic.
## [0.32.9-Beta] - 2025-08-12
### Changed
# - Refined the DX station regex to correctly handle callsigns with
#   forward slashes, preventing parsing errors.
## [0.32.8-Beta] - 2025-08-12
### Changed
# - Updated regexes to correctly handle single-digit reports (e.g., "59")
#   in SSB logs, in addition to three-digit RSTs.
## [0.32.7-Beta] - 2025-08-12
### Added
# - Added a regex rule for DX stations to correctly parse state/province
#   abbreviations from W/VE stations.
## [0.32.6-Beta] - 2025-08-12
### Added
# - Added a regex rule for W/VE stations to correctly parse power output
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
from ..core_annotations import CtyLookup

def parse_log(filepath: str, contest_definition: ContestDefinition, root_input_dir: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Custom parser for the ARRL DX Contest (CW and SSB).
    """
    log_metadata: Dict[str, Any] = {}
    qso_records: List[Dict[str, Any]] = []
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    # --- Pre-scan header to determine logger's location and contest ID ---
    logger_call = ''
    contest_id_from_header = ''
    for line in lines[:30]:
        line_upper = line.upper()
        if line_upper.startswith('CALLSIGN:'):
            logger_call = line.split(':', 1)[1].strip()
        elif line_upper.startswith('CONTEST:'):
            contest_id_from_header = line.split(':', 1)[1].strip()
        
        if logger_call and contest_id_from_header:
            break

    if not logger_call:
        raise ValueError("CALLSIGN: tag not found in Cabrillo header.")
    if not contest_id_from_header:
        raise ValueError("CONTEST: tag not found in Cabrillo header.")
        
    root_dir = root_input_dir.strip().strip('"').strip("'")
    data_dir = os.path.join(root_dir, 'data')
    cty_dat_path = os.path.join(data_dir, 'cty.dat')
    cty_lookup = CtyLookup(cty_dat_path=cty_dat_path)
    info = cty_lookup.get_cty_DXCC_WAE(logger_call)._asdict()
    logger_location_type = "W/VE" if info['DXCCName'] in ["United States", "Canada"] else "DX"
    logging.info(f"ARRL DX parser: Logger location type determined as '{logger_location_type}'")
    
    # Select the appropriate rule based on the contest and logger's location
    rule_set_key = f"{contest_id_from_header}-{logger_location_type}"
    rule_info = contest_definition.exchange_parsing_rules.get(rule_set_key)
    if not rule_info:
        raise ValueError(f"Parsing rule '{rule_set_key}' not found in JSON definition.")
        
    exchange_regex = re.compile(rule_info['regex'])
    exchange_groups = rule_info['groups']

    for line in lines:
        cleaned_line = line.replace('\u00a0', ' ').strip()
        line_to_process = cleaned_line.upper() if cleaned_line.upper().startswith('QSO:') else cleaned_line

        if not line_to_process or line_to_process.startswith(('END-OF-LOG:', 'START-OF-LOG:')):
            continue
            
        if line_to_process.startswith('QSO:'):
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
        
        else: # It's a header line
            for cabrillo_tag, df_key in contest_definition.header_field_map.items():
                if line_to_process.startswith(f"{cabrillo_tag}:"):
                    value = line_to_process[len(f"{cabrillo_tag}:"):].strip()
                    log_metadata[df_key] = value
                    break

    if not qso_records:
        raise ValueError(f"No valid QSO lines found in Cabrillo file: {filepath}")
        
    df = pd.DataFrame(qso_records)
    return df, log_metadata