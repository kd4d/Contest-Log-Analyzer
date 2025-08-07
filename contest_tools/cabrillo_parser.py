# Contest Log Analyzer/contest_tools/cabrillo_parser.py
#
# Purpose: Provides functionality to parse Cabrillo log files into a Pandas DataFrame
#          and extract log metadata. It uses a ContestDefinition object to guide
#          the parsing of contest-specific header fields and QSO exchange formats.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-07
# Version: 0.30.57-Beta
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
## [0.30.57-Beta] - 2025-08-07
### Changed
# - Modified the parser to only warn once for each unique unrecognized
#   header tag per file.
## [0.30.33-Beta] - 2025-08-07
### Added
# - Added a diagnostic warning to log any unrecognized header lines.
## [0.30.32-Beta] - 2025-08-07
### Added
# - Added a diagnostic warning to log malformed QSO lines that fail to parse.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
# ---
import re
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
import os
import logging

# Import the ContestDefinition class from the definitions package
from .contest_definitions import ContestDefinition # Relative import within contest_tools


def parse_cabrillo_file(filepath: str, contest_definition: ContestDefinition) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Parses a Cabrillo log file into a Pandas DataFrame of QSOs and extracts header metadata.
    """
    log_metadata: Dict[str, Any] = {}
    qso_records: List[Dict[str, Any]] = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Cabrillo file not found: {filepath}")
    except Exception as e:
        raise ValueError(f"Error reading Cabrillo file {filepath}: {e}")

    in_header = True
    warned_tags = set()
    
    for i, line in enumerate(lines):
        line = line.strip()

        if not line:
            continue

        if line.startswith('START-OF-LOG:'):
            if i != 0:
                raise ValueError(f"Cabrillo format error: START-OF-LOG: must be the first line. (Line {i+1})")
            continue
        elif line.startswith('END-OF-LOG:'):
            break
        elif line.startswith('QSO:'):
            in_header = False
            qso_data = _parse_qso_line(line, contest_definition, log_metadata)
            if qso_data:
                qso_records.append(qso_data)
            continue 

        if in_header:
            parsed_header = False
            for cabrillo_tag, df_key in contest_definition.header_field_map.items():
                if line.startswith(f"{cabrillo_tag}:"):
                    value = line[len(f"{cabrillo_tag}:"):].strip()
                    log_metadata[df_key] = value
                    parsed_header = True
                    break
            
            if not parsed_header:
                tag = line.split(':', 1)[0]
                if tag not in warned_tags:
                    logging.warning(f"Unrecognized header tag found: {tag}")
                    warned_tags.add(tag)

    if not qso_records:
        raise ValueError(f"No valid QSO lines found in Cabrillo file: {filepath}")
    
    if 'MyCall' not in log_metadata or 'ContestName' not in log_metadata:
        raise ValueError(f"Required header fields (CALLSIGN:, CONTEST:) not found in {filepath}")
    
    df = pd.DataFrame(qso_records)

    return df, log_metadata

def _parse_qso_line(
    line: str,
    contest_definition: ContestDefinition,
    log_metadata: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Internal helper to parse a single QSO line from a Cabrillo log.
    """
    
    qso_final_dict = {col: pd.NA for col in contest_definition.default_qso_columns}

    common_match = re.match(contest_definition.qso_common_fields_regex, line)
    if not common_match:
        logging.warning(f"Malformed QSO line found (common fields regex failed): {line}")
        return None 

    qso_dict_common_parsed = dict(zip(contest_definition.qso_common_field_names, common_match.groups()))
    
    for key, val in qso_dict_common_parsed.items():
        qso_final_dict[key] = val.strip() if isinstance(val, str) else val

    exchange_rest = qso_final_dict.pop('ExchangeRest', '').strip()

    contest_name = log_metadata.get('ContestName')
    rules_for_contest = contest_definition.exchange_parsing_rules.get(contest_name)
    
    if not rules_for_contest:
        base_contest_name = contest_name.rsplit('-', 1)[0]
        rules_for_contest = contest_definition.exchange_parsing_rules.get(base_contest_name)

    if not rules_for_contest:
        logging.warning(f"No exchange parsing rules found for contest '{contest_name}'. Malformed line: {line}")
        return None

    if not isinstance(rules_for_contest, list):
        rules_for_contest = [rules_for_contest]

    parsed_successfully = False
    for rule_info in rules_for_contest:
        exchange_regex = rule_info['regex']
        exchange_groups = rule_info['groups']
        exchange_match = re.match(exchange_regex, exchange_rest)
        
        if exchange_match:
            for i, group_name in enumerate(exchange_groups):
                try:
                    val = exchange_match.groups()[i]
                    if val is not None:
                        qso_final_dict[group_name] = val.strip()
                except IndexError:
                    qso_final_dict[group_name] = pd.NA
            parsed_successfully = True
            break
            
    if not parsed_successfully:
        logging.warning(f"Malformed QSO line found (exchange regex failed): {line}")
        return None

    for cabrillo_tag, df_key in contest_definition.header_field_map.items():
        if df_key in log_metadata:
            qso_final_dict[df_key] = log_metadata[df_key]

    return qso_final_dict