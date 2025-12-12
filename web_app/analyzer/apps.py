# web_app/analyzer/apps.py
#
# Purpose: Django app configuration for the analyzer application.
#
# Author: Gemini AI
# Date: 2025-12-12
# Version: 0.103.0-Beta
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
#
# --- Revision History ---
# [0.103.0-Beta] - 2025-12-12
# - Initial creation.

from django.apps import AppConfig

class AnalyzerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web_app.analyzer'