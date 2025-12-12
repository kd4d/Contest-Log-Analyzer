# web_app/config/wsgi.py
#
# Purpose: WSGI config for the Contest Log Analyzer Web App.
#          It exposes the WSGI callable as a module-level variable named ``application``.
#
# Author: Gemini AI
# Date: 2025-12-11
# Version: 0.102.0-Beta
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
# --- Revision History ---
# [0.102.0-Beta] - 2025-12-11
# - Initial creation for Phase 3.

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()