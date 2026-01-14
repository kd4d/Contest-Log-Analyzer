# contest_tools/utils/callsign_utils.py
#
# Purpose: Utility functions for converting callsigns between display format
#          (with /) and filename-safe format (with -).
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
import logging
from typing import List

logger = logging.getLogger(__name__)

def callsign_to_filename_part(callsign: str) -> str:
    """
    Converts a callsign to filename-safe format.
    - Converts / to -
    - Lowercases
    - Validates characters (A-Z, 0-9, / only) - logs warning if invalid
    
    Args:
        callsign: Callsign in display format (e.g., '5B/YT7AW', 'K3LR')
        
    Returns:
        Filename-safe callsign (e.g., '5b-yt7aw', 'k3lr')
    """
    if not callsign:
        logger.warning("Empty callsign provided to callsign_to_filename_part")
        return ""
    
    # Check for invalid characters (only A-Z, 0-9, / allowed)
    if not all(c.upper() in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/' for c in callsign):
        invalid_chars = set(c for c in callsign if c.upper() not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/')
        logger.warning(f"Callsign contains invalid characters {invalid_chars}: {callsign}")
        # Sanitize: remove invalid characters
        callsign = ''.join(c for c in callsign if c.upper() in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/')
    
    # Convert / to - and lowercase
    result = callsign.replace('/', '-').lower()
    return result


def filename_part_to_callsign(filename_part: str) -> str:
    """
    Converts a filename part back to callsign format.
    - Converts - to /
    - Uppercases
    - Pattern: if contains 1-2 dashes (not first/last char), treat as portable
    
    Args:
        filename_part: Filename-safe callsign (e.g., '5b-yt7aw', 'k3lr')
        
    Returns:
        Callsign in display format (e.g., '5B/YT7AW', 'K3LR')
    """
    if not filename_part:
        logger.warning("Empty filename_part provided to filename_part_to_callsign")
        return ""
    
    # Count dashes and check position
    dash_count = filename_part.count('-')
    
    # If no dashes, it's a non-portable callsign - just uppercase
    if dash_count == 0:
        return filename_part.upper()
    
    # If dashes exist and none are at start/end, convert to portable format
    if not filename_part.startswith('-') and not filename_part.endswith('-'):
        # Convert - to / and uppercase
        result = filename_part.replace('-', '/').upper()
        return result
    
    # Edge case: dash at start/end (shouldn't happen in our filenames, but handle defensively)
    logger.warning(f"Filename part has dash at start/end (unexpected): {filename_part}")
    # Remove leading/trailing dashes, then convert
    cleaned = filename_part.strip('-')
    result = cleaned.replace('-', '/').upper()
    return result


def build_callsigns_filename_part(callsigns: List[str]) -> str:
    """
    Builds the callsigns part for filenames/directories.
    Joins multiple callsigns with underscore (_).
    
    Args:
        callsigns: List of callsigns in display format (e.g., ['5B/YT7AW', 'K3LR'])
        
    Returns:
        Filename-safe callsigns part (e.g., '5b-yt7aw_k3lr')
    """
    if not callsigns:
        return ""
    
    filename_parts = [callsign_to_filename_part(call) for call in callsigns]
    return '_'.join(filename_parts)


def parse_callsigns_from_filename_part(filename_part: str) -> List[str]:
    """
    Parses callsigns from a filename/directory part.
    Splits by underscore (_) and converts each part back to callsign format.
    
    Args:
        filename_part: Filename-safe callsigns part (e.g., '5b-yt7aw_k3lr')
        
    Returns:
        List of callsigns in display format (e.g., ['5B/YT7AW', 'K3LR'])
    """
    if not filename_part:
        return []
    
    # Split by underscore
    parts = filename_part.split('_')
    
    # Convert each part back to callsign format
    callsigns = [filename_part_to_callsign(part) for part in parts if part]
    return callsigns
