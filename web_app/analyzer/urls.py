# web_app/analyzer/urls.py
#
# Purpose: URL configuration for the analyzer application.
#          Maps the home page and analysis endpoint to views.
#
# Author: Gemini AI
# Date: 2025-12-13
# Version: 0.103.1-Beta
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
# [0.103.1-Beta] - 2025-12-13
# - Removed trailing slash from 'view_report' pattern to support clean file paths.
# [0.103.0-Beta] - 2025-12-12
# - Initial creation.
# - Defined routes for 'home' and 'analyze'.

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('analyze/', views.analyze_logs, name='analyze'),
    path('report/<str:session_id>/<path:file_path>', views.view_report, name='view_report'),
]