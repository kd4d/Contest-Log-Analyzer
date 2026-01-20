# web_app/analyzer/templatetags/analyzer_extras.py
#
# Purpose: Custom template tags and filters for the Analyzer app.
#
# Author: Gemini AI
# Date: 2025-12-30
# Version: 0.145.0-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0.
# If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# --- Revision History ---
# [0.145.0-Beta] - 2025-12-30
# - Updated get_item to handle list indexing via integer coercion.

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to look up a key in a dictionary variable.
    Usage: {{ mydict|get_item:key_variable }}
    """
    if not dictionary:
        return ""

    if isinstance(dictionary, dict):
        return dictionary.get(key)

    if isinstance(dictionary, list):
        try:
            return dictionary[int(key)]
        except (IndexError, ValueError, TypeError):
            return ""

    return ""

@register.filter
def replace(value, arg):
    """
    Template filter to replace occurrences of a substring in a string.
    
    Usage examples:
    - {{ string|replace:" : -" }} (replaces space with hyphen)
    - {{ string|replace:"old:new" }} (replaces "old" with "new")
    - {{ string|replace:" ":"_" }} (replaces space with underscore)
    
    The filter accepts the replacement specification as a single string argument.
    If the argument contains a colon, it splits on the first colon to get old:new.
    Otherwise, it treats the entire argument as the string to replace (with empty replacement).
    
    Args:
        value: The string to process
        arg: Replacement specification. Can be:
             - "old:new" format (splits on first colon)
             - " : -" format (space-colon-space separates old and new)
             - Just the old string (replaces with empty string)
    """
    if not value:
        return ""
    
    if not isinstance(value, str):
        value = str(value)
    
    if not arg:
        return value
    
    # Handle format "old:new" or " : -" (space-colon-space format)
    if ':' in arg:
        # Try splitting on colon
        parts = arg.split(':', 1)
        if len(parts) == 2:
            # Preserve the search string (old) as-is to handle spaces correctly
            # Strip only the replacement (new) to handle " : -" format correctly
            # " : -" means: replace " " (space) with "-" (hyphen, no leading space)
            old = parts[0]
            new = parts[1].strip()  # Strip replacement to remove leading space
            return value.replace(old, new)
    
    # If no colon or malformed, treat entire arg as string to replace (with empty)
    return value.replace(arg, "")

@register.filter
def abbreviate_multiplier(value):
    """
    Template filter to abbreviate multiplier names for compact tab display.
    
    Abbreviations:
    - "Provinces" → "Provs"
    - "Mexican States" → "Mex"
    - "ITU Regions" → "Regs"
    - "Regions" → "Regs"
    
    Usage: {{ mult_name|abbreviate_multiplier }}
    """
    if not value:
        return ""
    
    if not isinstance(value, str):
        value = str(value)
    
    # Strip whitespace for matching
    value_trimmed = value.strip()
    
    # Abbreviation mapping - check both full names and prefixed versions
    abbreviations = {
        # Full names
        "Provinces": "Provs",
        "Mexican States": "Mex",
        "ITU Regions": "Regs",
        "Regions": "Regs",
        # Prefixed versions (e.g., "US Provinces", "Mexican Regions")
        "US Provinces": "US Provs",
        "Mexican States": "Mex",
        "Mexican Regions": "Mex Regs",
        "ITU Regions": "Regs",
    }
    
    # Try exact match first
    if value_trimmed in abbreviations:
        return abbreviations[value_trimmed]
    
    # Try to match with prefix removed (e.g., "US Provinces" -> check "Provinces")
    # This handles cases like "US Provinces", "Canadian Provinces", etc.
    for key, abbr in [("Provinces", "Provs"), ("Regions", "Regs")]:
        if value_trimmed.endswith(f" {key}"):
            prefix = value_trimmed[:-len(f" {key}")]
            return f"{prefix} {abbr}"
    
    # Special handling for "Mexican States" - can appear with or without prefix
    if "Mexican States" in value_trimmed:
        # If it's just "Mexican States", return "Mex"
        if value_trimmed == "Mexican States":
            return "Mex"
        # If it has a prefix like "US Mexican States" (unlikely but handle it), keep prefix
        if value_trimmed.startswith("Mexican States"):
            return value_trimmed.replace("Mexican States", "Mex")
    
    # Return original value if no match
    return value