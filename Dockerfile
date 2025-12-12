# Dockerfile
#
# Purpose: Defines the Docker container image for the Contest Log Analyzer
#          Web Application (Phase 3). It sets up a lightweight Python 3.11-slim
#          environment, installs dependencies, and explicitly excludes multimedia
#          libraries (ffmpeg) to enforce architectural constraints.
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
# - Initial creation for Phase 3 (The Web Pathfinder).
# - Configured for Python 3.11-slim with /app PYTHONPATH.

FROM python:3.11-slim

# Prevent Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1
# Add the root directory to PYTHONPATH so web_app can import contest_tools
ENV PYTHONPATH /app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "web_app/manage.py", "runserver", "0.0.0.0:8000"]