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