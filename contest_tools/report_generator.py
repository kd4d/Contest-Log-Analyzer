# contest_tools/report_generator.py
#
# Purpose: This class orchestrates the generation of reports.
#          It takes a list of loaded ContestLog objects and user-specified options,
#          then uses the properties of each available report class to determine how to
#          execute it (e.g., single-log, pairwise, multi-log).
#
# Author: Gemini AI
# Date: 2026-01-05
# Version: 0.164.1-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
#
# License: Mozilla Public License, v. 2.0
#          ([https://www.mozilla.org/MPL/2.0/](https://www.mozilla.org/MPL/2.0/))
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0.
# If a copy of the MPL was not distributed with this
# file, You can obtain one at [http://mozilla.org/MPL/2.0/](http://mozilla.org/MPL/2.0/).
#
# --- Revision History ---
# [0.164.1-Beta] - 2026-01-05
# - Added pairwise iteration loop for multiplier reports when > 2 logs are present.
# [0.163.0-Beta] - 2026-01-05
# - Enforced strict filename sanitization for callsign directory components to match report suffix logic.
# [0.134.1-Beta] - 2025-12-20
# - Removed redundant local 'import os' to fix NameError in nested helper.
# [0.134.0-Beta] - 2025-12-20
# - Integrated ManifestManager to track generated artifacts.
# - Implemented directory snapshot logic to decouple report generation from file discovery.
# [0.113.0-Beta] - 2025-12-13
# - Enforced strict lowercase sanitization for all output directory paths (contest, event, callsigns).
# [0.107.0-Beta] - 2025-12-13
# - Removed 'html' output directory support to enforce semantic routing.
# - Removed temporary debug logging and traceback imports.
# [0.106.0-Beta] - 2025-12-13
# - Added Systemic Directory Scaffolding (os.makedirs) to run_reports to prevent
#   FileNotFoundError in dynamic session environments.
# [0.91.1-Beta] - 2025-10-10
# - Implemented hybrid "opt-in/opt-out" report model to handle
#   specialized, contest-specific reports.
# [0.90.0-Beta] - 2025-10-01
# - Set new baseline version for release.

import os
import itertools
import importlib
import logging
import pandas as pd
from .reports import AVAILABLE_REPORTS
from .manifest_manager import ManifestManager
from .utils.report_utils import _sanitize_filename_part

