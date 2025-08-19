# Contest Log Analyzer/contest_tools/contest_specific_annotations/arrl_fd_parser.py
#
# Version: 0.39.2-Beta
# Date: 2025-08-18
#
# Purpose: Provides a custom, contest-specific parser for the ARRL Field Day
#          contest to handle its complex, multi-part exchange format.
#
# --- Revision History ---
## [0.39.2-Beta] - 2025-08-18
### Fixed
# - Rewrote the parser to use a list of regular expressions to handle
#   both standard HF (kHz) and non-standard VHF/UHF/SAT band designators
#   in the frequency field, resolving the parsing error.
## [0.39.1-Beta] - 2025-08-18
# - Initial release of the custom parser.
#
import pandas as pd
import re
import logging
from typing import Dict, Any, List, Tuple

from ..contest_definitions import ContestDefinition

# Pattern 1: Standard HF bands with frequency in kHz (4-5 digits)
QSO_REGEX_HF = re.compile(
    r'QSO:\s+'
    r'(\d{4,5})\s+'           # FrequencyRaw (kHz)
    r'([A-Z]{2})\s+'          # Mode
    r'(\d{4}-\d{2}-\d{2})\s+'  # DateRaw
    r'(\d{4})\s+'             # TimeRaw
    r'([A-Z0-9/]+)\s+'        # MyCallRaw
    r'(\S+)\s+'               # SentClass
    r'([A-Z]{2,4})\s+'        # SentSection
    r'([A-Z0-9/]+)\s+'        # Call
    r'(\S+)\s+'               # RcvdClass
    r'([A-Z]{2,4}|DX)'        # RcvdSection
)
QSO_GROUPS_HF = [
    "FrequencyRaw", "Mode", "DateRaw", "TimeRaw", "MyCallRaw",
    "SentClass", "SentSection", "Call", "RcvdClass", "RcvdSection"
]

# Pattern 2: VHF/UHF/SAT bands where the first field is a band designator, not kHz
QSO_REGEX_VHF = re.compile(
    r'QSO:\s+'
    r'([A-Z0-9]+)\s+'         # Band (e.g., 50, 144, SAT)
    r'([A-Z]{2})\s+'          # Mode
    r'(\d{4}-\d{2}-\d{2})\s+'  # DateRaw
    r'(\d{4})\s+'             # TimeRaw
    r'([A-Z0-9/]+)\s+'        # MyCallRaw
    r'(\S+)\s+'               # SentClass
    r'([A-Z]{2,4})\s+'        # SentSection
    r'([A-Z0-9/]+)\s+'        # Call
    r'(\S+)\s+'               # RcvdClass
    r'([A-Z]{2,4}|DX)'        # RcvdSection
)
QSO_GROUPS_VHF = [
    "Band", "Mode", "DateRaw", "TimeRaw", "MyCallRaw",
    "SentClass", "SentSection", "Call", "RcvdClass", "RcvdSection"
]

QSO_PATTERNS = [
    (QSO_REGEX_HF, QSO_GROUPS_HF),
    (QSO_REGEX_VHF, QSO_GROUPS_VHF)
]

def parse_log(filepath: str, contest_definition: ContestDefinition) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Custom parser for the ARRL Field Day contest."""
    log_metadata: Dict[str, Any] = {}
    qso_records: List[Dict[str, Any]] = []

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    for line in lines:
        sanitized_line = line.replace('\u00a0', ' ').strip().upper()
        if not sanitized_line:
            continue

        if sanitized_line.startswith('QSO:'):
            matched = False
            for regex, groups in QSO_PATTERNS:
                match = regex.match(sanitized_line)
                if match:
                    qso_data = dict(zip(groups, match.groups()))
                    qso_records.append(qso_data)
                    matched = True
                    break
            if not matched:
                logging.warning(f"Skipping malformed QSO line: {line.strip()}")

        elif not sanitized_line.startswith(('START-OF-LOG', 'END-OF-LOG')):
            for cabrillo_tag, df_key in contest_definition.header_field_map.items():
                if sanitized_line.startswith(f"{cabrillo_tag}:"):
                    value = sanitized_line[len(f"{cabrillo_tag}:"):].strip()
                    log_metadata[df_key] = value
                    break

    if not qso_records:
        raise ValueError(f"Custom parser found no valid QSO lines in Cabrillo file: {filepath}")

    df = pd.DataFrame(qso_records)
    return df, log_metadata