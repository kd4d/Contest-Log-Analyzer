# web_app/analyzer/views.py
#
# Purpose: Django views for the Contest Log Analyzer application.
#          Handles log file uploads, invokes the core LogManager for parsing,
#          aggregates data using DAL components, and renders the dashboard.
#
# Author: Gemini AI
# Date: 2025-12-22
# Version: 0.138.8-Beta
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
# [0.138.8-Beta] - 2025-12-22
# - Removed temporary diagnostic `print` statements from `multiplier_dashboard` (Cleanup).
# [0.138.6-Beta] - 2025-12-22
# - Replaced logger.info with print() for "Force Diagnostic Output" strategy to bypass Django logging filters.
# [0.138.5-Beta] - 2025-12-22
# - Injected temporary diagnostic logging to trace JSON artifact discovery in `multiplier_dashboard`.
# [0.138.0-Beta] - 2025-12-22
# - Implemented "Write Once, Read Many" (WORM) strategy for Multiplier Dashboard using JSON artifacts.
# [0.137.0-Beta] - 2025-12-22
# - Updated `multiplier_dashboard` to discover and serve the new HTML breakdown report.
# - Updated `multiplier_dashboard` to retrieve and pass `full_contest_title` to the context.
# [0.136.4-Beta] - 2025-12-20
# - Fixed UnboundLocalError in multiplier_dashboard by hoisting suffix definition.
# [0.136.2-Beta] - 2025-12-20
# - Updated `multiplier_dashboard` to discover and link `text_multiplier_breakdown` report.
# [0.136.1-Beta] - 2025-12-20
# - Updated `qso_dashboard` to recursively search for `session_manifest.json` and prepend relative paths to artifacts.
# [0.136.0-Beta] - 2025-12-20
# - Integrated ManifestManager into `qso_dashboard` to replace fragile filesystem walking.
# - Updated report discovery logic to rely on the session manifest for reliability.
# [0.135.2-Beta] - 2025-12-20
# - Fixed Dashboard Band Sorting: Normalized numeric band names (e.g., '160') to match sort keys (e.g., '160M') in plot discovery loops.
# [0.135.1-Beta] - 2025-12-20
# - Refactored `qso_dashboard` to hoist `BAND_SORT_ORDER` to function scope for consistency.
# [0.135.0-Beta] - 2025-12-20
# - Updated `qso_dashboard` to discover 'Cumulative Rates' plots (qso_rate_plots_*) for the new dashboard tab.
# [0.133.1-Beta] - 2025-12-20
# - Restored "All Bands" button in QSO Dashboard by removing suppression logic.
# [0.132.0-Beta] - 2025-12-20
# - Injected pipeline diagnostics to trace log handoff and file generation state.
# [0.129.1-Beta] - 2025-12-19
# - Fixed Rate Differential plot linking by using raw band name in directory path.
# [0.129.0-Beta] - 2025-12-19
# - Updated `qso_dashboard` to support band-specific Drill-Down for Rate Differential plots.
# - Enforced sort order for Diff Bands (160 -> 10 -> All).
# [0.128.0-Beta] - 2025-12-19
# - Updated `qso_dashboard` to filter out "All Bands" plot.
# - Updated `qso_dashboard` to set 20M as the default active tab.
# [0.127.2-Beta] - 2025-12-19
# - Injected diagnostic logging into `qso_dashboard` to trace `point_rate_plots` discovery.
# [0.127.1-Beta] - 2025-12-19
# - Updated `qso_dashboard` to use `os.walk` instead of `os.listdir` to
#   recursively discover Point Rate Plots in subdirectories (e.g., plots/20M/).
# [0.127.0-Beta] - 2025-12-19
# - Updated `qso_dashboard` to discover and list Point Rate Plots for all bands,
#   restoring the Drill-Down functionality to the Points tab.
# [0.126.2-Beta] - 2025-12-19
# - Removed Correlation Analysis report context to prevent loading.
# [0.126.1-Beta] - 2025-12-19
# - Fixed filename construction for Global QSO Rate plot in `analyze_logs` (added missing `_plots_all` segment).
# - Updated `analyze_logs` to register `plot_correlation_analysis` report.
# - Updated `qso_dashboard` to detect solo mode and suppress pairwise matchups.
# - Updated `multiplier_dashboard` to map 'summary' matrix to 'missed' slot in solo mode.
# [0.126.0-Beta] - 2025-12-18
# - Implemented `get_log_index_view` to expose log fetcher API.
# - Refactored `analyze_logs` to support both manual uploads and public archive fetching.
# - Extracted `_run_analysis_pipeline` to share processing logic between upload and fetch modes.
# [0.125.2-Beta] - 2025-12-17
# - Fixed IndentationError in `_cleanup_old_sessions`.
# [0.125.1-Beta] - 2025-12-17
# - Updated `multiplier_dashboard` view to consume structured breakdown data
#   (totals/bands) and split bands into low/high groups for responsive layout.
# [0.124.0-Beta] - 2025-12-17
# - Updated `multiplier_dashboard` to consume hierarchical `breakdown_rows`
#   instead of the legacy `matrix_data`.
# [0.124.1-Beta] - 2025-12-17
# - Updated `multiplier_dashboard` view to calculate and pass `col_width` for Bootstrap grid.
# [0.124.0-Beta] - 2025-12-17
# - Updated `multiplier_dashboard` to hydrate live data for the Opportunity Matrix.
# [0.121.0-Beta] - 2025-12-16
# - Updated `analyze_logs` to pass raw `contest_name` to dashboard context.
# - Updated `dashboard_view` to route non-CQ-WW contests to a construction page.
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
#   (plots/, charts/, text/) to report filenames.
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
#   (Note: This previous fix was incomplete or regressed; re-applying correctly in 0.126.1).
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
import re
import json
import time
from django.shortcuts import render, redirect, reverse
from django.http import Http404, JsonResponse, FileResponse
from django.conf import settings
from .forms import UploadLogForm

