# web_app/analyzer/urls.py
#
# Purpose: URL configuration for the analyzer application.
#          Maps the home page and analysis endpoint to views.
#
# Author: Gemini AI
# Date: 2025-12-14
# Version: 0.111.2-Beta
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
# [0.111.2-Beta] - 2025-12-14
# - Fixed routing conflict by moving 'qso_dashboard' pattern above the greedy
#   'view_report' pattern to prevent 404 errors.
# [0.111.0-Beta] - 2025-12-13
# - Added 'qso_dashboard' route for the dedicated QSO Reports Sub-Dashboard.
# [0.110.0-Beta] - 2025-12-13
# - Added 'get_progress' endpoint for polling analysis status.
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
    path('analyze/progress/<str:request_id>/', views.get_progress, name='get_progress'),
    path('report/<str:session_id>/dashboard/qso/', views.qso_dashboard, name='qso_dashboard'),
    path('report/<str:session_id>/<path:file_path>', views.view_report, name='view_report'),
]