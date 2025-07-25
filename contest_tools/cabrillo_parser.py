v# Contest Log Analyzer/contest_tools/cabrillo_parser.py
#
# Purpose: Provides functionality to parse Cabrillo log files into a Pandas DataFrame
#          and extract log metadata. It uses a ContestDefinition object to guide
#          the parsing of contest-specific header fields and QSO exchange formats.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-25
# Version: 0.15.0-Beta
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
    
    # Track the actual contest name from the log's CONTEST: header
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
            qso_data = _parse_qso_line(line, contest_definition, log_metadata, actual_contest_name)
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
    
    # Ensure the actual_contest_name found matches the contest_definition's name for consistency
    if actual_contest_name and actual_contest_name != contest_definition.contest_name:
        raise ValueError(f"Contest name in Cabrillo file header ('{actual_contest_name}') "
                         f"does not match the provided ContestDefinition ('{contest_definition.contest_name}').")

    # Construct DataFrame from the list of QSO dictionaries
    df = pd.DataFrame(qso_records)

    return df, log_metadata

def _parse_qso_line(
    line: str,
    contest_definition: ContestDefinition,
    log_metadata: Dict[str, Any],
    cabrillo_contest_name: Optional[str]
) -> Optional[Dict[str, Any]]:
    """
    Internal helper to parse a single QSO line from a Cabrillo log.

    Args:
        line (str): The raw QSO line string.
        contest_definition (ContestDefinition): The definition object to guide parsing.
        log_metadata (Dict[str, Any]): The extracted header metadata.
        cabrillo_contest_name (Optional[str]): The contest name from the CONTEST: header.

    Returns:
        Optional[Dict[str, Any]]: A dictionary representing the parsed QSO, or None if parsing fails.
    """
    
    # Initialize the dictionary for this QSO with all possible final columns set to NA
    qso_final_dict = {col: pd.NA for col in contest_definition.default_qso_columns}

    # Parse the common part of the QSO line
    common_match = re.match(contest_definition.qso_common_fields_regex, line)
    if not common_match:
        return None # Skip malformed common part

    # Map captured common groups to their names
    qso_dict_common_parsed = dict(zip(contest_definition.qso_common_field_names, common_match.groups()))
    
    # Add raw parsed fields to the final dictionary for downstream processing
    for key, val in qso_dict_common_parsed.items():
        qso_final_dict[key] = val.strip() if isinstance(val, str) else val

    # Extract the contest-specific exchange part
    exchange_rest = qso_final_dict.pop('ExchangeRest', '').strip()

    # Parse the contest-specific exchange
    exchange_info = contest_definition.get_exchange_parse_info(cabrillo_contest_name or contest_definition.contest_name)
    
    if exchange_info:
        exchange_regex = exchange_info['regex']
        exchange_groups = exchange_info['groups']
        exchange_match = re.match(exchange_regex, exchange_rest)
        
        if exchange_match:
            for i, group_name in enumerate(exchange_groups):
                try:
                    val = exchange_match.groups()[i]
                    if val is not None:
                        qso_final_dict[group_name] = val.strip()
                except IndexError:
                    qso_final_dict[group_name] = pd.NA
        else:
            # If exchange doesn't match, fields remain NA
            pass
            
    # Add duplicated header metadata to each QSO record
    for cabrillo_tag, df_key in contest_definition.header_field_map.items():
        if df_key in log_metadata:
            qso_final_dict[df_key] = log_metadata[df_key]

    return qso_final_dict