# Import Core Logic
from contest_tools.log_manager import LogManager
from contest_tools.data_aggregators.time_series import TimeSeriesAggregator
from contest_tools.data_aggregators.multiplier_stats import MultiplierStatsAggregator
from contest_tools.report_generator import ReportGenerator
from contest_tools.core_annotations import CtyLookup
from contest_tools.reports._report_utils import _sanitize_filename_part
from contest_tools.utils.log_fetcher import fetch_log_index, download_logs
from contest_tools.manifest_manager import ManifestManager

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

def get_log_index_view(request):
    """API Endpoint: Returns list of available callsigns for Year/Mode."""
    contest = request.GET.get('contest')
    year = request.GET.get('year')
    mode = request.GET.get('mode')
    
    if contest == 'CQ-WW' and year and mode:
        try:
            callsigns = fetch_log_index(year, mode)
            return JsonResponse({'callsigns': callsigns})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'callsigns': []})

def home(request):
    form = UploadLogForm()
    return render(request, 'analyzer/home.html', {'form': form})

def analyze_logs(request):
    if request.method == 'POST':
        _cleanup_old_sessions() # Trigger lazy cleanup
        
        # Retrieve the request_id from the form to track progress
        request_id = request.POST.get('request_id')
        _update_progress(request_id, 1) # Step 1: Uploading (Done, moving to Parsing)

        # Handle Manual Upload
        if 'log1' in request.FILES:
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

                    return _run_analysis_pipeline(request_id, log_paths, session_path, session_key)
                except Exception as e:
                    logger.exception("Log analysis failed")
                    return render(request, 'analyzer/home.html', {'form': form, 'error': str(e)})
        
        # Handle Public Fetch
        elif 'fetch_callsigns' in request.POST:
            try:
                # 1. Create Session Context
                session_key = str(uuid.uuid4())
                session_path = os.path.join(settings.MEDIA_ROOT, 'sessions', session_key)
                os.makedirs(session_path, exist_ok=True)

                # 2. Fetch Logs
                callsigns_raw = request.POST.get('fetch_callsigns') # JSON string
                year = request.POST.get('fetch_year')
                mode = request.POST.get('fetch_mode')
                
                callsigns = json.loads(callsigns_raw)
                
                _update_progress(request_id, 1) # Step 1: Fetching
                log_paths = download_logs(callsigns, year, mode, session_path)
                
                return _run_analysis_pipeline(request_id, log_paths, session_path, session_key)
            except Exception as e:
                logger.exception("Public log fetch failed")
                return render(request, 'analyzer/home.html', {'form': UploadLogForm(), 'error': str(e)})
        
    return redirect('home')

