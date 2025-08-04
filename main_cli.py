# Contest Log Analyzer/main_cli.py
#
# Purpose: This is the main command-line interface (CLI) entry point for the
#          Contest Log Analyzer. It now handles multiple log files and can
#          generate specific reports.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-04
# Version: 0.26.4-Beta
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
## [0.26.4-Beta] - 2025-08-04
### Fixed
# - Corrected the call to `log_manager.load_log` to pass the correct
#   number of arguments, fixing a TypeError.
## [0.26.3-Beta] - 2025-08-02
### Fixed
# - Corrected the usage guide to access 'report_name' as a direct
#   class attribute instead of a property, fixing an 'AttributeError'.
import sys
import os
import argparse
from contest_tools.log_manager import LogManager
from contest_tools.reports import AVAILABLE_REPORTS
from contest_tools.report_generator import ReportGenerator

def print_usage_guide():
    """Prints the command-line usage guide."""
    print("\nUsage: python main_cli.py --report <ReportID|all> <LogFilePath1> [<LogFile2>...] [options]")
    print("\nOptions:")
    print("  --include-dupes         Include duplicate QSOs in calculations.")
    print("  --mult-name <name>      Specify multiplier for reports (e.g., 'Countries', 'Zones').")
    print("  --metric <qsos|points>  Specify metric for difference plots (defaults to 'qsos').")
    
    print("\nAvailable Reports:")
    max_id_len = max(len(rid) for rid in AVAILABLE_REPORTS.keys())
    for report_id, report_class in sorted(AVAILABLE_REPORTS.items()):
        print(f"  {report_id:<{max_id_len}} : {report_class.report_name}")
    print("")

def main():
    """Main function to parse arguments and run the analyzer."""
    
    # --- Custom Argument Parser ---
    class CustomArgumentParser(argparse.ArgumentParser):
        def error(self, message):
            sys.stderr.write(f'Error: {message}\n')
            print_usage_guide()
            sys.exit(2)

    parser = CustomArgumentParser(description="Contest Log Analyzer", add_help=False)
    
    # --- Define Arguments ---
    parser.add_argument('log_filepaths', nargs='*', help="Paths to Cabrillo log files.")
    parser.add_argument('--report', '-r', dest='report_id', help="The ID of the report to generate, or 'all'.")
    parser.add_argument('--include-dupes', action='store_true', help="Include duplicate QSOs in calculations.")
    parser.add_argument('--mult-name', dest='mult_name', help="Specify the multiplier name for relevant reports.")
    parser.add_argument('--metric', dest='metric', choices=['qsos', 'points'], default='qsos', help="Metric for difference plots.")
    
    # --- Parse Known and Unknown Args ---
    args, unknown = parser.parse_known_args()

    # --- Argument Validation ---
    if unknown:
        print(f"Error: Unrecognized arguments: {' '.join(unknown)}")
        print_usage_guide()
        return

    if not args.log_filepaths:
        print("Error: At least one log file path must be provided.")
        print_usage_guide()
        return

    if not args.report_id:
        print("Error: The --report argument is required.")
        print_usage_guide()
        return

    if args.report_id.lower() != 'all' and args.report_id not in AVAILABLE_REPORTS:
        print(f"Error: Report '{args.report_id}' not found.")
        print_usage_guide()
        return
        
    if 'CONTEST_DATA_DIR' not in os.environ:
        print("Error: The CONTEST_DATA_DIR environment variable is not set.")
        print("Please set it to the directory containing your cty.dat and other data files.")
        return

    # --- Main Application Logic ---
    print("\n--- Contest Log Analyzer ---")
    log_manager = LogManager()
    
    for path in args.log_filepaths:
        log_manager.load_log(path)
    
    log_manager.finalize_loading()
    
    report_kwargs = {
        'include_dupes': args.include_dupes,
        'mult_name': args.mult_name,
        'metric': args.metric
    }

    generator = ReportGenerator(logs=log_manager.get_logs())
    generator.run_reports(args.report_id, **report_kwargs)
    
    print("\n--- Done ---")

if __name__ == '__main__':
    main()