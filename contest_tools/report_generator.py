# Contest Log Analyzer/contest_tools/report_generator.py
#
# Purpose: This class orchestrates the generation of reports. It takes a list
#          of loaded ContestLog objects and user-specified options, then uses
#          the properties of each available report class to determine how to
#          execute it (e.g., single-log, pairwise, multi-log).
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-04
# Version: 0.28.15-Beta
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
# All notable changes to this project will be documented in this file.
# The format is based on "Keep a Changelog" (https://keepachangelog.com/en/1.0.0/),
# and this project aims to adhere to Semantic Versioning (https://semver.org/).
## [0.28.15-Beta] - 2025-08-04
### Fixed
# - The main report generation loop now correctly skips multiplier reports,
#   fixing the "'mult_name' argument is required" error.
## [0.28.14-Beta] - 2025-08-04
### Fixed
# - Corrected the auto-generation logic to correctly handle reports that
#   support both single and multi-log modes (e.g., multiplier_summary).
import os
import itertools
from .reports import AVAILABLE_REPORTS

class ReportGenerator:
    """
    Handles the logic of selecting, configuring, and running one or more reports.
    """
    def __init__(self, logs, output_base_dir="reports_output"):
        """
        Initializes the ReportGenerator.

        Args:
            logs (list): A list of loaded ContestLog objects.
            output_base_dir (str): The root directory for report output.
        """
        if not logs:
            raise ValueError("ReportGenerator must be initialized with at least one log.")
        self.logs = logs
        
        # --- Define Output Directory Structure ---
        first_log = self.logs[0]
        contest_name = first_log.get_metadata().get('ContestName', 'UnknownContest').replace(' ', '_')
        
        first_qso_date = first_log.get_processed_data()['Date'].dropna().iloc[0] if not first_log.get_processed_data().empty and not first_log.get_processed_data()['Date'].dropna().empty else None
        year = first_qso_date.split('-')[0] if first_qso_date else "UnknownYear"

        self.base_output_dir = os.path.join(output_base_dir, year, contest_name)
        self.text_output_dir = os.path.join(self.base_output_dir, "text")
        self.plots_output_dir = os.path.join(self.base_output_dir, "plots")
        self.charts_output_dir = os.path.join(self.base_output_dir, "charts")

    def run_reports(self, report_id, **report_kwargs):
        """
        Executes the requested reports based on the report_id and options.

        Args:
            report_id (str): The ID of the report to run, or 'all'.
            **report_kwargs: A dictionary of options to pass to the reports.
        """
        reports_to_run = []
        if report_id.lower() == 'all':
            reports_to_run = AVAILABLE_REPORTS.items()
        elif report_id in AVAILABLE_REPORTS:
            reports_to_run = [(report_id, AVAILABLE_REPORTS[report_id])]
        else:
            print(f"Error: Report '{report_id}' not found.")
            return

        # --- This entire block is the logic moved from main_cli.py ---
        for r_id, ReportClass in reports_to_run:
            first_log = self.logs[0]
            excluded = first_log.contest_definition.excluded_reports
            if r_id in excluded:
                print(f"\nSkipping report '{ReportClass.report_name}': Excluded by contest definition.")
                continue

            report_type = ReportClass.report_type
            
            if report_type == 'text': output_path = self.text_output_dir
            elif report_type == 'plot': output_path = self.plots_output_dir
            elif report_type == 'chart': output_path = self.charts_output_dir
            else: output_path = self.base_output_dir

            # --- Auto-generate reports for each multiplier type if needed ---
            is_multiplier_report = r_id in ['missed_multipliers', 'multiplier_summary', 'multipliers_by_hour']
            
            if is_multiplier_report and not report_kwargs.get('mult_name'):
                print(f"\nAuto-generating '{ReportClass.report_name}' for all available multiplier types...")
                
                first_log = self.logs[0]
                log_location_type = first_log._my_location_type
                all_rules = first_log.contest_definition.multiplier_rules
                
                applicable_rules = []
                if log_location_type: # This is an asymmetric contest
                    for rule in all_rules:
                        applies_to = rule.get('applies_to')
                        if applies_to is None or applies_to == log_location_type:
                            applicable_rules.append(rule)
                else: # This is a standard contest
                    applicable_rules = all_rules

                for mult_rule in applicable_rules:
                    mult_name = mult_rule.get('name')
                    if mult_name:
                        print(f"  - Generating for: {mult_name}")
                        current_kwargs = report_kwargs.copy()
                        current_kwargs['mult_name'] = mult_name
                        
                        # Handle single-log reports
                        if ReportClass.supports_single:
                            for log in self.logs:
                                instance = ReportClass([log])
                                result = instance.generate(output_path=output_path, **current_kwargs)
                                print(result)
                        
                        # Handle multi-log and pairwise reports
                        if (ReportClass.supports_multi or ReportClass.supports_pairwise):
                            if len(self.logs) < 2:
                                print(f"    - Skipping comparative version: Requires at least two logs.")
                                continue
                            
                            instance = ReportClass(self.logs)
                            result = instance.generate(output_path=output_path, **current_kwargs)
                            print(result)
            
            # --- Handle report generation based on comparison mode ---
            else:
                # Explicitly skip multiplier reports in this generic section
                if is_multiplier_report:
                    continue

                print(f"\nGenerating report: '{ReportClass.report_name}'...")
                
                if ReportClass.supports_multi and len(self.logs) >= 2:
                    instance = ReportClass(self.logs)
                    result = instance.generate(output_path=output_path, **report_kwargs)
                    print(result)

                if ReportClass.supports_pairwise and len(self.logs) >= 2:
                    for log_pair in itertools.combinations(self.logs, 2):
                        instance = ReportClass(list(log_pair))
                        result = instance.generate(output_path=output_path, **report_kwargs)
                        print(result)
                
                if ReportClass.supports_single:
                    for log in self.logs:
                        instance = ReportClass([log])
                        result = instance.generate(output_path=output_path, **report_kwargs)
                        print(result)