def _run_analysis_pipeline(request_id, log_paths, session_path, session_key):
    """Shared logic for processing logs (Manual or Fetched)."""
    # 3. Process with LogManager
    # Note: We rely on docker-compose env vars for CONTEST_INPUT_DIR
    root_input = os.environ.get('CONTEST_INPUT_DIR', '/app/CONTEST_LOGS_REPORTS')
    
    _update_progress(request_id, 2) # Step 2: Parsing
    lm = LogManager()
    # Load logs (auto-detect contest type)
    lm.load_log_batch(log_paths, root_input, 'after')

    lm.finalize_loading(session_path)

    # --- DIAGNOSTIC: Validate Handoff ---
    valid_count = 0
    for log in lm.logs:
        if not log.get_processed_data().empty:
            valid_count += 1
    logger.info(f"Pipeline Diagnostic: Loaded {len(lm.logs)} logs. Valid (Non-Empty): {valid_count}.")
    # ------------------------------------

    # 4. Generate Physical Reports (Drill-Down Assets)
    _update_progress(request_id, 3) # Step 3: Aggregating
    
    # Note: ReportGenerator implicitly aggregates if needed, but we treat it as the bridge
    # Step 4: Generating
    _update_progress(request_id, 4) 
    
    generator = ReportGenerator(lm.logs, root_output_dir=session_path)
    generator.run_reports('all')
    
    # --- DIAGNOSTIC: Verify Disk State ---
    generated_files = []
    for root, dirs, files in os.walk(session_path):
        for file in files:
            if file.endswith('.html') or file.endswith('.png'):
                generated_files.append(file)
    logger.info(f"Pipeline Diagnostic: Generated {len(generated_files)} artifacts on disk: {generated_files}")
    # -------------------------------------
    
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
    plot_filename = f"qso_rate_plots_all_{combo_id.lower()}.html"
    
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
        'contest_name': contest_name,
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

