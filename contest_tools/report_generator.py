# Contest Log Analyzer/contest_tools/report_generator.py
#
# Purpose: This class orchestrates the generation of reports. It takes a list
#          of loaded ContestLog objects and user-specified options, then uses
#          the properties of each available report class to determine how to
#          execute it (e.g., single-log, pairwise, multi-log).
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-05
# Version: 0.30.0-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# --- Revision History ---
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
# - Standardized all project files to a common baseline version.
import os
import itertools
import importlib
import logging
from .reports import AVAILABLE_REPORTS

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
        contest_name = first_log.get_metadata().get('ContestName', 'UnknownContest').replace(' ', '_')
        
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
        callsign_combo_id = '_'.join(all_calls)

        # --- Construct Final Path ---
        self.base_output_dir = os.path.join(root_output_dir, year, contest_name, event_id, callsign_combo_id)
        self.text_output_dir = os.path.join(self.base_output_dir, "text")
        self.plots_output_dir = os.path.join(self.base_output_dir, "plots")
        self.charts_output_dir = os.path.join(self.base_output_dir, "charts")

    def run_reports(self, report_id, **report_kwargs):
        """
        Executes the requested reports based on the report_id and options.
        """
        reports_to_run = []
        if report_id.lower() == 'all':
            reports_to_run = AVAILABLE_REPORTS.items()
        elif report_id in AVAILABLE_REPORTS:
            reports_to_run = [(report_id, AVAILABLE_REPORTS[report_id])]
        else:
            logging.error(f"Report '{report_id}' not found.")
            return

        for r_id, ReportClass in reports_to_run:
            first_log = self.logs[0]
            excluded = first_log.contest_definition.excluded_reports
            if r_id in excluded:
                logging.info(f"\nSkipping report '{ReportClass.report_name}': Excluded by contest definition.")
                continue

            report_type = ReportClass.report_type
            
            if report_type == 'text': output_path = self.text_output_dir
            elif report_type == 'plot': output_path = self.plots_output_dir
            elif report_type == 'chart': output_path = self.charts_output_dir
            else: output_path = self.base_output_dir

            is_multiplier_report = r_id in ['missed_multipliers', 'multiplier_summary', 'multipliers_by_hour']
            
            if is_multiplier_report and not report_kwargs.get('mult_name'):
                logging.info(f"\nAuto-generating '{ReportClass.report_name}' for all available multiplier types...")
                
                log_location_type = first_log._my_location_type
                all_rules = first_log.contest_definition.multiplier_rules
                
                applicable_rules = []
                if log_location_type:
                    for rule in all_rules:
                        applies_to = rule.get('applies_to')
                        if applies_to is None or applies_to == log_location_type:
                            applicable_rules.append(rule)
                else:
                    applicable_rules = all_rules

                for mult_rule in applicable_rules:
                    mult_name = mult_rule.get('name')
                    if mult_name:
                        logging.info(f"  - Generating for: {mult_name}")
                        current_kwargs = report_kwargs.copy()
                        current_kwargs['mult_name'] = mult_name
                        
                        if ReportClass.supports_single:
                            for log in self.logs:
                                instance = ReportClass([log])
                                result = instance.generate(output_path=output_path, **current_kwargs)
                                logging.info(result)
                        
                        if (ReportClass.supports_multi or ReportClass.supports_pairwise):
                            if len(self.logs) < 2:
                                logging.info(f"    - Skipping comparative version: Requires at least two logs.")
                                continue
                            
                            instance = ReportClass(self.logs)
                            result = instance.generate(output_path=output_path, **current_kwargs)
                            logging.info(result)
            
            else:
                if is_multiplier_report:
                    continue

                logging.info(f"\nGenerating report: '{ReportClass.report_name}'...")
                
                if ReportClass.supports_multi and len(self.logs) >= 2:
                    instance = ReportClass(self.logs)
                    result = instance.generate(output_path=output_path, **report_kwargs)
                    logging.info(result)

                if ReportClass.supports_pairwise and len(self.logs) >= 2:
                    for log_pair in itertools.combinations(self.logs, 2):
                        instance = ReportClass(list(log_pair))
                        result = instance.generate(output_path=output_path, **report_kwargs)
                        logging.info(result)
                
                if ReportClass.supports_single:
                    for log in self.logs:
                        instance = ReportClass([log])
                        result = instance.generate(output_path=output_path, **report_kwargs)
                        logging.info(result)
