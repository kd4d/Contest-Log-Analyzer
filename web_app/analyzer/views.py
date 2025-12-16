# web_app/analyzer/views.py
#
# Purpose: Django views for the Contest Log Analyzer application.
#          Handles log file uploads, invokes the core LogManager for parsing,
#          aggregates data using DAL components, and renders the dashboard.
#
# Author: Gemini AI
# Date: 2025-12-15
# Version: 0.120.0-Beta
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
# [0.120.0-Beta] - 2025-12-15
# - Added `multiplier_dashboard` view to dynamically discover and display
#   multiplier reports in a tabbed interface, resolving 404 errors.
# - Updated `analyze_logs` to remove the fragile `mult_file` context variable.
# [0.119.2-Beta] - 2025-12-15
# - Added `help_about`, `help_dashboard`, and `help_reports` views for static documentation pages.
# [0.119.0-Beta] - 2025-12-15
# - Added `download_all_reports` view to zip and serve the session's 'reports' directory.
# - Added `FileResponse` import and `_sanitize_filename_part` for archive handling.
# [0.117.1-Beta] - 2025-12-15
# - Fixed 404 error for rate sheet comparison in 'qso_dashboard' by correcting filename construction
#   (removed '_vs_' separator to match ReportGenerator output).
# [0.115.0-Beta] - 2025-12-14
# - Fixed 404 errors on Linux/Docker by lowercasing report URL path components
#   to match the filesystem structure created by ReportGenerator.
# [0.114.0-Beta] - 2025-12-14
# - Added `dashboard_view` to load dashboard context from disk, fixing navigation loops.
# - Updated `analyze_logs` to persist context to JSON and redirect to `dashboard_view`.
# - Updated `view_report` to point "Back" links to the persisted dashboard URL.
# [0.113.3-Beta] - 2025-12-14
# - Updated `view_report` to process `chromeless` parameter and improved
#   `dashboard_url` logic for context-aware navigation ("Back to..." link).
# [0.113.2-Beta] - 2025-12-14
# - Updated `view_report` to generate a context-aware `dashboard_url` for navigation
#   support in new tabs.
# [0.113.1-Beta] - 2025-12-14
# - Fixed 404 error for Global QSO Rate Plot by adding missing '_all' suffix
#   to the constructed filename in `qso_dashboard`.
# [0.112.0-Beta] - 2025-12-14
# - Updated `qso_dashboard` to dynamically discover the deep report path.
# - Re-implemented path construction using sanitized, lowercase callsigns to
#   match the standardized report generator output.
# [0.111.4-Beta] - 2025-12-14
# - Fixed 404 errors in 'qso_dashboard' by prepending correct subdirectories
#   (plots/, charts/, text/) to report filenames.
# - Enforced lowercase filenames for all generated report links to ensure
#   compatibility with Linux/Docker filesystems.
# [0.111.0-Beta] - 2025-12-13
# - Implemented 'qso_dashboard' view logic to power the new QSO Reports Sub-Dashboard.
# - Added dynamic session scanning for rate sheets and animation files to build
#   the pairwise strategy context.
# [0.110.0-Beta] - 2025-12-13
# - Implemented "Honest Progress Bar": Added backend logic to track and report
#   analysis status.
# [0.109.5-Beta] - 2025-12-13
# - Reverted diagnostic logging in `view_report`.
# [0.105.1-Beta] - 2025-12-13
# - Replaced ephemeral tempfile storage with session-based storage in MEDIA_ROOT.
# [0.103.0-Beta] - 2025-12-11
# - Initial creation for Phase 3.

import os
import shutil
import logging
import uuid
import json
import time
from django.shortcuts import render, redirect, reverse
from django.http import Http404, JsonResponse, FileResponse
from django.conf import settings
from .forms import UploadLogForm

# Import Core Logic
from contest_tools.log_manager import LogManager
from contest_tools.data_aggregators.time_series import TimeSeriesAggregator
from contest_tools.report_generator import ReportGenerator
from contest_tools.core_annotations import CtyLookup
from contest_tools.reports._report_utils import _sanitize_filename_part

logger = logging.getLogger(__name__)

