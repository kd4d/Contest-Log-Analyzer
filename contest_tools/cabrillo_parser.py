# Contest Log Analyzer/contest_tools/cabrillo_parser.py
#
# Purpose: Provides functionality to parse Cabrillo log files into a Pandas DataFrame
#          and extract log metadata. It uses a ContestDefinition object to guide
#          the parsing of contest-specific header fields and QSO exchange formats.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-31
# Version: 0.55.9-Beta
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
## [0.55.9-Beta] - 2025-08-31
### Changed
# - Refactored the parser to use an internal, two-pattern regex system
#   to robustly handle both HF (kHz) frequencies and VHF+ band designators.
# - The primary QSO parsing regex is no longer loaded from JSON.
## [0.52.6-Beta] - 2025-08-26
### Changed
# - The parser now includes the raw, cleaned QSO: line in its output
#   under the 'RawQSO' key to support enhanced diagnostics.
## [0.31.55-Beta] - 2025-08-11
### Changed
# - Consolidated X-QSO warnings to a single message per log file.
## [0.31.45-Beta] - 2025-08-10
### Changed
# - Removed temporary debugging log statements from the _parse_qso_line method.
## [0.31.41-Beta] - 2025-08-10
### Added
# - Added a WARNING-level log message to report when X-QSO lines are found
#   and ignored in a log file.
## [0.31.40-Beta] - 2025-08-10
### Changed
# - Implemented case-insensitive parsing for QSO lines by converting them
#   to uppercase during the data cleanup stage.
## [0.31.37-Beta] - 2025-08-10
### Changed
# - Synchronizing to current project version to resolve environmental
#   file mismatch issues.
## [0.31.36-Beta] - 2025-08-10
### Added
# - Added a hexadecimal dump of the exchange string to the debug logs to
#   conclusively identify problematic characters.
## [0.31.35-Beta] - 2025-08-10
### Added
# - Added detailed INFO-level logging statements to the _parse_qso_line
#   method to assist with debugging parsing failures.
## [0.30.34-Beta] - 2025-08-06
### Changed
# - Removed diagnostic print statements from _parse_qso_line.
## [0.30.33-Beta] - 2025-08-06
### Added
# - Added diagnostic print statements to _parse_qso_line to debug
#   persistent parsing failures.
## [0.30.31-Beta] - 2025-08-06
### Changed
# - Added a line to the main parsing loop to replace non-breaking spaces
#   with regular spaces, increasing parsing robustness.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
import re
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
import os
import logging

# Import the ContestDefinition class from the definitions package
from .contest_definitions import ContestDefinition # Relative import within contest_tools

# --- Internal Regex Definitions for QSO lines ---
# Pattern 1: Standard HF bands with frequency in kHz (4-5 digits)
QSO_REGEX_HF = re.compile(r'QSO:\s+(\d{4,5})\s+([A-Z]{2})\s+(\d{4}-\d{2}-\d{2})\s+(\d{4})\s+([A-Z0-9/]+)\s+(.*)')
QSO_GROUPS_HF = ["FrequencyRaw", "Mode", "DateRaw", "TimeRaw", "MyCallRaw", "ExchangeRest"]

# Pattern 2: VHF/UHF/etc. bands where the first field is a band designator
QSO_REGEX_VHF = re.compile(r'QSO:\s+([A-Z0-9.]+)\s+([A-Z]{2})\s+(\d{4}-\d{2}-\d{2})\s+(\d{4})\s+([A-Z0-9/]+)\s+(.*)')
QSO_GROUPS_VHF = ["Band", "Mode", "DateRaw", "TimeRaw", "MyCallRaw", "ExchangeRest"]


def parse_cabrillo_file(filepath: str, contest_definition: ContestDefinition) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Parses a Cabrillo log file into a Pandas DataFrame of QSOs and extracts header metadata.
    """
    log_metadata: Dict[str, Any] = {}
    qso_records: List[Dict[str, Any]] = []
    
    actual_contest_name: Optional[str] = None
    x_qso_warning_issued = False

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Cabrillo file not found: {filepath}")
    except Exception as e:
        raise ValueError(f"Error reading Cabrillo file {filepath}: {e}")

    in_header = True
    
    for i, line in enumerate(lines):
        # Clean the line of nbsp and leading/trailing whitespace
        cleaned_line = line.replace('\u00a0', ' ').strip()
        
        # Create a temporary uppercase version for a case-insensitive check
        temp_upper_line = cleaned_line.upper()
        
        # Check if it's a QSO line. If so, use the uppercase version for all parsing.
        if temp_upper_line.startswith('QSO:') or temp_upper_line.startswith('QSO-X:'):
            line_to_process = temp_upper_line
        else:
            line_to_process = cleaned_line

        if not line_to_process: # Skip blank lines
            continue

        if line_to_process.startswith('START-OF-LOG:'):
            if i != 0:
                raise ValueError(f"Cabrillo format error: START-OF-LOG: must be the first line. (Line {i+1})")
            continue
        elif line_to_process.startswith('END-OF-LOG:'):
            break
        elif line_to_process.startswith('X-QSO:'):
            if not x_qso_warning_issued:
                logging.warning(f"Ignoring X-QSO line(s) in {os.path.basename(filepath)}")
                x_qso_warning_issued = True
            continue
        elif line_to_process.startswith('QSO:'):
            in_header = False
            qso_data = _parse_qso_line(line_to_process, contest_definition, log_metadata)
            if qso_data:
                qso_data['RawQSO'] = line_to_process
                qso_records.append(qso_data)
            continue 

        if in_header:
            for cabrillo_tag, df_key in contest_definition.header_field_map.items():
                if line_to_process.startswith(f"{cabrillo_tag}:"):
                    value = line_to_process[len(f"{cabrillo_tag}:"):].strip()
                    log_metadata[df_key] = value
                    if cabrillo_tag == 'CONTEST':
                        actual_contest_name = value
                    break 
    
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

    # --- New Two-Pattern Matching Logic ---
    common_match = QSO_REGEX_HF.match(line)
    if common_match:
        common_groups = QSO_GROUPS_HF
    else:
        common_match = QSO_REGEX_VHF.match(line)
        if common_match:
            common_groups = QSO_GROUPS_VHF
        else:
            logging.warning(f"Skipping malformed QSO line: {line}")
            return None
    
    qso_dict_common_parsed = dict(zip(common_groups, common_match.groups()))
    
    for key, val in qso_dict_common_parsed.items():
        qso_final_dict[key] = val.strip() if isinstance(val, str) else val

    exchange_rest = qso_final_dict.pop('ExchangeRest', '').strip()

    contest_name = log_metadata.get('ContestName')
    rules_for_contest = contest_definition.exchange_parsing_rules.get(contest_name)
    
    if not rules_for_contest:
        base_contest_name = contest_name.rsplit('-', 1)[0]
        rules_for_contest = contest_definition.exchange_parsing_rules.get(base_contest_name)

    if not rules_for_contest:
        return None 

    if not isinstance(rules_for_contest, list):
        rules_for_contest = [rules_for_contest]

    parsed_successfully = False
    for i, rule_info in enumerate(rules_for_contest):
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
        return None 

    for cabrillo_tag, df_key in contest_definition.header_field_map.items():
        if df_key in log_metadata:
            qso_final_dict[df_key] = log_metadata[df_key]

    return qso_final_dict