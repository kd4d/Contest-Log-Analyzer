# web_app/analyzer/views.py
#
# Purpose: Django views for the Contest Log Analyzer application.
#          Handles log file uploads, invokes the core LogManager for parsing,
#          aggregates data using DAL components, and renders the dashboard.
#
# Author: Gemini AI
# Date: 2025-12-11
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
# --- Revision History ---
# [0.103.3-Beta] - 2025-12-12
# - Added logging to capture stack traces for debugging upload failures.
# [0.103.0-Beta] - 2025-12-11
# - Initial creation for Phase 3.
# - Implements the "Ephemeral I/O" pattern using tempfile.

import os
import tempfile
import shutil
import logging
from django.shortcuts import render, redirect
from .forms import UploadLogForm

# Import Core Logic
from contest_tools.log_manager import LogManager
from contest_tools.data_aggregators.time_series import TimeSeriesAggregator

logger = logging.getLogger(__name__)

def home(request):
    form = UploadLogForm()
    return render(request, 'analyzer/home.html', {'form': form})

def analyze_logs(request):
    if request.method == 'POST':
        form = UploadLogForm(request.POST, request.FILES)
        if form.is_valid():
            # 1. Create Ephemeral Context
            temp_dir = tempfile.mkdtemp()
            try:
                # 2. Save Uploads
                log_paths = []
                # Ensure data directory exists for CTY lookups if not mapped (Docker handles this though)
                
                files = [request.FILES.get('log1'), request.FILES.get('log2'), request.FILES.get('log3')]
                files = [f for f in files if f] # Filter None

                for f in files:
                    file_path = os.path.join(temp_dir, f.name)
                    with open(file_path, 'wb+') as destination:
                        for chunk in f.chunks():
                            destination.write(chunk)
                    log_paths.append(file_path)

                # 3. Process with LogManager
                # Note: We rely on docker-compose env vars for CONTEST_INPUT_DIR to find CTY files
                root_input = os.environ.get('CONTEST_INPUT_DIR', '/app/CONTEST_LOGS_REPORTS')
                
                lm = LogManager()
                # Load logs (auto-detect contest type)
                lm.load_log_batch(log_paths, root_input, 'after', wrtc_year=None)

                lm.finalize_loading(temp_dir)
                
                # 4. Aggregate Data (Proof of Life)
                ts_agg = TimeSeriesAggregator(lm.logs)
                ts_data = ts_agg.get_time_series_data()
                
                # Extract basic scalars for dashboard
                context = {
                    'logs': [],
                    'contest_name': lm.logs[0].metadata.get('ContestName', 'Unknown'),
                }
                
                for call, data in ts_data['logs'].items():
                    context['logs'].append({
                        'callsign': call,
                        'score': data['scalars']['points_sum'], # Using raw points for simple verify
                        'qsos': data['scalars']['net_qsos']
                    })

                return render(request, 'analyzer/dashboard.html', context)

            except Exception as e:
                logger.exception("Log analysis failed")
                return render(request, 'analyzer/home.html', {'form': form, 'error': str(e)})
            finally:
                # 5. Cleanup
                shutil.rmtree(temp_dir)
    
    return redirect('home')