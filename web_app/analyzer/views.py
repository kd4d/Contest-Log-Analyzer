# web_app/analyzer/views.py
#
# Purpose: Django views for the Contest Log Analyzer application.
#          Handles log file uploads, invokes the core LogManager for parsing,
#          aggregates data using DAL components, and renders the dashboard.
#
# Author: Gemini AI
# Date: 2026-01-07
# Version: 0.160.0-Beta
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
# [0.156.11-Beta] - 2026-01-06
# - Updated 'qso_dashboard' to discover and pass JSON artifacts for the Comparative Activity Butterfly chart.
# [0.156.10-Beta] - 2026-01-05
# - Fixed "Order of Operations" bug in Multiplier Dashboard artifact discovery.
# - Reordered logic to check for Pairwise suffixes (Longest Match) before Single suffixes
#   to prevent partial collisions (e.g., `_a_b` being claimed by `_b`).
# [0.156.9-Beta] - 2026-01-05
# - Implemented 3-Tier Tab Strategy for Multiplier Dashboard (Session, Pairs, Singles).
# - Refactored artifact discovery to categorize reports by suffix.
# [0.156.8-Beta] - 2026-01-05
# - Fixed SyntaxError in `multiplier_dashboard` by correcting indentation of except block.
# [0.156.7-Beta] - 2026-01-05
# - Updated `multiplier_dashboard` to strip individual callsign suffixes from report filenames
#   when the session suffix check fails (fixes display bug for drill-down reports).
# [0.156.6-Beta] - 2026-01-05
# - Fixed 'qso_dashboard' to target 'chart_comparative_activity_butterfly' for comparative band activity.
# [0.156.5-Beta] - 2026-01-05
# - Updated 'qso_dashboard' to strictly target HTML artifacts for comparative band activity.
# [0.156.3-Beta] - 2026-01-05
# - Refactored Multiplier Dashboard to separate "Missed" and "Summary" reports into distinct tabs.
# - Removed legacy Solo Mode logic that re-mapped summary reports to the missed slot.
# [0.156.2-Beta] - 2026-01-01
# - Updated import path for report utilities to `contest_tools.utils.report_utils`
#   to resolve circular dependency.
# [0.156.1-Beta] - 2025-12-31
# - Implemented "Fast Path" hydration for Multiplier Dashboard to bypass LogManager reload.
# - Updated footer generation to support multi-line text (Branding + CTY).
# [0.156.0-Beta] - 2025-12-31
# - Updated `multiplier_dashboard` to use `get_standard_title_lines` and `get_cty_metadata` for
#   standardized report headers/footers (Ghost Injection support).
# - Implemented `report_metadata` dictionary in context, replacing `full_contest_title`.
# [0.152.0-Beta] - 2025-12-30
# - Updated `multiplier_dashboard` to calculate `global_max` scaling factors for normalized charting.
# [Phase 1 (Pathfinder)] - 2025-12-29
# - Updated `qso_dashboard` to pass JSON artifact URLs for Point and QSO rate plots
#   to support JS-based rendering (Chart.js/Plotly) instead of iframes.
# [Phase 1 (Pathfinder)] - 2025-12-29
# - Updated `qso_dashboard` view to discover and pass JSON artifacts for interactive web components.
# [0.140.0-Beta] - 2025-12-25
# - Updated `_update_progress` to use atomic file writes (write to .tmp -> os.replace)
#   to prevent `JSONDecodeError` race conditions on the frontend.
# [0.139.8-Beta] - 2025-12-23
# - Fixed artifact discovery bug in `multiplier_dashboard` where `next()` would return single-log
#   artifacts instead of the combined session artifact.
#   Implemented strict suffix matching using `combo_id`.
# [0.139.7-Beta] - 2025-12-23
# - Refactored `multiplier_dashboard` and `qso_dashboard` to derive `combo_id` directly from
#   the authoritative `session_manifest.json` directory name, removing fragile filename parsing.
# [0.139.6-Beta] - 2025-12-23
# - Refactored `report_base` in `qso_dashboard` to rely on authoritative manifest path rather than file discovery.
# - Added specific diagnostic logging for missing rate sheets in `qso_dashboard`.
# [0.139.4-Beta] - 2025-12-23
# - Added diagnostic logging to `qso_dashboard` to trace missing global rate plots and comparison sheets.
# [0.139.3-Beta] - 2025-12-23
# - Implemented specific ValueError handling in `analyze_logs` to catch quiet validation errors.
# [0.139.2-Beta] - 2025-12-22
# - Fixed shadowing bug in `multiplier_dashboard` loop variable initialization.
# [0.139.1-Beta] - 2025-12-22
# - Fixed Comparative Rate Sheet discovery logic to strictly match full combo_id.
# [0.139.0-Beta] - 2025-12-22
# - Refactored `multiplier_dashboard` to use `ManifestManager` for robust artifact discovery.
# - Removed fragile `os.walk` and `os.listdir` loops from `multiplier_dashboard`.
# - Implemented precise artifact lookup for JSON hydration and report linking.
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
import itertools
import zipfile
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
from contest_tools.utils.report_utils import _sanitize_filename_part, get_standard_title_lines, get_cty_metadata
from contest_tools.version import __version__
from contest_tools.utils.callsign_utils import build_callsigns_filename_part, parse_callsigns_from_filename_part, callsign_to_filename_part
from contest_tools.utils.log_fetcher import fetch_log_index, download_logs
from contest_tools.manifest_manager import ManifestManager
from contest_tools.utils.profiler import ProfileContext
from contest_tools.utils.architecture_validator import ArchitectureValidator
from contest_tools.contest_definitions import ContestDefinition

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
                # Cleanup old archive_temp.zip files (15 minutes) within active sessions
                zip_path = os.path.join(item_path, 'archive_temp.zip')
                if os.path.exists(zip_path):
                    zip_age = now - os.stat(zip_path).st_mtime
                    if zip_age > 900:  # 15 minutes
                        os.remove(zip_path)
                        logger.info(f"Cleaned up old archive_temp.zip in session {item}")
                
                # Cleanup entire session if older than max_age_seconds
                if os.stat(item_path).st_mtime < (now - max_age_seconds):
                    shutil.rmtree(item_path)
                    logger.info(f"Cleaned up old session: {item}")
            except Exception as e:
                logger.warning(f"Failed to cleanup session {item}: {e}")

def _update_progress(request_id, step, message=None, file_count=None, download_url=None):
    """Writes the current progress step to a transient JSON file.
    
    Args:
        request_id: Unique identifier for the progress tracking
        step: Progress step number (1, 2, 3, etc.)
        message: Optional status message (e.g., "Zipping...")
        file_count: Optional file count for display
        download_url: Optional download URL when file is ready
    """
    if not request_id:
        return
    
    progress_dir = os.path.join(settings.MEDIA_ROOT, 'progress')
    os.makedirs(progress_dir, exist_ok=True)
    
    file_path = os.path.join(progress_dir, f"{request_id}.json")
    temp_path = f"{file_path}.tmp"

    # Build progress data
    progress_data = {'step': step}
    if message:
        progress_data['message'] = message
    if file_count is not None:
        progress_data['file_count'] = file_count
    if download_url:
        progress_data['download_url'] = download_url

    # Write to a temporary file first
    with open(temp_path, 'w') as f:
        json.dump(progress_data, f)
    
    # Atomic replace to avoid JSONDecodeError on read
    os.replace(temp_path, file_path)

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
    elif contest == 'ARRL-10' and year:
        # ARRL 10 Meter doesn't have modes - contest code is '10m'
        try:
            from contest_tools.utils.log_fetcher import fetch_arrl_log_index, ARRL_CONTEST_CODES
            contest_code = ARRL_CONTEST_CODES.get('ARRL-10')
            if contest_code:
                callsigns = fetch_arrl_log_index(year, contest_code)
                return JsonResponse({'callsigns': callsigns})
            else:
                return JsonResponse({'error': 'ARRL-10 contest code not found'}, status=500)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'callsigns': []})

def home(request):
    form = UploadLogForm()
    return render(request, 'analyzer/home.html', {'form': form})

