# web_app/analyzer/views.py
#
# Purpose: Django views for the Contest Log Analyzer application.
#          Handles log file uploads, invokes the core LogManager for parsing,
#          aggregates data using DAL components, and renders the dashboard.
#
# Author: Gemini AI
# Date: 2025-12-13
# Version: 0.108.0-Beta
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
# [0.108.0-Beta] - 2025-12-13
# - Injected CtyLookup version info and full contest title into dashboard context.
# [0.105.4-Beta] - 2025-12-13
# - Explicitly instantiated ReportGenerator to create physical report files.
# - Added dynamic filename generation for animation, plot, and mult reports to context.
# [0.105.3-Beta] - 2025-12-13
# - Updated context to include pre-assembled 'report_url_path' to handle empty event IDs safely.
# [0.105.1-Beta] - 2025-12-13
# - Replaced ephemeral tempfile storage with session-based storage in MEDIA_ROOT.
# - Implemented lazy cleanup for old sessions.
# - Updated context to include drill-down parameters (year, event, combo).
# [0.105.0-Beta] - 2025-12-13
# - Added 'run_qsos' and 'run_percent' to the dashboard context context.
# [0.104.0-Beta] - 2025-12-12
# - Updated analyze_logs to consume new 'final_score' and 'mult_breakdown'
#   from TimeSeriesAggregator instead of raw points.
# - Added logic to dynamically determine multiplier headers.
# [0.103.3-Beta] - 2025-12-12
# - Added logging to capture stack traces for debugging upload failures.
# [0.103.0-Beta] - 2025-12-11
# - Initial creation for Phase 3.
# - Implements the "Ephemeral I/O" pattern using tempfile.
import os
import shutil
import logging
import uuid
import time
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import UploadLogForm

# Import Core Logic
from contest_tools.log_manager import LogManager
from contest_tools.data_aggregators.time_series import TimeSeriesAggregator
from contest_tools.report_generator import ReportGenerator
from contest_tools.core_annotations import CtyLookup

logger = logging.getLogger(__name__)

def _cleanup_old_sessions(max_age_seconds=3600):
    """Lazy cleanup: Deletes session directories older than 1 hour."""
    sessions_root = os.path.join(settings.MEDIA_ROOT, 'sessions')
    if not os.path.exists(sessions_root):
        return

    now = time.time()
    for item in os.listdir(sessions_root):
        item_path = os.path.join(sessions_root, item)
        if os.path.isdir(item_path):
            try:
                if os.stat(item_path).st_mtime < (now - max_age_seconds):
                    shutil.rmtree(item_path)
                    logger.info(f"Cleaned up old session: {item}")
            except Exception as e:
                logger.warning(f"Failed to cleanup session {item}: {e}")

def home(request):
    form = UploadLogForm()
    return render(request, 'analyzer/home.html', {'form': form})

