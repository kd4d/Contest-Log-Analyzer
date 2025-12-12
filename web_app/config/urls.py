# web_app/config/urls.py
#
# Purpose: Root URL configuration for the Contest Log Analyzer Web App.
#          It maps URL patterns to Django views. Currently configured
#          with the default admin route as a placeholder for Phase 3 bootstrapping.
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
# - Included 'web_app.analyzer.urls' for the root path.
# [0.102.0-Beta] - 2025-12-11
# - Initial creation for Phase 3.
# - Includes basic admin route.

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('web_app.analyzer.urls')),
]