def analyze_logs(request):
    # DIAGNOSTICS: Log all requests to this function (ERROR level for visibility)
    logger.error(f"[DIAG] analyze_logs called. Method: {request.method}, Path: {request.path}")
    
    if request.method == 'POST':
        logger.error(f"[DIAG] POST request detected. FILES keys: {list(request.FILES.keys())}, POST keys: {list(request.POST.keys())}")
        
        _cleanup_old_sessions() # Trigger lazy cleanup
        
        # Retrieve the request_id from the form to track progress
        request_id = request.POST.get('request_id')
        logger.error(f"[DIAG] request_id from POST: {request_id}")
        
        # Wrap _update_progress in try/except - it might be failing silently
        try:
            _update_progress(request_id, 1) # Step 1: Uploading (Done, moving to Parsing)
            logger.error(f"[DIAG] _update_progress called successfully")
        except Exception as e:
            logger.error(f"[DIAG] _update_progress FAILED: {e}")
            logger.exception("Exception in _update_progress")

        # Handle Manual Upload
        if 'log1' in request.FILES:
            logger.error(f"[DIAG] Manual upload branch entered")
            # DIAGNOSTICS: Log request details (ERROR level for visibility)
            logger.error(f"[DIAG] Manual upload detected. FILES keys: {list(request.FILES.keys())}")
            logger.error(f"[DIAG] POST keys: {list(request.POST.keys())}")
            for key in request.FILES.keys():
                file_obj = request.FILES[key]
                logger.error(f"[DIAG]   File '{key}': name={file_obj.name}, size={file_obj.size}, content_type={file_obj.content_type}")
            
            form = UploadLogForm(request.POST, request.FILES)
            
            # DIAGNOSTICS: Log form state before validation
            logger.error(f"[DIAG] Form created. cleaned_data available: {hasattr(form, 'cleaned_data')}")
            
            if form.is_valid():
                logger.error(f"[DIAG] Form validation PASSED")
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
                except ValueError as e:
                    logger.warning(f"Validation error during manual upload: {e}")
                    return render(request, 'analyzer/home.html', {'form': form, 'error': str(e)})
        
                except Exception as e:
                    logger.exception("Log analysis failed")
                    return render(request, 'analyzer/home.html', {'form': form, 'error': str(e)})
            else:
                # Form validation failed - render form with errors
                logger.error(f"[DIAG] Form validation FAILED. Form errors: {form.errors}")
                logger.error(f"[DIAG] Form non-field errors: {form.non_field_errors()}")
                for field, errors in form.errors.items():
                    logger.error(f"[DIAG]   Field '{field}' errors: {errors}")
                
                # Build detailed error message from form errors
                error_details = []
                for field, errors in form.errors.items():
                    for error in errors:
                        error_details.append(f"{field}: {error}")
                if error_details:
                    error_msg = "Form validation failed: " + "; ".join(error_details)
                else:
                    error_msg = "Please check the file uploads and try again."
                return render(request, 'analyzer/home.html', {'form': form, 'error': error_msg})
        
        # Handle Public Fetch
        elif 'fetch_callsigns' in request.POST:
            logger.error(f"[DIAG] Public fetch branch entered")
            try:
                # 1. Create Session Context
                session_key = str(uuid.uuid4())
                session_path = os.path.join(settings.MEDIA_ROOT, 'sessions', session_key)
                os.makedirs(session_path, exist_ok=True)

                # 2. Fetch Logs
                callsigns_raw = request.POST.get('fetch_callsigns') # JSON string
                year = request.POST.get('fetch_year')
                mode = request.POST.get('fetch_mode')  # May be empty for ARRL-10
                contest = request.POST.get('fetch_contest', 'CQ-WW')  # Default to CQ-WW for backward compatibility
                
                callsigns = json.loads(callsigns_raw)
                
                _update_progress(request_id, 1) # Step 1: Fetching
                
                # Route to appropriate download function based on contest
                if contest == 'CQ-WW' and mode:
                    log_paths = download_logs(callsigns, year, mode, session_path)
                elif contest == 'ARRL-10':
                    from contest_tools.utils.log_fetcher import download_arrl_logs, ARRL_CONTEST_CODES
                    contest_code = ARRL_CONTEST_CODES.get('ARRL-10')
                    if contest_code:
                        log_paths = download_arrl_logs(callsigns, year, contest_code, session_path)
                    else:
                        raise ValueError('ARRL-10 contest code not found')
                else:
                    raise ValueError(f'Unsupported contest: {contest}')
                
                return _run_analysis_pipeline(request_id, log_paths, session_path, session_key)
            
            except ValueError as e:
                logger.warning(f"Validation error during public log fetch: {e}")
                return render(request, 'analyzer/home.html', {'form': UploadLogForm(), 'error': str(e)})
             
            except Exception as e:
                logger.exception("Public log fetch failed")
                return render(request, 'analyzer/home.html', {'form': UploadLogForm(), 'error': str(e)})
        
    # If we get here, neither branch was taken
    logger.error(f"[DIAG] Neither manual upload nor public fetch branch taken. Redirecting to home.")
    logger.error(f"[DIAG] request.method={request.method}, 'log1' in FILES={'log1' in request.FILES if hasattr(request, 'FILES') else 'N/A'}, 'fetch_callsigns' in POST={'fetch_callsigns' in request.POST if request.method == 'POST' else 'N/A'}")
    return redirect('home')