def analyze_logs(request):
    if request.method == 'POST':
        _cleanup_old_sessions()  # Trigger lazy cleanup
        form = UploadLogForm(request.POST, request.FILES)
        if form.is_valid():
            # 1. Create Session Context
            session_key = str(uuid.uuid4())
            session_path = os.path.join(settings.MEDIA_ROOT, 'sessions', session_key)
            os.makedirs(session_path, exist_ok=True)

            try:
                # 2. Save Uploads
                log_paths = []
                # Ensure data directory exists for CTY lookups if not mapped (Docker handles this though)
                
                files = [request.FILES.get('log1'), request.FILES.get('log2'), request.FILES.get('log3')]
                files = [f for f in files if f] # Filter None

                for f in files:
                    file_path = os.path.join(session_path, f.name)
                    with open(file_path, 'wb+') as destination:
                        for chunk in f.chunks():
                            destination.write(chunk)
                    log_paths.append(file_path)

                # 3. Process with LogManager
                # Note: We rely on docker-compose env vars for CONTEST_INPUT_DIR
                root_input = os.environ.get('CONTEST_INPUT_DIR', '/app/CONTEST_LOGS_REPORTS')
                
                lm = LogManager()
                # Load logs (auto-detect contest type)
                lm.load_log_batch(log_paths, root_input, 'after')

                lm.finalize_loading(session_path)

                # 4. Generate Physical Reports (Drill-Down Assets)
                generator = ReportGenerator(lm.logs, root_output_dir=session_path)
                generator.run_reports('all')
                
                # 5. Aggregate Data (Dashboard Scalars)
                ts_agg = TimeSeriesAggregator(lm.logs)
                ts_data = ts_agg.get_time_series_data()
                 
                # Extract basic scalars for dashboard
                # Construct relative path components for the template
                first_log_meta = lm.logs[0].get_metadata()
                contest_name = first_log_meta.get('ContestName', 'Unknown').replace(' ', '_')
                # Date/Year extraction logic mirrors LogManager
                df_first = lm.logs[0].get_processed_data()
                year = df_first['Date'].dropna().iloc[0].split('-')[0] if not df_first.empty else "UnknownYear"
                
                # Re-derive event_id locally or fetch from metadata if available (LogManager stores it there now)
                event_id = first_log_meta.get('EventID', '')

                # Construct Full Title: "CQ-WW-CW 2024" or "NAQP 2025 JAN"
                full_contest_title = f"{contest_name.replace('_', ' ')} {year} {event_id}".strip()

                # Extract CTY Version Info
                cty_path = lm.logs[0].cty_dat_path
                cty_date = CtyLookup.extract_version_date(cty_path)
                cty_date_str = cty_date.strftime('%Y-%m-%d') if cty_date else "Unknown Date"
                cty_filename = os.path.basename(cty_path)
                cty_version_info = f"{cty_filename} ({cty_date_str})"
                
                all_calls = sorted([l.get_metadata().get('MyCall', f'Log{i+1}') for i, l in enumerate(lm.logs)])
                combo_id = '_'.join(all_calls)

                # Construct safe URL path by filtering out empty components (e.g. empty event_id)
                path_components = [year, contest_name, event_id, combo_id]
                report_url_path = "/".join([str(p) for p in path_components if p])

                # Protocol 3.5: Construct Standardized Filenames <report_id>_<callsigns>.<ext>
                # Note: 'qso_rate' is the ID for the main plot report.
                animation_filename = f"interactive_animation_{combo_id}.html"
                plot_filename = f"qso_rate_{combo_id}.html"
                mult_filename = f"missed_multipliers_{combo_id}.txt"

                context = {
                    'session_key': session_key,
                    'report_url_path': report_url_path,
                    'animation_file': animation_filename,
                    'plot_file': plot_filename,
                    'mult_file': mult_filename,
                    'logs': [],
                    'mult_headers': [],
                    'full_contest_title': full_contest_title,
                    'cty_version_info': cty_version_info,
                }
                
                # Determine multiplier headers from the first log (assuming all are same contest)
                if ts_data['logs']:
                    first_log_key = list(ts_data['logs'].keys())[0]
                    if 'mult_breakdown' in ts_data['logs'][first_log_key]['scalars']:
                        context['mult_headers'] = list(ts_data['logs'][first_log_key]['scalars']['mult_breakdown'].keys())

                for call, data in ts_data['logs'].items():
                    context['logs'].append({
                        'callsign': call,
                        'score': data['scalars'].get('final_score', 0),
                        'qsos': data['scalars']['net_qsos'],
                        'mults': data['scalars'].get('mult_breakdown', {}),
                        'run_qsos': data['scalars'].get('run_qsos', 0),
                        'run_percent': data['scalars'].get('run_percent', 0.0)
                    })

                return render(request, 'analyzer/dashboard.html', context)

            except Exception as e:
                logger.exception("Log analysis failed")
                return render(request, 'analyzer/home.html', {'form': form, 'error': str(e)})
    
    return redirect('home')