def dashboard_view(request, session_id):
    """Persisted view of the main dashboard, loaded from session JSON."""
    session_path = os.path.join(settings.MEDIA_ROOT, 'sessions', session_id)
    context_path = os.path.join(session_path, 'dashboard_context.json')

    if not os.path.exists(context_path):
        return redirect('home') # Session expired or invalid

    with open(context_path, 'r') as f:
        context = json.load(f)

    # Contest-Specific Routing
    contest_name = context.get('contest_name', '').upper()
    if not contest_name.startswith('CQ-WW'):
        return render(request, 'analyzer/dashboard_construction.html', context)
    
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
    Dynamically discovers and display multiplier reports in a tabbed interface.
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

    # 3. Data Hydration Strategy
    breakdown_data = None

    # Strategy A: Fast Load (JSON Artifact)
    # Look for the JSON file generated by json_multiplier_breakdown.py
    json_prefix = "json_multiplier_breakdown_"
    
    if os.path.exists(text_dir):
        for f in os.listdir(text_dir):
            if f.startswith(json_prefix) and f.endswith(".json"):
                try:
                    with open(os.path.join(text_dir, f), 'r') as json_file:
                        breakdown_data = json.load(json_file)
                    break 
                except Exception as e:
                    logger.error(f"Failed to load JSON artifact {f}: {e}")

    # Strategy B: Slow Fallback (Live Hydration)
    # Only runs if JSON artifact is missing
    if not breakdown_data:
        # We must reload logs to perform live aggregation
        # Note: We rely on the session directory containing the source logs
        lm = LogManager()
        # Find log files in session root (excluding directories and known generated files)
        log_candidates = []
        for f in os.listdir(session_path):
            f_path = os.path.join(session_path, f)
            if os.path.isfile(f_path) and not f.startswith('dashboard_context') and not f.endswith('.zip'):
                log_candidates.append(f_path)
        
        # Load without progress tracking (fast for reload)
        root_input = os.environ.get('CONTEST_INPUT_DIR', '/app/CONTEST_LOGS_REPORTS')
        lm.load_log_batch(log_candidates, root_input, 'after')
        
        # Aggregate Matrix
        mult_agg = MultiplierStatsAggregator(lm.logs)
        breakdown_data = mult_agg.get_multiplier_breakdown_data()

        # Aggregate Scoreboard (Simple scalars)
        # Note: This is dead code when using JSON path, but required for fallback context
        scoreboard = []
        for log in lm.logs:
            meta = log.get_metadata()
            df = log.get_processed_data()
            scoreboard.append({
                'call': meta.get('MyCall', 'Unknown'),
                'qsos': len(df),
                'zones': len(df['Zone'].unique()) if 'Zone' in df.columns else 0, # Approx
                'countries': len(df['Country'].unique()) if 'Country' in df.columns else 0 # Approx
            })
    
    # Split Bands for Layout
    low_bands = ['160M', '80M', '40M']
    low_bands_data = []
    high_bands_data = []
    
    for block in breakdown_data['bands']:
        if block['label'] in low_bands:
            low_bands_data.append(block)
        else:
            high_bands_data.append(block)
    
    # Re-fetch persisted context for accurate scores (since LM reload is raw)
    context_path = os.path.join(session_path, 'dashboard_context.json')
    persisted_logs = []
    full_contest_title = ""
    if os.path.exists(context_path):
        with open(context_path, 'r') as f:
            d_ctx = json.load(f)
            persisted_logs = d_ctx.get('logs', [])
            full_contest_title = d_ctx.get('full_contest_title', '')

    # Calculate optimal column width for scoreboard
    log_count = len(persisted_logs) if persisted_logs else 0
    col_width = 12 // log_count if log_count > 0 else 12

    # Common suffix for text reports
    suffix = f"_{combo_id}.txt"

    # 4. Discover Text Version of Breakdown
    breakdown_txt_rel_path = None
    txt_breakdown_prefix = "text_multiplier_breakdown_"
    for filename in os.listdir(text_dir):
        if filename.startswith(txt_breakdown_prefix) and filename.endswith(suffix):
            breakdown_txt_rel_path = os.path.join(report_rel_path, 'text', filename)
            break

    # 5. Discover HTML Version of Breakdown
    breakdown_html_rel_path = None
    html_breakdown_prefix = "html_multiplier_breakdown_"
    html_suffix = f"_{combo_id}.html"
    # HTML reports are in the root report dir, not text/
    report_abs_path = os.path.join(session_path, report_rel_path)
    if os.path.exists(report_abs_path):
        for filename in os.listdir(report_abs_path):
            if filename.startswith(html_breakdown_prefix) and filename.endswith(html_suffix):
                breakdown_html_rel_path = os.path.join(report_rel_path, filename)
                break

    # 2. Scan and Group Reports
    # Expected format: missed_multipliers_{TYPE}_{COMBO_ID}.txt
    # We strip prefix and suffix to find {TYPE}.
    multipliers = {}

    # In Solo Mode, we show 'multiplier_summary' (The Matrix) instead of 'missed_multipliers'
    # We map it to the 'missed' key so the template renders it in the card slot.
    target_prefix = 'multiplier_summary_' if log_count == 1 else 'missed_multipliers_'

    for filename in os.listdir(text_dir):
        if not filename.endswith(suffix):
            continue
        
        mult_type = None
        if filename.startswith(target_prefix):
            mult_type = filename.replace(target_prefix, '').replace(suffix, '').replace('_', ' ').title()
            report_key = 'missed' # Hijack 'missed' slot for display
        elif filename.startswith('multiplier_summary_') and log_count > 1:
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
        'scoreboard': persisted_logs, # Use persisted logs for accurate scores
        'col_width': col_width,
        'breakdown_totals': breakdown_data['totals'],
        'low_bands_data': low_bands_data,
        'high_bands_data': high_bands_data,
        'all_calls': sorted([l['callsign'] for l in persisted_logs]),
        'breakdown_txt_url': breakdown_txt_rel_path,
        'breakdown_html_url': breakdown_html_rel_path,
        'full_contest_title': full_contest_title,
        'multipliers': sorted_mults,
        'is_solo': (log_count == 1),
    }
    return render(request, 'analyzer/multiplier_dashboard.html', context)