def _cleanup_old_sessions(max_age_seconds=3600):
    """Lazy cleanup: Deletes session directories older than 1 hour."""
    sessions_root = os.path.join(settings.MEDIA_ROOT, 'sessions')
    if not os.path.exists(sessions_root):
        return

    now = time.time()
    
    # Cleanup progress files too
    progress_root = os.path.join(settings.MEDIA_ROOT, 'progress')
    if os.path.exists(progress_root):
        for item in os.listdir(progress_root):
            item_path = os.path.join(progress_root, item)
            try:
                if os.stat(item_path).st_mtime < (now - max_age_seconds):
                    os.remove(item_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup progress file {item}: {e}")

    for item in os.listdir(sessions_root):
        item_path = os.path.join(sessions_root, item)
        if os.path.isdir(item_path):
            try:
                if os.stat(item_path).st_mtime < (now - max_age_seconds):
                    shutil.rmtree(item_path)
                    logger.info(f"Cleaned up old session: {item}")
            except Exception as e:
                logger.warning(f"Failed to cleanup session {item}: {e}")

def _update_progress(request_id, step):
    """Writes the current progress step to a transient JSON file."""
    if not request_id:
        return
    
    progress_dir = os.path.join(settings.MEDIA_ROOT, 'progress')
    os.makedirs(progress_dir, exist_ok=True)
    
    file_path = os.path.join(progress_dir, f"{request_id}.json")
    with open(file_path, 'w') as f:
        json.dump({'step': step}, f)

def home(request):
    form = UploadLogForm()
    return render(request, 'analyzer/home.html', {'form': form})

def analyze_logs(request):
    if request.method == 'POST':
        _cleanup_old_sessions()  # Trigger lazy cleanup
        
        # Retrieve the request_id from the form to track progress
        request_id = request.POST.get('request_id')
        _update_progress(request_id, 1) # Step 1: Uploading (Done, moving to Parsing)

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
                
                _update_progress(request_id, 2) # Step 2: Parsing
                lm = LogManager()
                # Load logs (auto-detect contest type)
                lm.load_log_batch(log_paths, root_input, 'after')

                lm.finalize_loading(session_path)

                # 4. Generate Physical Reports (Drill-Down Assets)
                _update_progress(request_id, 3) # Step 3: Aggregating
                
                # Note: ReportGenerator implicitly aggregates if needed, but we treat it as the bridge
                # Step 4: Generating
                _update_progress(request_id, 4) 
                
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

                # Construct safe URL path (LOWERCASE to match ReportGenerator's disk output)
                path_components = [year, contest_name.lower(), event_id.lower(), combo_id.lower()]
                report_url_path = "/".join([str(p) for p in path_components if p])

                # Protocol 3.5: Construct Standardized Filenames <report_id>_<callsigns>.<ext>
                # CRITICAL: Filenames on disk are lowercased by ReportGenerator. We must match that.
                animation_filename = f"interactive_animation_{combo_id.lower()}.html"
                plot_filename = f"qso_rate_{combo_id.lower()}.html"
                
                # Note: Multiplier filename removed here. It is now dynamically resolved in multiplier_dashboard view.

                context = {
                    'session_key': session_key,
                    'report_url_path': report_url_path,
                    'animation_file': animation_filename,
                    'plot_file': plot_filename,
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

                # --- Session Persistence (Fix Navigation Loop) ---
                # Save the context to disk so it can be reloaded via GET request
                context_path = os.path.join(session_path, 'dashboard_context.json')
                with open(context_path, 'w') as f:
                    json.dump(context, f)

                _update_progress(request_id, 5) # Step 5: Finalizing/Ready
                return redirect('dashboard_view', session_id=session_key)

            except Exception as e:
                logger.exception("Log analysis failed")
                return render(request, 'analyzer/home.html', {'form': form, 'error': str(e)})
    
    return redirect('home')

def dashboard_view(request, session_id):
    """Persisted view of the main dashboard, loaded from session JSON."""
    session_path = os.path.join(settings.MEDIA_ROOT, 'sessions', session_id)
    context_path = os.path.join(session_path, 'dashboard_context.json')

    if not os.path.exists(context_path):
        return redirect('home') # Session expired or invalid

    with open(context_path, 'r') as f:
        context = json.load(f)
    
    return render(request, 'analyzer/dashboard.html', context)

def get_progress(request, request_id):
    """Returns the current progress step for the given request ID."""
    file_path = os.path.join(settings.MEDIA_ROOT, 'progress', f"{request_id}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
        return JsonResponse(data)
    return JsonResponse({'step': 0})

def view_report(request, session_id, file_path):
    """
    Wraps a generated report file in the application shell (header/footer).
    Supports 'chromeless' mode for iframe embedding and context-aware 'Back' links.
    """

    # Security Check: Verify file exists within the session
    abs_path = os.path.join(settings.MEDIA_ROOT, 'sessions', session_id, file_path)
    
    if not os.path.exists(abs_path):
        raise Http404("Report not found")

    # Extract query params
    source = request.GET.get('source')
    is_chromeless = request.GET.get('chromeless') == '1'

    # Determine Back Button Logic
    if source == 'main':
        back_label = "Back to Main Dashboard"
        back_url = reverse('dashboard_view', args=[session_id])
    elif source == 'qso':
        back_label = "Back to QSO Dashboard"
        back_url = f"/report/{session_id}/dashboard/qso/"
    elif source == 'mult':
        back_label = "Back to Multiplier Dashboard"
        back_url = f"/report/{session_id}/dashboard/multipliers/"
    else:
        back_label = "Back to Dashboard"
        back_url = reverse('dashboard_view', args=[session_id])

    context = {
        'iframe_src': f"{settings.MEDIA_URL}sessions/{session_id}/{file_path}",
        'filename': os.path.basename(file_path),
        'back_label': back_label,
        'back_url': back_url,
        'chromeless': is_chromeless
    }
    return render(request, 'analyzer/report_viewer.html', context)

def multiplier_dashboard(request, session_id):
    """
    Renders the dedicated Multiplier Reports Sub-Dashboard.
    Dynamically discovers and groups multiplier reports by type (Zones, Countries, etc.).
    """
    session_path = os.path.join(settings.MEDIA_ROOT, 'sessions', session_id)
    if not os.path.exists(session_path):
        raise Http404("Session not found")

    # 1. Discover the "Deep Path" to reports
    report_rel_path = ""
    combo_id = ""
    for root, dirs, filenames in os.walk(session_path):
        for f in filenames:
            if f.startswith('interactive_animation_') and f.endswith('.html'):
                combo_id = f.replace('interactive_animation_', '').replace('.html', '')
                full_dir = os.path.dirname(os.path.join(root, f)) # .../animations
                parent_dir = os.path.dirname(full_dir) # .../
                report_rel_path = os.path.relpath(parent_dir, session_path)
                break
        if combo_id: break
    
    if not report_rel_path:
        raise Http404("Analysis data structure not found")

    text_dir = os.path.join(session_path, report_rel_path, 'text')
    if not os.path.exists(text_dir):
        raise Http404("No text reports found")

    # 2. Scan and Group Reports
    # Expected format: missed_multipliers_{TYPE}_{COMBO_ID}.txt
    # We strip prefix and suffix to find {TYPE}.
    
    suffix = f"_{combo_id}.txt"
    multipliers = {}

    for filename in os.listdir(text_dir):
        if not filename.endswith(suffix):
            continue
        
        mult_type = None
        if filename.startswith('missed_multipliers_'):
            mult_type = filename.replace('missed_multipliers_', '').replace(suffix, '').replace('_', ' ').title()
            report_key = 'missed'
        elif filename.startswith('multiplier_summary_'):
            mult_type = filename.replace('multiplier_summary_', '').replace(suffix, '').replace('_', ' ').title()
            report_key = 'summary'
        
        if mult_type:
            if mult_type not in multipliers:
                multipliers[mult_type] = {'label': mult_type, 'missed': None, 'summary': None}
            
            # Store relative path for template
            file_rel_path = os.path.join(report_rel_path, 'text', filename)
            multipliers[mult_type][report_key] = file_rel_path

    # Convert dict to sorted list for template
    sorted_mults = sorted(multipliers.values(), key=lambda x: x['label'])

    context = {
        'session_id': session_id,
        'multipliers': sorted_mults,
    }
    return render(request, 'analyzer/multiplier_dashboard.html', context)

def qso_dashboard(request, session_id):
    """Renders the dedicated QSO Reports Sub-Dashboard."""
    session_path = os.path.join(settings.MEDIA_ROOT, 'sessions', session_id)
    if not os.path.exists(session_path):
        raise Http404("Session not found")

    # 1. Discover the "Deep Path"
    report_rel_path = ""
    combo_id = ""
    
    for root, dirs, filenames in os.walk(session_path):
        for f in filenames:
            if f.startswith('interactive_animation_') and f.endswith('.html'):
                combo_id = f.replace('interactive_animation_', '').replace('.html', '')
                full_dir = os.path.dirname(os.path.join(root, f)) # .../animations
                parent_dir = os.path.dirname(full_dir) # .../
                report_rel_path = os.path.relpath(parent_dir, session_path)
                break
        if combo_id: break
    
    if not combo_id:
        raise Http404("Analysis data not found")

    # 2. Re-construct Callsigns from the combo_id
    callsigns_safe = combo_id.split('_')
    callsigns_display = [c.upper() for c in callsigns_safe]
    
    # 3. Identify Pairs for Strategy Tab
    import itertools
    pairs = list(itertools.combinations(callsigns_safe, 2))
    
    matchups = []
    for p in pairs:
        c1, c2 = sorted(p)
        label = f"{c1.upper()} vs {c2.upper()}"
        base_path = report_rel_path
        
        matchups.append({
            'label': label,
            'id': f"{c1}_{c2}",
            'qso_breakdown_file': os.path.join(base_path, f"charts/qso_breakdown_chart_{c1}_{c2}.html"),
            'diff_plot_file': os.path.join(base_path, f"plots/cumulative_difference_plots_qsos_all_{c1}_{c2}.html"),
            'band_activity_file': os.path.join(base_path, f"plots/comparative_band_activity_{c1}_{c2}.html"),
            'continent_file': os.path.join(base_path, f"text/comparative_continent_summary_{c1}_{c2}.txt")
        })

    context = {
        'session_id': session_id,
        'callsigns': callsigns_display,
        'matchups': matchups,
        # Global Files
        'global_qso_rate_file': os.path.join(report_rel_path, f"plots/qso_rate_plots_all_{combo_id}.html"),
        'global_point_rate_file': os.path.join(report_rel_path, f"plots/point_rate_plots_all_{combo_id}.html"),
        'rate_sheet_comparison': os.path.join(report_rel_path, f"text/rate_sheet_comparison_{'_'.join(sorted(callsigns_safe))}.txt"),
        'report_base': os.path.join(report_rel_path) # Pass base path for template filters
    }
    
    return render(request, 'analyzer/qso_dashboard.html', context)

def download_all_reports(request, session_id):
    """
    Zips the entire 'reports' directory for the session and serves it as a download.
    Filename format: YYYY_CONTEST_NAME.zip
    """
    session_path = os.path.join(settings.MEDIA_ROOT, 'sessions', session_id)
    context_path = os.path.join(session_path, 'dashboard_context.json')

    if not os.path.exists(session_path) or not os.path.exists(context_path):
        raise Http404("Session or context not found")

    # 1. Get Metadata for Filename
    try:
        with open(context_path, 'r') as f:
            context = json.load(f)
        
        # report_url_path format: "YYYY/contest_name/event/calls"
        path_parts = context.get('report_url_path', '').split('/')
        if len(path_parts) >= 2:
            year = _sanitize_filename_part(path_parts[0])
            contest = _sanitize_filename_part(path_parts[1])
            zip_filename = f"{year}_{contest}.zip"
        else:
            zip_filename = "contest_reports.zip"
    except Exception:
        zip_filename = "contest_reports.zip"

    # 2. Create Zip Archive
    # We zip 'reports' directory relative to session_path to avoid recursive loops
    reports_root = os.path.join(session_path, 'reports')
    if not os.path.exists(reports_root):
        raise Http404("No reports found to archive")

    # Output zip path (stored in session root, not inside reports!)
    zip_output_base = os.path.join(session_path, 'archive_temp')
    
    try:
        # make_archive appends .zip automatically
        archive_path = shutil.make_archive(
            base_name=zip_output_base,
            format='zip',
            root_dir=session_path,
            base_dir='reports'
        )
        
        # 3. Serve File
        response = FileResponse(open(archive_path, 'rb'), as_attachment=True, filename=zip_filename)
        return response
    except Exception as e:
        logger.error(f"Failed to zip reports: {e}")
        raise Http404("Failed to generate archive")

def help_about(request):
    """Renders the About / Intro page."""
    return render(request, 'analyzer/about.html')

def help_dashboard(request):
    """Renders the Dashboard Help page."""
    return render(request, 'analyzer/help_dashboard.html')

def help_reports(request):
    """Renders the Report Interpretation Guide."""
    return render(request, 'analyzer/help_reports.html')