def _run_analysis_pipeline(request_id, log_paths, session_path, session_key):
    """Shared logic for processing logs (Manual or Fetched)."""
    with ProfileContext("Web Analysis Pipeline (Total)"):
        # 3. Process with LogManager
        # Note: We rely on docker-compose env vars for CONTEST_INPUT_DIR
        root_input = os.environ.get('CONTEST_INPUT_DIR', '/app/CONTEST_LOGS_REPORTS')
        
        _update_progress(request_id, 2) # Step 2: Parsing
        with ProfileContext("Web - Log Loading"):
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
        
        with ProfileContext("Web - Report Generation"):
            generator = ReportGenerator(lm.logs, root_output_dir=session_path)
            
            # --- Architecture Validation: Check for scoring inconsistencies ---
            try:
                validator = ArchitectureValidator()
                validation_results = validator.validate_all(generator.logs)
                if validation_results['warnings']:
                    for warning in validation_results['warnings']:
                        logger.warning(f"Architecture Validation: {warning}")
                logger.info(f"Architecture Validation: {validation_results['summary']}")
            except Exception as e:
                logger.warning(f"Architecture validation failed: {e}. Continuing with report generation.")
            # ------------------------------------
            
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
        with ProfileContext("Web - Dashboard Aggregation"):
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

    # Extract CTY Version Info (format: CTY-3538 2024-12-09)
    cty_path = lm.logs[0].cty_dat_path
    cty_date = CtyLookup.extract_version_date(cty_path)
    cty_date_str = cty_date.strftime('%Y-%m-%d') if cty_date else "Unknown Date"
    # Extract version number from filename (e.g., cty_wt_mod_3538.dat -> 3538)
    version_match = re.search(r'(\d{4})', os.path.basename(cty_path))
    cty_version_str = f"CTY-{version_match.group(1)}" if version_match else "CTY-Unknown"
    cty_info = f"{cty_version_str} {cty_date_str}"
    # Create footer text with CLA abbreviation
    footer_text = f"CLA v{__version__}   |   {cty_info}"
    
    all_calls = sorted([l.get_metadata().get('MyCall', f'Log{i+1}') for i, l in enumerate(lm.logs)])
    combo_id = build_callsigns_filename_part(all_calls)

    # Construct safe URL path (LOWERCASE to match ReportGenerator's disk output)
    path_components = [year, contest_name.lower(), event_id.lower(), combo_id.lower()]
    report_url_path = "/".join([str(p) for p in path_components if p])

    # Protocol 3.5: Construct Standardized Filenames <report_id>--<callsigns>.<ext>
    # CRITICAL: Filenames on disk are lowercased by ReportGenerator. We must match that.
    animation_filename = f"interactive_animation--{combo_id.lower()}.html"
    plot_filename = f"qso_rate_plots_all--{combo_id.lower()}.html"
    
    # Note: Multiplier filename removed here. It is now dynamically resolved in multiplier_dashboard view.

    # Extract valid_bands and valid_modes from contest definition for dashboard context
    # Note: Dashboards now load this directly from ContestDefinition JSON, but we keep it
    # in context for backward compatibility and other uses (e.g., download_all_reports)
    valid_bands = ['80M', '40M', '20M', '15M', '10M']  # Default fallback
    valid_modes = []  # Default: empty list (will be populated if defined in JSON)
    if lm.logs:
        try:
            valid_bands = lm.logs[0].contest_definition.valid_bands
            valid_modes = lm.logs[0].contest_definition.valid_modes
        except Exception as e:
            logger.warning(f"Failed to extract valid_bands/valid_modes from contest definition: {e}")
    
    context = {
        'session_key': session_key,
        'report_url_path': report_url_path,
        'animation_file': animation_filename,
        'plot_file': plot_filename,
        'logs': [],
        'mult_headers': [],
        'full_contest_title': full_contest_title,
        'cty_version_info': cty_info,
        'footer_text': footer_text,
        'contest_name': contest_name,
        'valid_bands': valid_bands,  # Kept for backward compatibility and other uses
        'valid_modes': valid_modes,  # Kept for backward compatibility and other uses
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
    # Enable same dashboard structure for CQ-WW and ARRL-10
    if not (contest_name.startswith('CQ-WW') or contest_name.startswith('ARRL-10')):
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

def _extract_contest_name_from_path(report_rel_path: str) -> str:
    """
    Extracts contest name from the report directory path structure.
    
    Path format: "reports/YYYY/contest_name/event_id/combo_id/" or similar variations.
    Returns contest name in format expected by ContestDefinition.from_json() (e.g., "ARRL-10", "CQ-WW-CW").
    
    Args:
        report_rel_path: Relative path from session root (e.g., "reports/2024/arrl-10/jan/k1lz_k3lr")
    
    Returns:
        Contest name string (e.g., "ARRL-10", "CQ-WW-CW") or None if extraction fails
    """
    if not report_rel_path:
        return None
    
    # Split path and normalize
    parts = [p for p in report_rel_path.replace("\\", "/").split("/") if p]
    
    # Path structure: reports/YYYY/contest_name/event_id/combo_id
    # We want the contest_name part (typically index 2)
    if len(parts) >= 3 and parts[0].lower() == 'reports':
        contest_name_lower = parts[2]  # e.g., "arrl-10", "cq-ww-cw"
        # Convert to expected format: uppercase and replace hyphens appropriately
        # Contest definition files use format like "ARRL-10", "CQ-WW-CW"
        contest_name = contest_name_lower.upper().replace('_', '-')
        return contest_name
    
    return None

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

    # 1. Discover Manifest (Deep Search)
    manifest_dir = None
    for root, dirs, files in os.walk(session_path):
        if 'session_manifest.json' in files:
            manifest_dir = root
            break
    
    if not manifest_dir:
        raise Http404("Analysis manifest not found")

    # 2. Load Manifest & Context
    manifest_mgr = ManifestManager(manifest_dir)
    artifacts = manifest_mgr.load()
    report_rel_path = os.path.relpath(manifest_dir, session_path).replace("\\", "/")
    combo_id = os.path.basename(manifest_dir)

    # 3. Data Hydration Strategy
    breakdown_data = None

    # Strategy A: Fast Load (JSON Artifact)
    # Look for the JSON file generated by json_multiplier_breakdown.py
    # New format: --{combo_id}.json, Old format (backward compat): _{combo_id}.json
    json_suffix_new = f"--{combo_id}.json"
    json_suffix_old = f"_{combo_id}.json"
    json_art = next((a for a in artifacts 
                    if a['report_id'] == 'json_multiplier_breakdown' 
                    and (a['path'].endswith(json_suffix_new) or a['path'].endswith(json_suffix_old))), None)
    
    if json_art:
        try:
            full_path = os.path.join(manifest_dir, json_art['path'])
            with open(full_path, 'r') as json_file:
                breakdown_data = json.load(json_file)
        except Exception as e:
            logger.error(f"Failed to load JSON artifact: {e}")

    # 4. Fetch Persisted Dashboard Context (EARLY LOAD)
    context_path = os.path.join(session_path, 'dashboard_context.json')
    dashboard_ctx = {}
    persisted_logs = []
    
    if os.path.exists(context_path):
        try:
            with open(context_path, 'r') as f:
                dashboard_ctx = json.load(f)
                persisted_logs = dashboard_ctx.get('logs', [])
    
        except Exception as e:
            logger.error(f"Failed to load dashboard context: {e}")

    # 5. Load contest definition to determine dimension (band vs mode)
    # Extract contest name from directory path structure (no cache needed)
    contest_name = _extract_contest_name_from_path(report_rel_path)
    valid_bands = ['80M', '40M', '20M', '15M', '10M']  # Default fallback
    valid_modes = []  # Default: empty list
    
    if contest_name:
        try:
            # Load contest definition directly from JSON (no log parsing needed)
            contest_def = ContestDefinition.from_json(contest_name)
            valid_bands = contest_def.valid_bands
            valid_modes = contest_def.valid_modes
        except (FileNotFoundError, ValueError, Exception) as e:
            logger.warning(f"Failed to load contest definition for '{contest_name}': {e}. Using defaults.")
    else:
        logger.warning(f"Could not extract contest name from path: {report_rel_path}. Using defaults.")
    
    # Determine dimension (band vs mode) based on contest type
    is_single_band = len(valid_bands) == 1
    is_multi_mode = len(valid_modes) > 1
    dimension = 'mode' if (is_single_band and is_multi_mode) else 'band'
    is_mode_dimension = (dimension == 'mode')
    
    # 6. Metadata Strategy (Fast Path vs Slow Path)
    lm = None
    report_metadata = {}
    
    # Check if we have both breakdown data and persisted logs (not just empty dict)
    # Note: breakdown_data may be None if we detected wrong dimension in fast path
    if breakdown_data and persisted_logs:
        # --- FAST PATH: Hydrate from Cache ---
        # No LogManager, No Parsing. Instant load.
        
        # Detect dimension from breakdown_data structure first
        if 'modes' in breakdown_data:
            is_mode_dimension = True
            dimension = 'mode'
        elif 'bands' in breakdown_data:
            # Check if contest should actually be mode dimension (for backward compatibility)
            if is_single_band and is_multi_mode:
                # Contest should be mode dimension, but JSON has bands (old format)
                # Regenerate with correct dimension (requires slow path)
                breakdown_data = None  # Force regeneration
                is_mode_dimension = True
                dimension = 'mode'
            else:
                is_mode_dimension = False
                dimension = 'band'
        else:
            # Fallback: use contest definition we just loaded
            if is_single_band and is_multi_mode:
                is_mode_dimension = True
                dimension = 'mode'
        
        full_title = dashboard_ctx.get('full_contest_title', '')
        cty_info = dashboard_ctx.get('cty_version_info', 'CTY-Unknown Unknown Date')
        
        # Reconstruct calls from persisted logs to match combo_id logic
        calls = sorted([l['callsign'] for l in persisted_logs])
        call_str = ", ".join(calls)
        
        # Line 2: Context
        context_line = f"{full_title} - {call_str}"
        
        # Footer: One line with CLA abbreviation
        footer_text = f"CLA v{__version__}   |   {cty_info}"
        
        scope_line = "All Modes" if is_mode_dimension else "All Bands"
        report_metadata = {
            'context_line': context_line,
            'scope_line': scope_line,
            'footer': footer_text
        }
        
    else:
        # --- SLOW PATH: Fallback to Log Parsing ---
        # Required if JSON artifact is missing or context is corrupted
        # Note: valid_bands and valid_modes already loaded from ContestDefinition above
        lm = LogManager()
        log_candidates = []
        for f in os.listdir(session_path):
            f_path = os.path.join(session_path, f)
            if os.path.isfile(f_path) and not f.startswith('dashboard_context') and not f.endswith('.zip'):
                log_candidates.append(f_path)
        
        root_input = os.environ.get('CONTEST_INPUT_DIR', '/app/CONTEST_LOGS_REPORTS')
        lm.load_log_batch(log_candidates, root_input, 'after')
        
        # Dimension already determined from ContestDefinition above, no need to recalculate
        
        # Generate Aggregation if missing
        if not breakdown_data:
            mult_agg = MultiplierStatsAggregator(lm.logs)
            breakdown_data = mult_agg.get_multiplier_breakdown_data(dimension=dimension)
        else:
            # Detect dimension from existing breakdown_data structure
            if 'modes' in breakdown_data:
                is_mode_dimension = True
                dimension = 'mode'
            elif 'bands' in breakdown_data:
                is_mode_dimension = False
                dimension = 'band'
            
        # Generate Metadata using Utilities
        modes_present = set()
        for log in lm.logs:
            df = log.get_processed_data()
            if 'Mode' in df.columns:
                 modes_present.update(df['Mode'].dropna().unique())

        scope_label = "All Modes" if is_mode_dimension else "All Bands"
        title_lines = get_standard_title_lines("Multiplier Breakdown", lm.logs, scope_label, None, modes_present)
        
        # Footer with Newline
        # Extract CTY info in new format
        cty_info = get_cty_metadata(lm.logs)
        footer_text = f"CLA v{__version__}   |   {cty_info}"
        
        report_metadata = {
            'context_line': title_lines[1],
            'scope_line': title_lines[2],
            'footer': footer_text
        }
    
    # Split Dimension Values (Layout Logic) - First 3 go to "low", rest to "high"
    low_bands_data = []
    high_bands_data = []
    low_modes_data = []
    high_modes_data = []
    
    if breakdown_data:
        if is_mode_dimension and 'modes' in breakdown_data:
            # Split modes: first 3 to low, rest to high
            mode_blocks = breakdown_data['modes']
            for i, block in enumerate(mode_blocks):
                if i < 3:
                    low_modes_data.append(block)
                else:
                    high_modes_data.append(block)
        elif 'bands' in breakdown_data:
            # Split bands: 160M, 80M, 40M to low, rest to high
            low_bands = ['160M', '80M', '40M']
            for block in breakdown_data['bands']:
                if block['label'] in low_bands:
                    low_bands_data.append(block)
                else:
                    high_bands_data.append(block)
    
    # Calculate optimal column width for scoreboard
    log_count = len(persisted_logs) if persisted_logs else 0
    col_width = 12 // log_count if log_count > 0 else 12

    # Common suffix for text reports
    suffix = f"_{combo_id}"

    # 6. Extract Multiplier Names and Calculate Global Maxima Dynamically
    multiplier_names = []  # List of multiplier names found in the data
    global_max = {'total': 1}  # Dynamic dict: will contain 'total' and one entry per multiplier type
    
    if breakdown_data:
        # Extract multiplier names from totals (skip "TOTAL" row)
        if 'totals' in breakdown_data:
            for row in breakdown_data['totals']:
                mult_name = row.get('label', '')
                if mult_name and mult_name != 'TOTAL':
                    # Normalize multiplier name for use as dict key (lowercase, no spaces)
                    mult_key = mult_name.lower().replace(' ', '_')
                    if mult_name not in multiplier_names:
                        multiplier_names.append(mult_name)
                    # Initialize max for this multiplier type
                    if mult_key not in global_max:
                        global_max[mult_key] = 1
        
        # Calculate global_max for each multiplier type from dimension breakdowns (bands or modes)
        dimension_key = 'modes' if is_mode_dimension else 'bands'
        if dimension_key in breakdown_data:
            for block in breakdown_data[dimension_key]:
                for row in block['rows']:
                    row_max = 0
                    for stat in row['stations']:
                        val = stat.get('unique_run', 0) + stat.get('unique_sp', 0) + stat.get('unique_unk', 0)
                        if val > row_max: row_max = val
                    
                    row_label = row.get('label', '')
                    
                    # Check if this is the TOTAL or dimension total row
                    if row_label == 'TOTAL' or row_label == block.get('label', ''):
                        if row_max > global_max['total']: global_max['total'] = row_max
                    else:
                        # Check if this row matches any multiplier name (e.g., "10M_States", "CW_States", or "States")
                        for mult_name in multiplier_names:
                            # Match pattern: "{dimension_value}_{mult_name}" or just "{mult_name}"
                            if mult_name in row_label:
                                mult_key = mult_name.lower().replace(' ', '_')
                                if row_max > global_max[mult_key]: global_max[mult_key] = row_max

    # 4. Discover Text Version of Breakdown
    breakdown_txt_rel_path = None
    txt_suffix = f"_{combo_id}.txt"
    txt_bd_art = next((a for a in artifacts if a['report_id'] == 'text_multiplier_breakdown' and a['path'].endswith(txt_suffix)), None)
    if txt_bd_art:
        breakdown_txt_rel_path = f"{report_rel_path}/{txt_bd_art['path']}"

    # 5. Discover HTML Version of Breakdown
    breakdown_html_rel_path = None
    html_suffix = f"_{combo_id}.html"
    html_bd_art = next((a for a in artifacts if a['report_id'] == 'html_multiplier_breakdown' and a['path'].endswith(html_suffix)), None)
    if html_bd_art:
        breakdown_html_rel_path = f"{report_rel_path}/{html_bd_art['path']}"

    # Helper function to format multiplier label from filename slug
    def format_multiplier_label(mult_type_slug, contest_def=None):
        """
        Formats a multiplier label from a filename slug (e.g., "dxcc_cw" -> "DXCC CW").
        Strips mode suffix, looks up proper multiplier name from contest definition,
        and uppercases mode abbreviations.
        
        Args:
            mult_type_slug: The multiplier type slug from filename (e.g., 'dxcc_cw', 'us_states')
            contest_def: ContestDefinition object (can be None)
        
        Returns:
            Properly formatted label (e.g., "DXCC CW" or "US States")
        """
        if not mult_type_slug:
            return ""
        
        # Parse the slug - handle mode suffixes (e.g., 'dxcc_cw' -> 'dxcc' + 'cw')
        parts = mult_type_slug.split('_')
        mult_name_slug = mult_type_slug
        mode_suffix = None
        
        # Check if last part is a mode suffix (2-3 character codes like cw, ph, rtty)
        if len(parts) > 1 and len(parts[-1]) <= 3:
            # Might have mode suffix, try without it
            mult_name_slug = '_'.join(parts[:-1])
            mode_suffix = parts[-1].upper()  # Uppercase mode (CW, PH, RTTY)
        
        # Look up multiplier name from contest definition if available
        mult_name = None
        if contest_def and hasattr(contest_def, 'multiplier_rules'):
            # Try exact match with mode suffix removed first
            for rule in contest_def.multiplier_rules:
                rule_slug = rule.get('name', '').lower().replace(' ', '_')
                if rule_slug == mult_name_slug:
                    mult_name = rule.get('name')  # Return the proper name from definition (e.g., "DXCC")
                    break
            
            # Try exact match with original slug (in case multiplier name has underscores)
            if not mult_name:
                for rule in contest_def.multiplier_rules:
                    rule_slug = rule.get('name', '').lower().replace(' ', '_')
                    if rule_slug == mult_type_slug:
                        mult_name = rule.get('name')
                        break
        
        # Fallback: format the slug WITHOUT mode suffix
        if not mult_name:
            # Convert to title case for readability (e.g., "us_states" -> "US States")
            # But handle common abbreviations that should be all caps
            words = mult_name_slug.replace('_', ' ').split()
            formatted_words = []
            for word in words:
                # Common multiplier abbreviations that should be all caps
                if word.upper() in ['DXCC', 'ITU', 'CQ', 'WAE', 'WPX', 'US']:
                    formatted_words.append(word.upper())
                else:
                    formatted_words.append(word.title())
            mult_name = ' '.join(formatted_words)
        
        # Combine multiplier name and mode suffix
        if mode_suffix:
            return f"{mult_name} {mode_suffix}"
        else:
            return mult_name
    
    # Get contest definition for multiplier name lookup
    contest_def_for_label = None
    if lm and lm.logs:
        contest_def_for_label = lm.logs[0].contest_definition
    elif persisted_logs:
        # Fast path: Try to load contest definition minimally
        try:
            root_input = os.environ.get('CONTEST_INPUT_DIR', '/app/CONTEST_LOGS_REPORTS')
            log_candidates = [f for f in os.listdir(session_path) 
                            if os.path.isfile(os.path.join(session_path, f)) 
                            and not f.startswith('dashboard_context') 
                            and not f.endswith('.zip') 
                            and not f.endswith('.json')]
            if log_candidates:
                temp_lm = LogManager()
                temp_lm.load_log_batch(log_candidates[:1], root_input, 'after')  # Load just first log
                if temp_lm.logs:
                    contest_def_for_label = temp_lm.logs[0].contest_definition
        except Exception as e:
            logger.debug(f"Failed to load contest definition for multiplier label lookup: {e}")

    # 2. Scan and Group Reports
    # Use Manifest to find Missed/Summary reports
    multipliers = {}

    # Prepare Suffixes for Categorization
    # Extract callsigns from persisted logs and build filename part
    persisted_callsigns = [l['callsign'] for l in persisted_logs]
    callsigns_part = build_callsigns_filename_part(sorted(persisted_callsigns))
    # For backward compatibility with old format parsing
    all_calls_safe = [callsign_to_filename_part(c) for c in sorted(persisted_callsigns)]
    
    # 1. Session Suffix (All Logs) - format: --{callsigns}
    suffix_session = "--" + callsigns_part

    target_ids = ['missed_multipliers', 'multiplier_summary']
    
    for art in artifacts:
        rid = art['report_id']
        if rid not in target_ids: continue
        
        mult_type = None
        report_key = None
        category = None # 'session', 'pair', 'single'
        label_context = None # e.g. "K1LZ vs K3LR" or "K1LZ"

        # Extract Mult Type from Filename: {report_id}_{MULT_TYPE}--{callsigns}.txt
        fname = os.path.basename(art['path'])
        # Strip extension
        base = os.path.splitext(fname)[0]
        
        # --- Categorization Logic ---
        # Check for new format with -- delimiter
        if base.endswith(suffix_session):
            category = 'session'
            base = base[:-len(suffix_session)]
        # Also check for old format (backward compatibility during migration)
        elif base.endswith("_" + callsigns_part):
            category = 'session'
            base = base[:-len("_" + callsigns_part)]
        else:
            # Parse callsigns from filename part (handle -- delimiter)
            # Format: {report_id}_{MULT_TYPE}--{callsigns} or old format {report_id}_{MULT_TYPE}_{callsigns}
            if '--' in base:
                # New format: split on -- to get callsigns part
                parts = base.rsplit('--', 1)
                if len(parts) == 2:
                    callsigns_part = parts[1]
                    parsed_calls = parse_callsigns_from_filename_part(callsigns_part)
                    callsigns_safe_for_matching = [c.lower().replace('/', '-') for c in parsed_calls]
                else:
                    callsigns_safe_for_matching = []
            else:
                # Old format: try to extract from end (backward compatibility)
                callsigns_safe_for_matching = all_calls_safe
            
            # 1. Check Pairs
            # Pair reports contain exactly 2 callsigns in the filename
            found_pair = False
            if len(callsigns_safe_for_matching) == 2:
                # This is a pair report - check if filename ends with the pair suffix
                c1, c2 = sorted(callsigns_safe_for_matching)
                p_suff_new = f"--{c1}_{c2}"
                p_suff_old = f"_{c1}_{c2}"
                if base.endswith(p_suff_new):
                    category = 'pairs'
                    label_context = f"{c1.upper().replace('-', '/')} vs {c2.upper().replace('-', '/')}"
                    base = base[:-len(p_suff_new)]
                    found_pair = True
                elif base.endswith(p_suff_old):
                    category = 'pairs'
                    label_context = f"{c1.upper()} vs {c2.upper()}"
                    base = base[:-len(p_suff_old)]
                    found_pair = True
            elif len(callsigns_safe_for_matching) > 2:
                # Multiple callsigns - check all possible pairs (for backward compatibility with old format)
                pairs = list(itertools.combinations(callsigns_safe_for_matching, 2))
                for p in pairs:
                    # Pairs in new format: --call1_call2, old format: _call1_call2
                    c1, c2 = sorted(p)
                    p_suff_new = f"--{c1}_{c2}"
                    p_suff_old = f"_{c1}_{c2}"
                    if base.endswith(p_suff_new):
                        category = 'pairs'
                        label_context = f"{c1.upper().replace('-', '/')} vs {c2.upper().replace('-', '/')}"
                        base = base[:-len(p_suff_new)]
                        found_pair = True
                        break
                    elif base.endswith(p_suff_old):
                        category = 'pairs'
                        label_context = f"{c1.upper()} vs {c2.upper()}"
                        base = base[:-len(p_suff_old)]
                        found_pair = True
                        break

            # 2. Check Singles (if not pair)
            if not found_pair:
                for c in callsigns_safe_for_matching:
                    s_suff_new = f"--{c}"
                    s_suff_old = f"_{c}"
                    if base.endswith(s_suff_new):
                        category = 'singles'
                        label_context = c.upper().replace('-', '/')
                        base = base[:-len(s_suff_new)]
                        break
                    elif base.endswith(s_suff_old):
                        category = 'singles'
                        label_context = c.upper()
                        base = base[:-len(s_suff_old)]
                        break

        # Strip prefix
        if base.startswith(rid + '_'):
            mult_type_slug = base[len(rid)+1:]
            # Use helper function to format multiplier label properly
            mult_type = format_multiplier_label(mult_type_slug, contest_def_for_label)
        else:
            continue

        if rid == 'missed_multipliers':
            report_key = 'missed'
        elif rid == 'multiplier_summary':
            report_key = 'summary'
        
        if report_key and category:
            if mult_type not in multipliers:
                multipliers[mult_type] = {
                    'label': mult_type, 
                    'session': {'missed': None, 'summary': None},
                    'pairs': [],
                    'singles': []
                }
            
            # Construct relative link
            link = f"{report_rel_path}/{art['path']}"
            
            if category == 'session':
                multipliers[mult_type]['session'][report_key] = link
            else:
                # For pairs/singles, we append to a list.
                # We need to find if an entry for this context already exists to merge 'missed' and 'summary'
                target_list = multipliers[mult_type][category]
                existing = next((item for item in target_list if item['label'] == label_context), None)
                if not existing:
                    existing = {'label': label_context, 'missed': None, 'summary': None}
                    target_list.append(existing)
                existing[report_key] = link
                # Sort lists for consistency
                target_list.sort(key=lambda x: x['label'])

    # Convert dict to sorted list for template
    sorted_mults = sorted(multipliers.values(), key=lambda x: x['label'])

    context = {
        'session_id': session_id,
        'scoreboard': persisted_logs, # Use persisted logs for accurate scores
        'col_width': col_width,
        'breakdown_totals': breakdown_data['totals'] if breakdown_data else [],
        'low_bands_data': low_bands_data,
        'high_bands_data': high_bands_data,
        'low_modes_data': low_modes_data,
        'high_modes_data': high_modes_data,
        'is_mode_dimension': is_mode_dimension,
        'all_calls': sorted([l['callsign'] for l in persisted_logs]),
        'breakdown_txt_url': breakdown_txt_rel_path,
        'breakdown_html_url': breakdown_html_rel_path,
        'report_metadata': report_metadata,
        'multipliers': sorted_mults,
        'is_solo': (log_count == 1),
        'global_max': global_max,
        'multiplier_names': multiplier_names,  # Dynamic list of multiplier types for Band Spectrum tabs
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
    
    # Derive combo_id from the directory name (Authoritative source from ReportGenerator)
    combo_id = os.path.basename(manifest_dir)

    # Calculate relative path segment (e.g., "reports/2024/...") to prepend to artifact paths
    report_rel_path = os.path.relpath(manifest_dir, session_path).replace("\\", "/")

    # 2. Re-construct Callsigns from the combo_id
    callsigns_display = parse_callsigns_from_filename_part(combo_id)
    callsigns_safe = [c.lower().replace('/', '-') for c in callsigns_display]  # For filename matching
    is_solo = (len(callsigns_safe) == 1)
    
    # 2a. Load valid_bands and valid_modes from contest definition JSON (no cache needed)
    # Extract contest name from directory path structure
    contest_name = _extract_contest_name_from_path(report_rel_path)
    DEFAULT_BANDS = ['80M', '40M', '20M', '15M', '10M']  # Default fallback
    valid_bands = DEFAULT_BANDS.copy()
    valid_modes = []  # Default: empty list
    
    if contest_name:
        try:
            # Load contest definition directly from JSON (no log parsing needed)
            contest_def = ContestDefinition.from_json(contest_name)
            valid_bands = contest_def.valid_bands
            valid_modes = contest_def.valid_modes
        except (FileNotFoundError, ValueError, Exception) as e:
            logger.warning(f"Failed to load contest definition for '{contest_name}': {e}. Using defaults.")
    else:
        logger.warning(f"Could not extract contest name from path: {report_rel_path}. Using defaults.")
    
    # Determine contest type for selector generation
    is_single_band = len(valid_bands) == 1
    is_multi_mode = len(valid_modes) > 1
    is_multi_band = len(valid_bands) > 1
    
    # Determine selector type for Rate Differential pane
    # - Single-band, multi-mode: mode selector (e.g., ARRL 10)
    # - Multi-band, single-mode: band selector (e.g., CQ WW CW)
    # - Multi-band, multi-mode: band selector (primary), mode can be added later (e.g., NAQP, ARRL FD)
    diff_selector_type = 'mode' if (is_single_band and is_multi_mode) else 'band'
    
    # Build band mapping: "80M" -> "80" for template buttons
    valid_bands_for_buttons = []
    for band in valid_bands:
        # Convert "80M" -> "80", "160M" -> "160", etc.
        band_num = band.replace('M', '').lower()
        valid_bands_for_buttons.append({
            'display': band_num,
            'key': band_num,
            'full': band
        })
    
    BAND_SORT_ORDER = {'ALL': 0, '160M': 1, '80M': 2, '40M': 3, '20M': 4, '15M': 5, '10M': 6, '6M': 7, '2M': 8}
    MODE_SORT_ORDER = {'ALL': 0, 'CW': 1, 'PH': 2, 'RY': 3, 'DG': 4}
    
    def parse_diff_filename_metadata(metadata_part: str, valid_bands: list, valid_modes: list, is_single_band: bool) -> str:
        """
        Parses filename metadata part into a structured key for diff_paths.
        
        Filename format: cumulative_difference_plots_qsos_{band}_{mode}--{callsigns}.html
        Examples:
        - "10" (single-band, all modes) → "mode:all" (for single-band, multi-mode)
        - "10_cw" (single-band, CW mode) → "mode:cw"
        - "all" (multi-band, all modes) → "band:all"
        - "80" (multi-band, all modes, specific band) → "band:80"
        - "80_cw" (multi-band, CW mode, specific band) → "band:80" (mode handled separately later)
        
        Returns structured key: "dimension:value" format for extensibility.
        """
        parts = metadata_part.split('_')
        band_part = parts[0].lower()
        mode_part = parts[1].lower() if len(parts) > 1 else None
        
        # Normalize band part
        if band_part == 'all':
            band_key = 'all'
        elif band_part.isdigit():
            band_key = band_part
        else:
            # Try to match against valid_bands (e.g., "160m" -> "160")
            band_key = band_part.replace('m', '')
        
        # Normalize mode part
        mode_key = None
        if mode_part:
            mode_upper = mode_part.upper()
            # Map common variations
            if mode_upper in ['CW', 'PH', 'RY', 'DG']:
                mode_key = mode_upper
            elif mode_upper in ['SSB', 'USB', 'LSB']:
                mode_key = 'PH'  # Cabrillo uses PH
        
        # Determine selector type and generate key
        if is_single_band and len(valid_modes) > 1:
            # Single-band, multi-mode: use mode dimension
            if mode_key:
                return f"mode:{mode_key.lower()}"
            else:
                return "mode:all"
        else:
            # Multi-band (or single-band, single-mode): use band dimension
            # For now, ignore mode in key (can add mode: prefix later for multi-band, multi-mode)
            return f"band:{band_key}"
    
    # 3. Identify Pairs for Strategy Tab
    matchups = []
    # Requested Sort Order for Diff Plots - filter to only valid bands
    DIFF_BANDS = ['ALL'] + [band for band in ['160M', '80M', '40M', '20M', '15M', '10M'] if band in valid_bands]

    if not is_solo:
        import itertools
        pairs = list(itertools.combinations(callsigns_safe, 2))
        
        for p in pairs:
            c1, c2 = sorted(p)
            label = f"{c1.upper()} vs {c2.upper()}"
            
            # Discover available band variants for the diff plot via Manifest
            # New format: cumulative_difference_plots_qsos_{band}--{callsigns}.html
            # Where callsigns is {c1}_{c2} (lowercase, underscore-separated)
            diff_paths = {}
            diff_json_paths = {}
            
            # Build expected callsigns part for this pair (lowercase, underscore-separated)
            pair_callsigns = f"{c1}_{c2}"
            
            # Filter artifacts for this pair's difference plots
            target_prefix = "cumulative_difference_plots_qsos_"
            target_suffix = f"--{pair_callsigns}"
            
            for art in artifacts:
                if art['report_id'] == 'cumulative_difference_plots':
                    fname = os.path.basename(art['path'])
                    
                    # Check if this file matches our pair (new format with -- delimiter)
                    if target_suffix in fname and fname.startswith(target_prefix):
                        # Extract metadata part from filename: cumulative_difference_plots_qsos_{band}_{mode}--{callsigns}.html
                        # Format: {prefix}{metadata}--{callsigns}.{ext}
                        metadata_part = fname.replace(target_prefix, '').split('--')[0]
                        
                        # Parse into structured key (dimension:value format)
                        structured_key = parse_diff_filename_metadata(metadata_part, valid_bands, valid_modes, is_single_band)
                        
                        if art['path'].endswith('.html'):
                            # Prepend report_rel_path to ensure view_report can find it
                            diff_paths[structured_key] = f"{report_rel_path}/{art['path']}"
                        elif art['path'].endswith('.json'):
                            # JSON Path Logic (Direct URL access via media)
                            diff_json_paths[structured_key] = f"{settings.MEDIA_URL}sessions/{session_id}/{report_rel_path}/{art['path']}"
        
            # Find breakdown chart
            bk_path = next((f"{report_rel_path}/{a['path']}" for a in artifacts if a['report_id'] == 'qso_breakdown_chart' and f"_{c1}_{c2}" in a['path'] and a['path'].endswith('.html')), "")
            bk_json = next((f"{settings.MEDIA_URL}sessions/{session_id}/{report_rel_path}/{a['path']}" for a in artifacts if a['report_id'] == 'qso_breakdown_chart' and f"_{c1}_{c2}" in a['path'] and a['path'].endswith('.json')), "")
            
            # Explicitly target HTML for interactive view
            ba_path = next((f"{report_rel_path}/{a['path']}" for a in artifacts if a['report_id'] == 'chart_comparative_activity_butterfly' and f"_{c1}_{c2}" in a['path'] and a['path'].endswith('.html')), "")
            ba_json = next((f"{settings.MEDIA_URL}sessions/{session_id}/{report_rel_path}/{a['path']}" for a in artifacts if a['report_id'] == 'chart_comparative_activity_butterfly' and f"_{c1}_{c2}" in a['path'] and a['path'].endswith('.json')), "")
            cont_path = next((f"{report_rel_path}/{a['path']}" for a in artifacts if a['report_id'] == 'comparative_continent_summary' and f"_{c1}_{c2}" in a['path']), "")

            matchups.append({
                'label': label,
                'id': f"{c1}_{c2}",
                'diff_paths': diff_paths,
                'diff_json_paths': diff_json_paths,
                'qso_breakdown_file': bk_path,
                'qso_breakdown_json': bk_json,
                'band_activity_file': ba_path,
                'band_activity_json': ba_json,
                'continent_file': cont_path
            })

    # 4. Discover Point Rate Plots (Manifest Scan)
    point_plots = []
    
    # For multi-log: Only show comparison plots (ending with combo_id)
    # For single-log: Show individual station plots (ending with single callsign)
    # New format: --{combo_id}.html, Old format: _{combo_id}.html
    target_suffix_new = f"--{combo_id}.html" if not is_solo else None
    target_suffix_old = f"_{combo_id}.html" if not is_solo else None
    target_callsigns = callsigns_safe if is_solo else None

    for art in artifacts:
        if art['report_id'] == 'point_rate_plots' and art['path'].endswith('.html'):
            fname = os.path.basename(art['path'])
            
            # Filter by suffix pattern
            if not is_solo:
                # Multi-log: Only include comparison plots (ending with combo_id)
                # Check both new and old formats
                if not (target_suffix_new and fname.endswith(target_suffix_new)) and not (target_suffix_old and fname.endswith(target_suffix_old)):
                    continue
            else:
                # Single-log: Only include individual station plots (ending with single callsign)
                # Exclude comparison plots (those ending with combo_id which is same as single callsign)
                # For single log, combo_id IS the callsign, so we need to check if it's exactly one callsign
                # Pattern: point_rate_plots_{band}--{callsign}.html (new) or point_rate_plots_{band}_{callsign}.html (old)
                matches_single = False
                for call in target_callsigns:
                    single_suffix_new = f"--{call}.html"
                    single_suffix_old = f"_{call}.html"
                    if fname.endswith(single_suffix_new) or fname.endswith(single_suffix_old):
                        matches_single = True
                        break
                if not matches_single:
                    continue
            
            # Handle new format with -- delimiter: point_rate_plots_{band}--{callsigns}.html
            # or old format: point_rate_plots_{band}_{callsigns}.html
            if '--' in fname:
                # New format: point_rate_plots_all--k1lz_k3lr_w3lpl.html or point_rate_plots_20m--k1lz_k3lr_w3lpl.html
                # Split on -- to separate band/mode from callsigns
                parts_before_dash = fname.replace('point_rate_plots_', '').split('--')[0]
                # Extract band from first part (e.g., "all", "20m", "20m_cw", "10_cw", "10_ph")
                band_parts = parts_before_dash.split('_')
                band_key = band_parts[0].upper()
                mode_key = band_parts[1].upper() if len(band_parts) > 1 else None
            else:
                # Old format (backward compatibility): point_rate_plots_20m_k1lz_k3lr.html
                remainder = fname.replace('point_rate_plots_', '')
                parts = remainder.split('_')
                if parts:
                    band_key = parts[0].upper()
                    mode_key = parts[1].upper() if len(parts) > 1 else None
                else:
                    continue
            
            if band_key.isdigit(): band_key += 'M'
            
            # For single-band, multi-mode contests: use mode labels instead of band labels
            # e.g., ARRL 10: "All", "CW", "PH" instead of all showing "10"
            if is_single_band and is_multi_mode and mode_key:
                # Extract mode from filename (e.g., "10_cw" -> "CW", "10_ph" -> "PH")
                mode_upper = mode_key
                if mode_upper in ['CW', 'PH', 'RY', 'DG']:
                    label = mode_upper
                elif mode_upper in ['SSB', 'USB', 'LSB']:
                    label = 'PH'  # Cabrillo uses PH
                else:
                    label = mode_upper  # Fallback
                # Sort value will be set later by MODE_SORT_ORDER, use temp value for now
                sort_val = 50  # Temporary, will be overridden
            elif is_single_band and is_multi_mode and not mode_key:
                # "All" mode for single-band, multi-mode (e.g., "10" without mode suffix)
                label = "All"
                # Sort value will be set later by MODE_SORT_ORDER, use temp value for now
                sort_val = 50  # Temporary, will be overridden
            else:
                # Multi-band contests: use band labels
                label = "All Bands" if band_key == 'ALL' else band_key
                sort_val = BAND_SORT_ORDER.get(band_key, 99)
            
            point_plots.append({
                'label': label,
                'file_html': f"{report_rel_path}/{art['path']}",
                'file_json': f"{settings.MEDIA_URL}sessions/{session_id}/{report_rel_path}/{art['path'].replace('.html', '.json')}",
                'sort_val': sort_val
            })
    
    # Sort: For single-band, multi-mode, sort by mode order (All first, then CW, PH, etc.)
    # For multi-band, sort by band order (All Bands first, then 20M, etc.)
    if is_single_band and is_multi_mode:
        # Define mode sort order
        MODE_SORT_ORDER = {'all': 0, 'cw': 1, 'ph': 2, 'ry': 3, 'dg': 4}
        for p in point_plots:
            label_lower = p['label'].lower()
            p['sort_val'] = MODE_SORT_ORDER.get(label_lower, 99)
        point_plots.sort(key=lambda x: x['sort_val'])
    else:
        point_plots.sort(key=lambda x: x['sort_val'])
    
    # Default active selection
    active_set = False
    if point_plots:
        # For single-band, multi-mode: prioritize "All", otherwise first available
        if is_single_band and is_multi_mode:
            for p in point_plots:
                if p['label'] == 'All':
                    p['active'] = True
                    active_set = True
                    break
            if not active_set:
                point_plots[0]['active'] = True
        else:
            # Multi-band: prioritize "All Bands", then 20M, then first available
            for p in point_plots:
                if p['label'] == 'All Bands':
                    p['active'] = True
                    active_set = True
                    break
            if not active_set:
                for p in point_plots:
                    if p['label'] == '20M':
                        p['active'] = True
                        active_set = True
                        break
            if not active_set:
                point_plots[0]['active'] = True

    # 5. Discover QSO Rate Plots (Manifest Scan)
    qso_band_plots = []
    
    # For multi-log: Only show comparison plots (ending with combo_id)
    # For single-log: Show individual station plots (ending with single callsign)
    # New format: --{combo_id}.html, Old format: _{combo_id}.html
    target_suffix_new = f"--{combo_id}.html" if not is_solo else None
    target_suffix_old = f"_{combo_id}.html" if not is_solo else None
    target_callsigns = callsigns_safe if is_solo else None
    
    for art in artifacts:
        if art['report_id'] == 'qso_rate_plots' and art['path'].endswith('.html'):
            fname = os.path.basename(art['path'])
            
            # Filter by suffix pattern
            if not is_solo:
                # Multi-log: Only include comparison plots (ending with combo_id)
                # Check both new and old formats
                if not (target_suffix_new and fname.endswith(target_suffix_new)) and not (target_suffix_old and fname.endswith(target_suffix_old)):
                    continue
            else:
                # Single-log: Only include individual station plots (ending with single callsign)
                # Exclude comparison plots (those ending with combo_id which is same as single callsign)
                # For single log, combo_id IS the callsign, so we need to check if it's exactly one callsign
                # Pattern: qso_rate_plots_{band}--{callsign}.html (new) or qso_rate_plots_{band}_{callsign}.html (old)
                matches_single = False
                for call in target_callsigns:
                    single_suffix_new = f"--{call}.html"
                    single_suffix_old = f"_{call}.html"
                    if fname.endswith(single_suffix_new) or fname.endswith(single_suffix_old):
                        matches_single = True
                        break
                if not matches_single:
                    continue
            
            # Handle new format with -- delimiter: qso_rate_plots_{band}--{callsigns}.html
            # or old format: qso_rate_plots_{band}_{callsigns}.html
            if '--' in fname:
                # New format: qso_rate_plots_all--k1lz_k3lr_w3lpl.html or qso_rate_plots_20m--k1lz_k3lr_w3lpl.html
                # Split on -- to separate band/mode from callsigns
                parts_before_dash = fname.replace('qso_rate_plots_', '').split('--')[0]
                # Extract band from first part (e.g., "all", "20m", "20m_cw", "10_cw", "10_ph")
                band_parts = parts_before_dash.split('_')
                band_key = band_parts[0].upper()
                mode_key = band_parts[1].upper() if len(band_parts) > 1 else None
            else:
                # Old format (backward compatibility): qso_rate_plots_20m_k1lz_k3lr.html
                remainder = fname.replace('qso_rate_plots_', '')
                parts = remainder.split('_')
                if parts:
                    band_key = parts[0].upper()
                    mode_key = parts[1].upper() if len(parts) > 1 else None
                else:
                    continue
            
            if band_key.isdigit(): band_key += 'M'
            
            # For single-band, multi-mode contests: use mode labels instead of band labels
            # e.g., ARRL 10: "All", "CW", "PH" instead of all showing "10"
            if is_single_band and is_multi_mode and mode_key:
                # Extract mode from filename (e.g., "10_cw" -> "CW", "10_ph" -> "PH")
                mode_upper = mode_key
                if mode_upper in ['CW', 'PH', 'RY', 'DG']:
                    label = mode_upper
                elif mode_upper in ['SSB', 'USB', 'LSB']:
                    label = 'PH'  # Cabrillo uses PH
                else:
                    label = mode_upper  # Fallback
                # Sort value will be set later by MODE_SORT_ORDER, use temp value for now
                sort_val = 50  # Temporary, will be overridden
            elif is_single_band and is_multi_mode and not mode_key:
                # "All" mode for single-band, multi-mode (e.g., "10" without mode suffix)
                label = "All"
                # Sort value will be set later by MODE_SORT_ORDER, use temp value for now
                sort_val = 50  # Temporary, will be overridden
            else:
                # Multi-band contests: use band labels
                label = "All Bands" if band_key == 'ALL' else band_key
                sort_val = BAND_SORT_ORDER.get(band_key, 99)
            
            qso_band_plots.append({
                'label': label,
                'file_html': f"{report_rel_path}/{art['path']}",
                'file_json': f"{settings.MEDIA_URL}sessions/{session_id}/{report_rel_path}/{art['path'].replace('.html', '.json')}",
                'sort_val': sort_val
            })

    # Sort: For single-band, multi-mode, sort by mode order (All first, then CW, PH, etc.)
    # For multi-band, sort by band order (All Bands first, then 20M, etc.)
    if is_single_band and is_multi_mode:
        # Define mode sort order
        MODE_SORT_ORDER = {'all': 0, 'cw': 1, 'ph': 2, 'ry': 3, 'dg': 4}
        for p in qso_band_plots:
            label_lower = p['label'].lower()
            p['sort_val'] = MODE_SORT_ORDER.get(label_lower, 99)
        qso_band_plots.sort(key=lambda x: x['sort_val'])
    else:
        qso_band_plots.sort(key=lambda x: x['sort_val'])
    
    # Default active selection
    active_set = False
    if qso_band_plots:
        # For single-band, multi-mode: prioritize "All", otherwise first available
        if is_single_band and is_multi_mode:
            for p in qso_band_plots:
                if p['label'] == 'All':
                    p['active'] = True
                    active_set = True
                    break
            if not active_set:
                qso_band_plots[0]['active'] = True
        else:
            # Multi-band: prioritize "All Bands", then 20M, then first available
            for p in qso_band_plots:
                if p['label'] == 'All Bands':
                    p['active'] = True
                    active_set = True
                    break
            if not active_set:
                for p in qso_band_plots:
                    if p['label'] == '20M':
                        p['active'] = True
                        active_set = True
                        break
            if not active_set:
                qso_band_plots[0]['active'] = True

    # Global files via manifest lookup
    # Handle both multi-band and single-band contests
    # Multi-band: qso_rate_plots_all--{callsigns}.html
    # Single-band: qso_rate_plots_{band}--{callsigns}.html (e.g., qso_rate_plots_10--{callsigns}.html)
    # Old format (backward compat): qso_rate_plots_all_{callsigns}.html
    single_band_name = valid_bands[0].replace('M', '').lower() if is_single_band else None  # e.g., "10" for "10M"
    
    if is_solo:
        # Single log: Look for qso_rate_plots_all--{callsign}.html or qso_rate_plots_{band}--{callsign}.html or old format
        call_safe = callsigns_safe[0] if callsigns_safe else combo_id
        # Try multi-band format first, then single-band format if applicable
        global_qso = next((f"{report_rel_path}/{a['path']}" for a in artifacts 
                          if a['report_id'] == 'qso_rate_plots' 
                          and (f"all--{call_safe}.html" in a['path'] or f"_all_{call_safe}.html" in a['path'])), "")
        # If not found and single-band contest, try single-band format
        if not global_qso and is_single_band and single_band_name:
            global_qso = next((f"{report_rel_path}/{a['path']}" for a in artifacts 
                              if a['report_id'] == 'qso_rate_plots' 
                              and (f"{single_band_name}--{call_safe}.html" in a['path'] or f"_{single_band_name}_{call_safe}.html" in a['path'])), "")
    else:
        # Multi log: Look for qso_rate_plots_all--{combo_id}.html or qso_rate_plots_{band}--{combo_id}.html or old format
        # Try multi-band format first, then single-band format if applicable
        global_qso = next((f"{report_rel_path}/{a['path']}" for a in artifacts 
                          if a['report_id'] == 'qso_rate_plots' 
                          and (f"all--{combo_id}.html" in a['path'] or f"_all_{combo_id}.html" in a['path'])), "")
        # If not found and single-band contest, try single-band format
        if not global_qso and is_single_band and single_band_name:
            global_qso = next((f"{report_rel_path}/{a['path']}" for a in artifacts 
                              if a['report_id'] == 'qso_rate_plots' 
                              and (f"{single_band_name}--{combo_id}.html" in a['path'] or f"_{single_band_name}_{combo_id}.html" in a['path'])), "")
    
    if not global_qso:
        logger.warning(f"QSO Dashboard: Global QSO Rate Plot not found for combo_id '{combo_id}' in '{report_rel_path}'.")

    # Strict lookup for Rate Sheet Comparison to ensure we get the full multi-log version, not a pairwise subset
    # New format: rate_sheet_comparison--{combo_id}.txt
    # Old format (backward compat): rate_sheet_comparison_{combo_id}.txt
    rate_sheet_target_new = f"rate_sheet_comparison--{combo_id}.txt"
    rate_sheet_target_old = f"rate_sheet_comparison_{combo_id}.txt"
    rate_sheet_comp = next((f"{report_rel_path}/{a['path']}" for a in artifacts 
                          if a['report_id'] == 'rate_sheet_comparison' 
                          and (a['path'].endswith(rate_sheet_target_new) or a['path'].endswith(rate_sheet_target_old))), "")
    
    if not rate_sheet_comp and not is_solo:
        logger.warning(f"QSO Dashboard: Comparative Rate Sheet not found for combo_id '{combo_id}'. Expected suffix: '{rate_sheet_target}'.")

    # Decouple base path from global_qso success. Use authoritative manifest path.
    report_base = report_rel_path

    # Diagnostic: Verify individual rate sheets exist
    for call in callsigns_safe:
        expected_rate_sheet = os.path.join(session_path, report_rel_path, f"text/rate_sheet_{call.upper()}.txt")
        if not os.path.exists(expected_rate_sheet):
            logger.warning(f"QSO Dashboard: Expected rate sheet not found: {expected_rate_sheet}")

    # Prepare valid_modes for template (similar to valid_bands_for_buttons)
    valid_modes_for_buttons = []
    if valid_modes:
        for mode in valid_modes:
            valid_modes_for_buttons.append({
                'display': mode,
                'key': mode.lower()
            })
        # Add "All" option at the beginning
        valid_modes_for_buttons.insert(0, {
            'display': 'All',
            'key': 'all'
        })

    # Determine activity tab labels based on contest type
    # Single-band, multi-mode contests (e.g., ARRL 10) should show "Mode Activity"
    # Multi-band contests should show "Band Activity"
    if is_single_band and is_multi_mode:
        activity_tab_label = 'Mode Activity'
        activity_tab_title = 'Mode Activity Butterfly Chart'
        qso_tab_label = 'QSOs by Mode'
        points_tab_label = 'Points by Mode'
        dimension_label = 'Mode'
    else:
        activity_tab_label = 'Band Activity'
        activity_tab_title = 'Band Activity Butterfly Chart'
        qso_tab_label = 'QSOs by Band'
        points_tab_label = 'Points by Band'
        dimension_label = 'Band'
    
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
        'is_solo': is_solo,
        'valid_bands': valid_bands_for_buttons,  # For dynamic band button generation
        'valid_modes': valid_modes_for_buttons,  # For dynamic mode button generation
        'diff_selector_type': diff_selector_type,  # 'band' or 'mode' for Rate Differential pane
        'activity_tab_label': activity_tab_label,  # 'Band Activity' or 'Mode Activity'
        'activity_tab_title': activity_tab_title,  # Chart title for activity tab
        'qso_tab_label': qso_tab_label,  # 'QSOs by Band' or 'QSOs by Mode'
        'points_tab_label': points_tab_label,  # 'Points by Band' or 'Points by Mode'
        'dimension_label': dimension_label  # 'Band' or 'Mode' for dropdown labels
    }
    
    return render(request, 'analyzer/qso_dashboard.html', context)

def download_all_reports(request, session_id):
    """
    Zips the 'reports' directory and original Cabrillo log files for the session.
    
    POST: Initiates zip creation with progress tracking. Returns request_id.
    GET with request_id: Serves the completed zip file.
    
    Filename format: YYYY_CONTEST_NAME.zip
    Structure:
        - reports/ (all generated reports)
        - logs/ (original Cabrillo log files)
    """
    session_path = os.path.join(settings.MEDIA_ROOT, 'sessions', session_id)
    context_path = os.path.join(session_path, 'dashboard_context.json')

    if not os.path.exists(session_path) or not os.path.exists(context_path):
        raise Http404("Session or context not found")

    # Handle GET request with request_id (serve file)
    request_id = request.GET.get('request_id')
    if request.method == 'GET' and request_id:
        zip_output_path = os.path.join(session_path, 'archive_temp.zip')
        if os.path.exists(zip_output_path):
            # Get filename from context
            try:
                with open(context_path, 'r') as f:
                    context = json.load(f)
                path_parts = context.get('report_url_path', '').split('/')
                if len(path_parts) >= 2:
                    year = _sanitize_filename_part(path_parts[0])
                    contest = _sanitize_filename_part(path_parts[1])
                    zip_filename = f"{year}_{contest}.zip"
                else:
                    zip_filename = "contest_reports.zip"
            except Exception:
                zip_filename = "contest_reports.zip"
            
            # Mark as done
            _update_progress(request_id, 3, message="Done")
            
            # Serve file
            response = FileResponse(open(zip_output_path, 'rb'), as_attachment=True, filename=zip_filename)
            return response
        else:
            raise Http404("Archive not found")

    # Handle POST request (initiate download) or GET without request_id (backward compat)
    # Generate request_id if not provided (for POST)
    if request.method == 'POST':
        request_id = request.POST.get('request_id') or f"zip_{uuid.uuid4().hex[:12]}"
    else:
        # Backward compatibility: direct GET serves file immediately (no progress)
        request_id = None

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

    # 2. Verify Required Directories/Files
    reports_root = os.path.join(session_path, 'reports')
    if not os.path.exists(reports_root):
        raise Http404("No reports found to archive")

    # 3. Find and Count Files
    log_extensions = ('.log', '.cbr', '.txt')
    log_files = []
    excluded_files = {'dashboard_context.json', 'session_manifest.json', 'archive_temp.zip'}
    
    if os.path.exists(session_path):
        for item in os.listdir(session_path):
            item_path = os.path.join(session_path, item)
            # Only include files (not directories) with log extensions
            if os.path.isfile(item_path) and item.lower().endswith(log_extensions):
                # Exclude known non-log files
                if item not in excluded_files:
                    log_files.append((item, item_path))
    
    # Count report files
    report_file_count = 0
    reports_dir = os.path.join(session_path, 'reports')
    if os.path.exists(reports_dir):
        for root, dirs, files in os.walk(reports_dir):
            report_file_count += len(files)
    
    total_file_count = report_file_count + len(log_files)
    
    # Update progress: Step 1 - Zipping
    if request_id:
        _update_progress(request_id, 1, message="Zipping...", file_count=total_file_count)
    
    # 4. Warning if no log files found
    if not log_files:
        logger.warning(f"download_all_reports: No Cabrillo log files found in session {session_id}. "
                      f"Expected files with extensions: {log_extensions}")
    else:
        logger.info(f"download_all_reports: Found {len(log_files)} log file(s) to include in archive")

    # 5. Create Zip Archive using zipfile for more control
    zip_output_path = os.path.join(session_path, 'archive_temp.zip')
    
    try:
        with zipfile.ZipFile(zip_output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add reports directory (recursive)
            if os.path.exists(reports_dir):
                for root, dirs, files in os.walk(reports_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Calculate relative path from session_path
                        arcname = os.path.relpath(file_path, session_path)
                        zipf.write(file_path, arcname)
                        logger.debug(f"Added to archive: {arcname}")
            
            # Add log files to logs/ subdirectory
            if log_files:
                for log_name, log_path in log_files:
                    # Store in logs/ subdirectory in ZIP
                    arcname = os.path.join('logs', log_name)
                    zipf.write(log_path, arcname)
                    logger.debug(f"Added log to archive: {arcname}")
            else:
                # Create empty logs directory marker (optional, but helps with structure)
                logger.warning(f"Archive created without log files - logs/ directory will be empty")
        
        # Update progress: Step 2 - Downloading (file ready)
        if request_id:
            download_url = f"/report/{session_id}/download_all/?request_id={request_id}"
            _update_progress(request_id, 2, message="Downloading...", file_count=total_file_count, download_url=download_url)
        
        # If POST, return request_id. If GET (backward compat), serve file immediately.
        if request.method == 'POST':
            return JsonResponse({'request_id': request_id, 'status': 'ready'})
        else:
            # Backward compatibility: serve file immediately
            response = FileResponse(open(zip_output_path, 'rb'), as_attachment=True, filename=zip_filename)
            return response
        
    except Exception as e:
        logger.error(f"Failed to create archive for session {session_id}: {e}")
        # Clean up partial zip if it exists
        if os.path.exists(zip_output_path):
            try:
                os.remove(zip_output_path)
            except:
                pass
        raise Http404("Failed to generate archive")

def help_about(request):
    """Renders the About / Intro page."""
    from contest_tools.version import __version__
    return render(request, 'analyzer/about.html', {'version': __version__})

def help_dashboard(request):
    """Renders the Dashboard Help page."""
    return render(request, 'analyzer/help_dashboard.html')

def help_reports(request):
    """Renders the Report Interpretation Guide."""
    return render(request, 'analyzer/help_reports.html')

def help_release_notes(request):
    """Renders CHANGELOG.md as HTML."""
    import markdown
    from contest_tools.version import __version__
    
    # BASE_DIR is 'web_app/' (Path object)
    # In Docker: /app/web_app/
    # Project root is BASE_DIR.parent: /app/
    # Convert Path to string for os.path.join() compatibility
    project_root = str(settings.BASE_DIR.parent)
    changelog_path = os.path.join(project_root, 'CHANGELOG.md')
    
    # DIAGNOSTICS: Log the path being checked
    logger.error(f"[DIAG] help_release_notes: BASE_DIR={settings.BASE_DIR}, project_root={project_root}, changelog_path={changelog_path}")
    
    try:
        with open(changelog_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert markdown to HTML with extensions for better formatting
        html_content = markdown.markdown(
            md_content, 
            extensions=['fenced_code', 'tables', 'nl2br']
        )
    except FileNotFoundError:
        logger.warning(f"CHANGELOG.md not found at {changelog_path}")
        html_content = "<div class='alert alert-warning'><p>Release notes are currently unavailable.</p></div>"
    except Exception as e:
        logger.error(f"Error reading CHANGELOG.md: {e}")
        html_content = "<div class='alert alert-danger'><p>Error loading release notes.</p></div>"
    
    return render(request, 'analyzer/help_release_notes.html', {
        'changelog_html': html_content,
        'version': __version__
    })