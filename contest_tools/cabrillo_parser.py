# Contest Log Analyzer/contest_tools/cabrillo_parser.py
#
# Purpose: Provides functionality to parse Cabrillo log files into a Pandas DataFrame
#          and extract log metadata. It uses a ContestDefinition object to guide
#          the parsing of contest-specific header fields and QSO exchange formats.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-03
# Version: 0.24.9-Beta
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
# All notable changes to this project will be documented in this file.
# The format is based on "Keep a Changelog" (https://keepachangelog.com/en/1.0.0/),
# and this project aims to adhere to Semantic Versioning (https://semver.org/).
## [0.24.9-Beta] - 2025-08-03
### Changed
# - Reworked `_parse_qso_line` to handle a list of regex rules for a single
#   contest, enabling support for complex, asymmetric exchanges.
## [0.24.8-Beta] - 2025-08-01
### Fixed
# - The 'Datetime' column is now correctly created as timezone-aware (UTC) to
#   prevent alignment issues with the master time index in reports.
## [0.24.7-Beta] - 2025-08-01
### Added
# - Added temporary diagnostic print statements to debug QSO line parsing failures.
## [0.22.0-Beta] - 2025-07-31
### Changed
# - The exchange parsing logic is now more robust. It iterates through all
#   available parsing rules in the contest definition and uses the first one
#   that successfully matches the QSO line, making it resilient to minor
#   variations in the CONTEST header.
## [0.15.0-Beta] - 2025-07-25
# - Standardized version for final review. No functional changes.
## [0.9.0-Beta] - 2025-07-18
# - Initial Beta release of `cabrillo_parser.py`.
# - Implemented `parse_cabrillo_file` function for Cabrillo ingestion.
# - Handles parsing of Cabrillo header lines and standard QSO fields.
# - Integrates with `ContestDefinition` to dynamically parse contest-specific exchange fields.
import re
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
import os

# Import the ContestDefinition class from the definitions package
from .contest_definitions import ContestDefinition # Relative import within contest_tools


def parse_cabrillo_file(filepath: str, contest_definition: ContestDefinition) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Parses a Cabrillo log file into a Pandas DataFrame of QSOs and extracts header metadata.
    The parsing is guided by a ContestDefinition object, allowing for flexible handling
    of contest-specific header fields and QSO exchange formats.

    Args:
        filepath (str): The path to the Cabrillo log file.
        contest_definition (ContestDefinition): An instance of ContestDefinition
                                                containing rules for the contest.

    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]: A tuple containing:
            - pd.DataFrame: A DataFrame where each row is a QSO, with standardized columns
                            and contest-specific exchange fields.
            - Dict[str, Any]: A dictionary containing log header metadata.

    Raises:
        FileNotFoundError: If the specified Cabrillo file does not exist.
        ValueError: If the Cabrillo file has an invalid format (e.g., missing START-OF-LOG,
                    missing CONTEST/CALLSIGN, malformed QSO lines, unsupported contest).
    """
    log_metadata: Dict[str, Any] = {}
    qso_records: List[Dict[str, Any]] = []
    
    actual_contest_name: Optional[str] = None

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Cabrillo file not found: {filepath}")
    except Exception as e:
        raise ValueError(f"Error reading Cabrillo file {filepath}: {e}")

    in_header = True
    
    for i, line in enumerate(lines):
        line = line.strip()

        if not line: # Skip blank lines
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
            for cabrillo_tag, df_key in contest_definition.header_field_map.items():
                if line.startswith(f"{cabrillo_tag}:"):
                    value = line[len(f"{cabrillo_tag}:"):].strip()
                    log_metadata[df_key] = value
                    if cabrillo_tag == 'CONTEST':
                        actual_contest_name = value
                    break 
    
    if not qso_records:
        raise ValueError(f"No valid QSO lines found in Cabrillo file: {filepath}")
    
    if 'MyCall' not in log_metadata or 'ContestName' not in log_metadata:
        raise ValueError(f"Required header fields (CALLSIGN:, CONTEST:) not found in {filepath}")
    
    # Construct DataFrame from the list of QSO dictionaries
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
        return None 

    qso_dict_common_parsed = dict(zip(contest_definition.qso_common_field_names, common_match.groups()))
    
    for key, val in qso_dict_common_parsed.items():
        qso_final_dict[key] = val.strip() if isinstance(val, str) else val

    exchange_rest = qso_final_dict.pop('ExchangeRest', '').strip()

    # --- New Robust Parsing Logic ---
    # Look up the rules for the specific contest identified in the header.
    contest_name = log_metadata.get('ContestName')
    rules_for_contest = contest_definition.exchange_parsing_rules.get(contest_name)
    
    if not rules_for_contest:
        # Fallback for contests that might use a generic name (e.g., NAQP-CW using NAQP rules)
        base_contest_name = contest_name.rsplit('-', 1)[0]
        rules_for_contest = contest_definition.exchange_parsing_rules.get(base_contest_name)

    if not rules_for_contest:
        return None # No parsing rule found for this contest

    # Ensure rules are in a list to handle both single-rule and multi-rule contests
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
            break # Stop after the first successful match
            
    if not parsed_successfully:
        return None # None of the rules for this contest matched the line

    for cabrillo_tag, df_key in contest_definition.header_field_map.items():
        if df_key in log_metadata:
            qso_final_dict[df_key] = log_metadata[df_key]

    return qso_final_dict