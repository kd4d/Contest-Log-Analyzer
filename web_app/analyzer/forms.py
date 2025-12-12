# web_app/analyzer/forms.py
#
# Purpose: Django forms for the analyzer application.
#          Defines the multi-slot upload form for Cabrillo logs.
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
# - Implemented UploadLogForm with three identity-agnostic slots.

from django import forms

class UploadLogForm(forms.Form):
    # Identity Agnostic Labels
    log1 = forms.FileField(
        label="Log 1",
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.log,.cbr,.txt'})
    )
    log2 = forms.FileField(
        label="Log 2",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.log,.cbr,.txt'})
    )
    log3 = forms.FileField(
        label="Log 3",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.log,.cbr,.txt'})
    )