def qso_dashboard(request, session_id):
    """Renders the dedicated QSO Reports Sub-Dashboard."""
    session_path = os.path.join(settings.MEDIA_ROOT, 'sessions', session_id)
    if not os.path.exists(session_path):
        raise Http404("Session not found")

    # 1. Discover Manifest (Deep Search)
    manifest_dir = None
    for root, dirs, files in os.walk(session_path):
        if 'session_manifest.json' in files:
            manifest_dir = root
            break
    
    if not manifest_dir:
        raise Http404("Analysis manifest not found")

    # 2. Load Manifest & Calculate Relative Path
    manifest_mgr = ManifestManager(manifest_dir)
    artifacts = manifest_mgr.load()
    
    combo_id = ""
    # Find combo_id from animation file in manifest
    for art in artifacts:
        if art['report_id'] == 'interactive_animation' and art['path'].endswith('.html'):
            filename = os.path.basename(art['path'])
            combo_id = filename.replace('interactive_animation_', '').replace('.html', '')
            break
    
    if not combo_id:
        raise Http404("Analysis data not found")

    # Calculate relative path segment (e.g., "reports/2024/...") to prepend to artifact paths
    report_rel_path = os.path.relpath(manifest_dir, session_path).replace("\\", "/")

    # 2. Re-construct Callsigns from the combo_id
    callsigns_safe = combo_id.split('_')
    callsigns_display = [c.upper() for c in callsigns_safe]
    is_solo = (len(callsigns_safe) == 1)
    BAND_SORT_ORDER = {'ALL': 0, '160M': 1, '80M': 2, '40M': 3, '20M': 4, '15M': 5, '10M': 6, '6M': 7, '2M': 8}
    
    # 3. Identify Pairs for Strategy Tab
    matchups = []
    # Requested Sort Order for Diff Plots
    DIFF_BANDS = ['160M', '80M', '40M', '20M', '15M', '10M', 'ALL']

    if not is_solo:
        import itertools
        pairs = list(itertools.combinations(callsigns_safe, 2))
        
        for p in pairs:
            c1, c2 = sorted(p)
            label = f"{c1.upper()} vs {c2.upper()}"
            
            # Discover available band variants for the diff plot via Manifest
            diff_paths = {}
            
            # Filter artifacts for this pair's difference plots
            target_prefix = f"cumulative_difference_plots_qsos_"
            target_suffix = f"_{c1}_{c2}.html"
            
            for art in artifacts:
                if art['report_id'] == 'cumulative_difference_plots' and art['path'].endswith(target_suffix):
                    # Extract band from filename: cumulative_difference_plots_qsos_{BAND}_{c1}_{c2}.html
                    fname = os.path.basename(art['path'])
                    # Remove prefix and suffix to isolate band
                    band_part = fname.replace(target_prefix, '').replace(target_suffix, '')
                    # band_part is roughly {band_slug}
                    # Prepend report_rel_path to ensure view_report can find it
                    diff_paths[band_part] = f"{report_rel_path}/{art['path']}"
        
            
            # Find breakdown chart
            bk_path = next((f"{report_rel_path}/{a['path']}" for a in artifacts if a['report_id'] == 'qso_breakdown_chart' and f"_{c1}_{c2}" in a['path']), "")
            ba_path = next((f"{report_rel_path}/{a['path']}" for a in artifacts if a['report_id'] == 'comparative_band_activity' and f"_{c1}_{c2}" in a['path']), "")
            cont_path = next((f"{report_rel_path}/{a['path']}" for a in artifacts if a['report_id'] == 'comparative_continent_summary' and f"_{c1}_{c2}" in a['path']), "")

            matchups.append({
                'label': label,
                'id': f"{c1}_{c2}",
                'diff_paths': diff_paths,
                'qso_breakdown_file': bk_path,
                'band_activity_file': ba_path,
                'continent_file': cont_path
            })

    # 4. Discover Point Rate Plots (Manifest Scan)
    point_plots = []

    for art in artifacts:
        if art['report_id'] == 'point_rate_plots' and art['path'].endswith('.html'):
            fname = os.path.basename(art['path'])
            # point_rate_plots_{band}_{calls}.html
            # Remove prefix
            remainder = fname.replace('point_rate_plots_', '')
            parts = remainder.split('_')
            if parts:
                band_key = parts[0].upper()
                if band_key.isdigit(): band_key += 'M'
                
                label = "All Bands" if band_key == 'ALL' else band_key
                sort_val = BAND_SORT_ORDER.get(band_key, 99)
                
                point_plots.append({
                    'label': label,
                    'file': f"{report_rel_path}/{art['path']}",
                    'sort_val': sort_val
                })
    
    # Sort by band order
    point_plots.sort(key=lambda x: x['sort_val'])
    
    # Default active to 20M, fallback to first available
    active_set = False
    if point_plots:
        for p in point_plots:
            if p['label'] == '20M':
                p['active'] = True
                active_set = True
                break
        if not active_set:
            point_plots[0]['active'] = True

    # 5. Discover QSO Rate Plots (Manifest Scan)
    qso_band_plots = []
    for art in artifacts:
        if art['report_id'] == 'qso_rate_plots' and art['path'].endswith('.html'):
            fname = os.path.basename(art['path'])
            remainder = fname.replace('qso_rate_plots_', '')
            parts = remainder.split('_')
            if parts:
                band_key = parts[0].upper()
                if band_key.isdigit(): band_key += 'M'
                if band_key == 'ALL': continue
                
                label = band_key
                sort_val = BAND_SORT_ORDER.get(band_key, 99)
                
                qso_band_plots.append({
                    'label': label,
                    'file': f"{report_rel_path}/{art['path']}",
                    'sort_val': sort_val
                })

    qso_band_plots.sort(key=lambda x: x['sort_val'])
    
    # Default active to 20M for consistency
    active_set = False
    if qso_band_plots:
        for p in qso_band_plots:
            if p['label'] == '20M':
                p['active'] = True
                active_set = True
                break
        if not active_set:
            qso_band_plots[0]['active'] = True

    # Global files via manifest lookup
    global_qso = next((f"{report_rel_path}/{a['path']}" for a in artifacts if a['report_id'] == 'qso_rate_plots' and '_all_' in a['path']), "")
    rate_sheet_comp = next((f"{report_rel_path}/{a['path']}" for a in artifacts if a['report_id'] == 'rate_sheet_comparison'), "")
    
    report_base = os.path.dirname(os.path.dirname(global_qso)) if global_qso else ""

    context = {
        'session_id': session_id,
        'callsigns': callsigns_display,
        'matchups': matchups,
        'point_plots': point_plots,
        'qso_band_plots': qso_band_plots,
        # Global Files
        'global_qso_rate_file': global_qso,
        'rate_sheet_comparison': rate_sheet_comp,
        'report_base': report_base,
        'is_solo': is_solo
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