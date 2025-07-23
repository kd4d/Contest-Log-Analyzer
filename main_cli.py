# Contest Log Analyzer/main_cli.py
#
# Purpose: This is the main command-line interface (CLI) entry point for the
#          Contest Log Analyzer. It now handles multiple log files and can
#          generate specific reports.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-22
# Version: 0.14.1-Beta
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

## [0.14.1-Beta] - 2025-07-22
### Changed
# - The '--report all' command now automatically generates the cumulative
#   difference plots for both QSOs and Points.

## [0.14.0-Beta] - 2025-07-22
### Changed
# - Added an optional '--metric <qsos|points>' flag to the command line to
#   specify the metric for the cumulative difference plot.

import sys
import os
from contest_tools.log_manager import LogManager
from contest_tools.reports import AVAILABLE_REPORTS

def main():
    """
    Main function to run the contest log analyzer from the command line.
    """
    print("--- Contest Log Analyzer ---")

    # --- Argument Parsing ---
    args = sys.argv[1:]
    report_kwargs = {}

    if '--include-dupes' in args:
        report_kwargs['include_dupes'] = True
        args.remove('--include-dupes')
    
    if '--mult-type' in args:
        try:
            mt_index = args.index('--mult-type')
            mult_type = args[mt_index + 1].lower()
            if mult_type not in ['dxcc', 'wae']:
                raise ValueError("Multiplier type must be 'dxcc' or 'wae'.")
            report_kwargs['mult_type'] = mult_type
            args.pop(mt_index)
            args.pop(mt_index)
        except (IndexError, ValueError) as e:
            print(f"\nError with --mult-type argument: {e}")
            sys.exit(1)

    if '--mult-name' in args:
        try:
            mn_index = args.index('--mult-name')
            mult_name = args[mn_index + 1]
            report_kwargs['mult_name'] = mult_name
            args.pop(mn_index)
            args.pop(mn_index)
        except IndexError:
            print(f"\nError: --mult-name flag requires a value (e.g., 'Countries').")
            sys.exit(1)
            
    if '--metric' in args:
        try:
            m_index = args.index('--metric')
            metric = args[m_index + 1].lower()
            if metric not in ['qsos', 'points']:
                raise ValueError("Metric type must be 'qsos' or 'points'.")
            report_kwargs['metric'] = metric
            args.pop(m_index)
            args.pop(m_index)
        except (IndexError, ValueError) as e:
            print(f"\nError with --metric argument: {e}")
            sys.exit(1)

    if len(args) < 2 or args[0] != '--report':
        print("\nUsage: python main_cli.py --report <ReportID|all> <LogFilePath1>... [options]")
        print("\nOptions:")
        print("  --include-dupes         Include duplicate QSOs in calculations.")
        print("  --mult-type <dxcc|wae>  Specify multiplier set for reports (e.g., 'wae').")
        print("  --mult-name <name>      Specify multiplier for reports (e.g., 'Countries', 'Zones').")
        print("  --metric <qsos|points>  Specify metric for difference plots (defaults to 'qsos').")
        print("\nNote: The CTY_DAT_PATH environment variable must be set to the location of your cty.dat file.")
        print("      For some contests (e.g., CQ-WW), a specific country file (e.g., cqww.cty) must")
        print("      be present in the same directory as cty.dat.")
        
        if AVAILABLE_REPORTS:
            print("\nAvailable reports:")
            for report_id, report_class in AVAILABLE_REPORTS.items():
                print(f"  - {report_id}: {report_class.report_name.fget(None)}")
        else:
            print("\nNo reports found.")
            
        sys.exit(1)

    report_id = args[1]
    log_filepaths = args[2:]

    # --- Input Validation ---
    if report_id.lower() != 'all' and report_id not in AVAILABLE_REPORTS:
        print(f"\nError: Report '{report_id}' not found.")
        sys.exit(1)

    if 'CTY_DAT_PATH' not in os.environ:
        print("\nError: The CTY_DAT_PATH environment variable is not set.")
        sys.exit(1)

    # --- Processing ---
    try:
        log_manager = LogManager()
        for path in log_filepaths:
            log_manager.load_log(path)
        
        logs = log_manager.get_all_logs()
        if not logs:
            print("\nError: No logs were successfully loaded. Aborting report generation.")
            sys.exit(1)

        reports_to_run = []
        if report_id.lower() == 'all':
            reports_to_run = AVAILABLE_REPORTS.items()
        else:
            reports_to_run = [(report_id, AVAILABLE_REPORTS[report_id])]
        
        # --- Define Output Directory Structure ---
        first_log = logs[0]
        contest_name = first_log.get_metadata().get('ContestName', 'UnknownContest').replace(' ', '_')
        
        first_qso_date = first_log.get_processed_data()['Date'].iloc[0]
        year = first_qso_date.split('-')[0] if first_qso_date else "UnknownYear"

        base_output_dir = os.path.join("reports_output", year, contest_name)
        text_output_dir = os.path.join(base_output_dir, "text")
        plots_output_dir = os.path.join(base_output_dir, "plots")
        
        # Generate the selected reports
        for r_id, ReportClass in reports_to_run:
            report_instance = ReportClass(logs)
            
            output_path = text_output_dir if report_instance.report_type == 'text' else plots_output_dir

            # --- Special Handling for Auto-Generating Multiple Report Variations ---
            if r_id == 'missed_multipliers' and 'mult_name' not in report_kwargs:
                print(f"\nAuto-generating '{report_instance.report_name}' for all available multiplier types...")
                for mult_rule in first_log.contest_definition.multiplier_rules:
                    mult_name = mult_rule.get('name')
                    if mult_name:
                        print(f"  - Generating for: {mult_name}")
                        current_kwargs = report_kwargs.copy()
                        current_kwargs['mult_name'] = mult_name
                        result = report_instance.generate(output_path=output_path, **current_kwargs)
                        print(result)
            elif r_id == 'cumulative_difference_plots' and 'metric' not in report_kwargs:
                print(f"\nAuto-generating '{report_instance.report_name}' for all available metrics...")
                for metric in ['qsos', 'points']:
                    print(f"  - Generating for: {metric.capitalize()}")
                    current_kwargs = report_kwargs.copy()
                    current_kwargs['metric'] = metric
                    result = report_instance.generate(output_path=output_path, **current_kwargs)
                    print(result)
            else:
                print(f"\nGenerating report: '{report_instance.report_name}'...")
                result = report_instance.generate(output_path=output_path, **report_kwargs)
                print(result)

        print("\n--- Done ---")

    except Exception as e:
        print(f"\nAn unexpected critical error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
