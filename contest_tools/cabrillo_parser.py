# contest_tools/cabrillo_parser.py
#
# Purpose: Provides functionality to parse Cabrillo log files into a Pandas DataFrame
#          and extract log metadata. It uses a ContestDefinition object to guide
#          the parsing of contest-specific header fields and QSO exchange formats.
#
# Copyright (c) 2025 Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import re
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
import os
import logging

from .contest_definitions import ContestDefinition

# --- Internal Regex Definitions for QSO lines ---

def _validate_header_callsign(callsign: str) -> str:
    """
    Validates CALLSIGN from Cabrillo header.
    Raises ValueError if invalid (reject log).
    Returns normalized callsign (uppercase, stripped).
    
    Rules:
    - Only letters (A-Z), digits (0-9), and / allowed
    - Cannot start or end with /
    - Cannot be empty/whitespace
    """
    if not callsign or not callsign.strip():
        raise ValueError("CALLSIGN header field is empty")
    
    callsign = callsign.strip().upper()
    
    # Check: only letters, digits, and / allowed
    if not all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/' for c in callsign):
        invalid_chars = set(c for c in callsign if c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/')
        raise ValueError(f"CALLSIGN contains invalid characters {invalid_chars}: {callsign}")
    
    # Check: cannot start or end with /
    if callsign.startswith('/') or callsign.endswith('/'):
        raise ValueError(f"CALLSIGN cannot start or end with /: {callsign}")
    
    return callsign
QSO_REGEX_HF = re.compile(r'QSO:\s+(\d{4,5})\s+([A-Z]{2})\s+(\d{4}-\d{2}-\d{2})\s+(\d{4})\s+([A-Z0-9/]+)\s+(.*)')
QSO_GROUPS_HF = ["FrequencyRaw", "Mode", "DateRaw", "TimeRaw", "MyCallRaw", "ExchangeRest"]

QSO_REGEX_VHF = re.compile(r'QSO:\s+([A-Z0-9.]+)\s+([A-Z]{2})\s+(\d{4}-\d{2}-\d{2})\s+(\d{4})\s+([A-Z0-9/]+)\s+(.*)')
QSO_GROUPS_VHF = ["Band", "Mode", "DateRaw", "TimeRaw", "MyCallRaw", "ExchangeRest"]


def parse_qso_common_fields(qso_line: str) -> Optional[Dict[str, Any]]:
    """
    Parses the common, standardized fields from a raw QSO line using a robust
    two-pattern regex system to handle both HF and VHF+ formats. This is the
    centralized helper function used by both the generic and all custom parsers.
    """
    common_match = QSO_REGEX_HF.match(qso_line)
    if common_match:
        common_groups = QSO_GROUPS_HF
    else:
        common_match = QSO_REGEX_VHF.match(qso_line)
        if common_match:
            common_groups = QSO_GROUPS_VHF
        else:
            return None
            
    return dict(zip(common_groups, common_match.groups()))


def parse_cabrillo_file(filepath: str, contest_definition: ContestDefinition) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Parses a Cabrillo log file into a Pandas DataFrame of QSOs and extracts header metadata.
    """
    log_metadata: Dict[str, Any] = {}
    qso_records: List[Dict[str, Any]] = []
    
    x_qso_count = 0
    parser_error_count = [0]  # Use list for mutable reference
    max_warnings = 5

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        raise ValueError(f"Error reading Cabrillo file {filepath}: {e}")

    for i, line in enumerate(lines):
        cleaned_line = line.replace('\u00a0', ' ').strip()
        line_to_process = cleaned_line.upper() if cleaned_line.upper().startswith('QSO:') else cleaned_line
        
        if not line_to_process:
            continue
        elif line_to_process.startswith('END-OF-LOG:'):
            break
        elif line_to_process.startswith('X-QSO:'):
            if x_qso_count < max_warnings:
                logging.warning(f"Ignoring X-QSO line in {os.path.basename(filepath)}: {cleaned_line}")
                x_qso_count += 1
            elif x_qso_count == max_warnings:
                logging.warning(f"Additional X-QSO messages suppressed (max {max_warnings} shown)")
                x_qso_count += 1
            continue
        elif line_to_process.startswith('QSO:'):
            qso_data = _parse_qso_line(line_to_process, contest_definition, log_metadata, cleaned_line, filepath, parser_error_count, max_warnings)
            if qso_data:
                qso_data['RawQSO'] = line_to_process
                qso_records.append(qso_data)
        elif line_to_process.startswith('START-OF-LOG:'):
            continue
        else:
            for cabrillo_tag, df_key in contest_definition.header_field_map.items():
                if line_to_process.startswith(f"{cabrillo_tag}:"):
                    value = line_to_process[len(f"{cabrillo_tag}:"):].strip()
                    # Validate CALLSIGN header field
                    if df_key == 'MyCall':
                        value = _validate_header_callsign(value)
                    log_metadata[df_key] = value
                    break

    if not qso_records:
        raise ValueError(f"No valid QSO lines found in Cabrillo file: {filepath}")
    
    df = pd.DataFrame(qso_records)
    return df, log_metadata

def _parse_qso_line(
    line: str,
    contest_definition: ContestDefinition,
    log_metadata: Dict[str, Any],
    original_line: str = None,
    filepath: str = None,
    parser_error_count: List[int] = None,
    max_warnings: int = 5
) -> Optional[Dict[str, Any]]:
    """
    Internal helper to parse a single QSO line, now a wrapper around the
    shared common field parser and the exchange-specific logic.
    Returns None if parsing fails (like X-QSO), preventing corrupted data from entering the DataFrame.
    """
    if original_line is None:
        original_line = line
    if filepath is None:
        filepath = ""
    if parser_error_count is None:
        parser_error_count = [0]
    
    common_data = parse_qso_common_fields(line)
    if not common_data:
        if parser_error_count[0] < max_warnings:
            logging.warning(f"Skipping malformed QSO line in {os.path.basename(filepath)}: {original_line}")
        elif parser_error_count[0] == max_warnings:
            logging.warning(f"Additional parser error messages suppressed (max {max_warnings} shown)")
        parser_error_count[0] += 1
        return None

    qso_final_dict = {col: pd.NA for col in contest_definition.default_qso_columns}
    for key, val in common_data.items():
        if key == 'MyCallRaw':
            # Validate QSO line callsign (warn and skip if invalid, like X-QSO)
            if not val or not str(val).strip():
                if parser_error_count[0] < max_warnings:
                    logging.warning(f"QSO line has empty callsign, skipping in {os.path.basename(filepath)}: {original_line}")
                elif parser_error_count[0] == max_warnings:
                    logging.warning(f"Additional parser error messages suppressed (max {max_warnings} shown)")
                parser_error_count[0] += 1
                return None
            # Note: We don't validate format for QSO line callsigns (they are data/metadata)
            # Only check for empty/None
        qso_final_dict[key] = val.strip() if isinstance(val, str) else val

    exchange_rest = qso_final_dict.pop('ExchangeRest', '').strip()
    
    contest_name = log_metadata.get('ContestName')
    rules_for_contest = contest_definition.exchange_parsing_rules.get(contest_name)
    if not rules_for_contest:
        base_contest_name = contest_name.rsplit('-', 1)[0]
        rules_for_contest = contest_definition.exchange_parsing_rules.get(base_contest_name, [])

    if not isinstance(rules_for_contest, list):
        rules_for_contest = [rules_for_contest]

    # Try to match exchange pattern
    exchange_matched = False
    for rule_info in rules_for_contest:
        exchange_match = re.match(rule_info['regex'], exchange_rest)
        if exchange_match:
            for i, group_name in enumerate(rule_info['groups']):
                val = exchange_match.groups()[i]
                if val is not None:
                    qso_final_dict[group_name] = val.strip()
            exchange_matched = True
            break
    
    # If exchange didn't match, skip this QSO (like X-QSO) to prevent corrupted data
    if not exchange_matched:
        if parser_error_count[0] < max_warnings:
            logging.warning(f"Skipping QSO line with unmatched exchange format in {os.path.basename(filepath)}: {original_line}")
        elif parser_error_count[0] == max_warnings:
            logging.warning(f"Additional parser error messages suppressed (max {max_warnings} shown)")
        parser_error_count[0] += 1
        return None
    
    qso_final_dict.update(log_metadata)
    return qso_final_dict
