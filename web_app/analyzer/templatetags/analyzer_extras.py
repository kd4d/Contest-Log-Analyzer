# web_app/analyzer/templatetags/analyzer_extras.py
#
# Purpose: Custom template tags and filters for the Analyzer app.
#
# Author: Gemini AI
# Date: 2025-12-12
# Version: 1.0.0
#
# License: Mozilla Public License, v. 2.0

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to look up a key in a dictionary variable.
    Usage: {{ mydict|get_item:key_variable }}
    """
    if dictionary is None:
        return ""
    return dictionary.get(key)