class ReportGenerator:
    """
    Handles the logic of selecting, configuring, and running one or more reports.
    """
    def __init__(self, logs, root_output_dir="reports"):
        """
        Initializes the ReportGenerator and creates the unique output directory path.

        Args:
            logs (list): A list of loaded ContestLog objects.
            root_output_dir (str): The root directory for all report output.
        """
        if not logs:
            raise ValueError("ReportGenerator must be initialized with at least one log.")
        self.logs = logs
        
        # --- Define Fully Unique Output Directory Structure ---
        
        first_log = self.logs[0]
        contest_name = first_log.get_metadata().get('ContestName', 'UnknownContest').replace(' ', '_').lower()
        
        df = first_log.get_processed_data()
        year = df['Date'].dropna().iloc[0].split('-')[0] if not df.empty and not df['Date'].dropna().empty else "UnknownYear"

        # --- Get Event ID from Resolver (if defined) ---
        event_id = ""
        resolver_name = first_log.contest_definition.contest_specific_event_id_resolver
        if resolver_name:
            try:
                resolver_module = importlib.import_module(f"contest_tools.event_resolvers.{resolver_name}")
                first_qso_time = df['Datetime'].iloc[0]
                event_id = resolver_module.resolve_event_id(first_qso_time)
            except (ImportError, AttributeError, IndexError) as e:
                logging.warning(f"Could not run event ID resolver '{resolver_name}': {e}")
                event_id = "UnknownEvent"

        # --- Get Callsign Combination ID ---
        all_calls = sorted([log.get_metadata().get('MyCall', f'Log{i+1}') for i, log in enumerate(self.logs)])
        callsign_combo_id = '_'.join([_sanitize_filename_part(c) for c in all_calls])

        # --- Construct Final Path ---
        self.base_output_dir = os.path.join(root_output_dir, 'reports', year, contest_name, event_id.lower(), callsign_combo_id)
        self.text_output_dir = os.path.join(self.base_output_dir, "text")
        self.plots_output_dir = os.path.join(self.base_output_dir, "plots")
        self.charts_output_dir = os.path.join(self.base_output_dir, "charts")
        self.animations_output_dir = os.path.join(self.base_output_dir, "animations")
        
        self.manifest = ManifestManager(self.base_output_dir)

    def run_reports(self, report_id, **report_kwargs):
        """
        Executes the requested reports based on the report_id and options.
        """
        reports_to_run = []
        report_id_lower = report_id.lower()

        if report_id_lower == 'all':
            reports_to_run = list(AVAILABLE_REPORTS.items())
        elif report_id_lower in ['chart', 'text', 'plot', 'animation', 'html']:
            reports_to_run = [
                (r_id, RClass) for r_id, RClass in AVAILABLE_REPORTS.items()
                if RClass.report_type == report_id_lower
            ]
        elif report_id in AVAILABLE_REPORTS:
            reports_to_run = [(report_id, AVAILABLE_REPORTS[report_id])]
        else:
            logging.error(f"Report '{report_id}' not found.")
            return

        if not reports_to_run:
            logging.warning(f"No reports found for category '{report_id}'.")
            return

        first_log = self.logs[0]
        contest_def = first_log.contest_definition
        included_reports = contest_def.included_reports

        # Filter out excluded reports before iterating
        final_reports_to_run = [
            (r_id, RClass) for r_id, RClass in reports_to_run
            if (
                r_id not in contest_def.excluded_reports and
                (not RClass.is_specialized or r_id in included_reports)
            )
        ]

        def get_all_files(directory):
            """Helper to recursively list all files in the output directory."""
            file_set = set()
            if not os.path.exists(directory):
                return file_set
            for root, dirs, files in os.walk(directory):
                for file in files:
                    # Store path relative to the base output dir
                    rel_path = os.path.relpath(os.path.join(root, file), self.base_output_dir)
                    file_set.add(rel_path)
            return file_set

        # Initial snapshot
        files_before = get_all_files(self.base_output_dir)

        for r_id, ReportClass in final_reports_to_run:
            report_type = ReportClass.report_type
            if report_type == 'text': output_path = self.text_output_dir
            elif report_type == 'plot': output_path = self.plots_output_dir
            elif report_type == 'chart': output_path = self.charts_output_dir
            elif report_type == 'animation': output_path = self.animations_output_dir
            else: output_path = self.base_output_dir

            # --- SYSTEMIC FIX: Scaffold Output Directory ---
            # Ensures the specific report type sub-directory (e.g., /plots) exists
            # before passing it to the plugin. Required for dynamic sessions.
            os.makedirs(output_path, exist_ok=True)

            is_multiplier_report = r_id in ['missed_multipliers', 'multiplier_summary', 'multipliers_by_hour']

            # --- MUTUALLY EXCLUSIVE LOGIC PATHS ---
            if is_multiplier_report:
                # --- Path 1: Multiplier Reports ---
                log_location_type = first_log._my_location_type
                all_rules = contest_def.multiplier_rules
                applicable_rules = [r for r in all_rules if r.get('applies_to') is None or r.get('applies_to') == log_location_type]
                
                mult_rules_to_run = []
                user_spec_mult = report_kwargs.get('mult_name')
                if user_spec_mult:
                    rule = next((r for r in applicable_rules if r.get('name', '').lower() == user_spec_mult.lower()), None)
                    if rule:
                        mult_rules_to_run.append(rule)
                else:
                    mult_rules_to_run = applicable_rules

                modes_to_run = [None] # Default for non-per-mode contests
                if contest_def.multiplier_report_scope == 'per_mode':
                    modes_to_run = pd.concat([log.get_processed_data()['Mode'] for log in self.logs]).dropna().unique()

                logging.info(f"\nGenerating report: '{ReportClass.report_name}'...")
                for mode in modes_to_run:
                    if mode:
                        logging.info(f"--- Analyzing Mode: {mode} ---")
                    
                    for mult_rule in mult_rules_to_run:
                        mult_name = mult_rule.get('name')
                        if not mult_name:
                            continue

                        logging.info(f"  - Generating for: {mult_name}")
                        current_kwargs = report_kwargs.copy()
                        current_kwargs['mult_name'] = mult_name
                        if mode:
                            current_kwargs['mode_filter'] = mode
                        
                        if ReportClass.supports_single:
                            for log in self.logs:
                                instance = ReportClass([log])
                                try:
                                    result = instance.generate(output_path=output_path, **current_kwargs)
                                    logging.info(result)
                                except Exception as e:
                                    logging.error(f"Error generating '{r_id}': {e}")
                        
                        if (ReportClass.supports_multi or ReportClass.supports_pairwise) and len(self.logs) >= 2:
                            # 1. Generate Session Summary (All Logs)
                            instance = ReportClass(self.logs)
                            try:
                                result = instance.generate(output_path=output_path, **current_kwargs)
                                logging.info(result)
                            except Exception as e:
                                logging.error(f"Error generating '{r_id}' (Session): {e}")

                            # 2. Generate Pairwise Comparisons (if > 2 logs)
                            if ReportClass.supports_pairwise and len(self.logs) > 2:
                                for log_pair in itertools.combinations(self.logs, 2):
                                    instance = ReportClass(list(log_pair))
                                    try:
                                        result = instance.generate(output_path=output_path, **current_kwargs)
                                        logging.info(result)
                                    except Exception as e:
                                        logging.error(f"Error generating '{r_id}' (Pair): {e}")
            
            else:
                # --- Path 2: Non-Multiplier Reports ---
                logging.info(f"\nGenerating report: '{ReportClass.report_name}'...")
                
                if ReportClass.supports_multi and len(self.logs) >= 2:
                    instance = ReportClass(self.logs)
                    try:
                        result = instance.generate(output_path=output_path, **report_kwargs)
                        logging.info(result)
                    except Exception as e:
                        logging.error(f"Error generating '{r_id}': {e}")

                if ReportClass.supports_pairwise and len(self.logs) >= 2:
                    for log_pair in itertools.combinations(self.logs, 2):
                        instance = ReportClass(list(log_pair))
                        try:
                            result = instance.generate(output_path=output_path, **report_kwargs)
                            logging.info(result)
                        except Exception as e:
                            logging.error(f"Error generating '{r_id}': {e}")

                if ReportClass.supports_single:
                    for log in self.logs:
                        instance = ReportClass([log])
                        try:
                            result = instance.generate(output_path=output_path, **report_kwargs)
                            logging.info(result)
                        except Exception as e:
                            logging.error(f"Error generating '{r_id}': {e}")

            # --- Post-Execution Snapshot ---
            # Detect new files generated by this specific report ID
            files_now = get_all_files(self.base_output_dir)
            new_files = files_now - files_before
            for new_file in new_files:
                self.manifest.add_artifact(r_id, new_file, report_type)
            files_before = files_now # Update baseline
            
        self.manifest.save()