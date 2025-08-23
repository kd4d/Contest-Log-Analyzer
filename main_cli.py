# Contest Log Analyzer/main_cli.py
#
# Purpose: This is the main command-line interface (CLI) entry point for the
#          Contest Log Analyzer. It now handles multiple log files and can
#          generate specific reports.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-21
# Version: 0.39.0-Beta
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
## [0.39.0-Beta] - 2025-08-21
### Added
# - Added a --debug-mults flag to generate diagnostic files for debugging
#   multiplier counting inconsistencies in text reports.
## [0.38.0-Beta] - 2025-08-18
### Added
# - Added a --debug-data flag to enable the generation of debug data dumps for visual reports.
## [0.35.10-Beta] - 2025-08-14
### Fixed
# - Added exception handling for log file mismatches (wrong contest/event)
#   to ensure a graceful exit.
import sys
import os
import argparse
import logging
from Utils.logger_config import setup_logging
from contest_tools.log_manager import LogManager
from contest_tools.reports import AVAILABLE_REPORTS
from contest_tools.report_generator import ReportGenerator

def handle_error(error_type: str, problem: str, solution: str, path: str = ""):
    """Logs a structured error message and prints the usage guide."""
    logging.error("\n" + "="*60)
    logging.error(f"[{error_type}]")
    logging.error(f"Problem:  {problem}")
    if path:
        logging.error(f"Path:     {path}")
    logging.error(f"Solution: {solution}")
    logging.error("="*60)
    print_usage_guide()
    sys.exit(1)

def print_usage_guide():
    """Prints the command-line usage guide."""
    print("\nUsage: python main_cli.py --report <ReportID|all|chart|text|plot> <LogFilePath1> [<LogFile2>...] [options]")
    print("\nNote: The CONTEST_LOGS_REPORTS environment variable must be set to the root directory")
    print("      containing your 'Logs', 'data', and 'reports' subdirectories.")
    print("\nOptions:")
    print("  --verbose               Enable verbose status reporting.")
    print("  --include-dupes         Include duplicate QSOs in calculations.")
    print("  --mult-name <name>      Specify multiplier for reports (e.g., 'Countries', 'Zones').")
    print("  --metric <qsos|points>  Specify metric for difference plots (defaults to 'qsos').")
    print("  --debug-data            Save source data for visual reports to a text file.")
    print("  --debug-mults           Save intermediate multiplier lists from text reports for debugging.")
    
    print("\nAvailable Reports:")
    max_id_len = max(len(rid) for rid in AVAILABLE_REPORTS.keys())
    for report_id, report_class in sorted(AVAILABLE_REPORTS.items()):
        print(f"  {report_id:<{max_id_len}} : {report_class.report_name}")
    print("")

def main():
    """Main function to parse arguments and run the analyzer."""
    
    class CustomArgumentParser(argparse.ArgumentParser):
        def error(self, message):
            handle_error("ARGUMENT ERROR", message, "Please check your command-line arguments against the usage guide below.")

    parser = CustomArgumentParser(description="Contest Log Analyzer", add_help=False)
    
    parser.add_argument('log_filepaths', nargs='*', help="Relative paths to Cabrillo log files under the 'Logs' directory.")
    parser.add_argument('--report', '-r', dest='report_id', help="The ID of the report to generate, or 'all'.")
    parser.add_argument('--verbose', action='store_true', help="Enable verbose status reporting.")
    parser.add_argument('--include-dupes', action='store_true', help="Include duplicate QSOs in calculations.")
    parser.add_argument('--mult-name', dest='mult_name', help="Specify the multiplier name for relevant reports.")
    parser.add_argument('--metric', dest='metric', choices=['qsos', 'points'], default='qsos', help="Metric for difference plots.")
    parser.add_argument('--debug-data', action='store_true', help='If set, save the data source for visual reports to a text file.')
    parser.add_argument('--debug-mults', action='store_true', help='Generate a debug file listing multipliers counted by summary reports.')
    
    args, unknown = parser.parse_known_args()

    setup_logging(args.verbose)

    raw_root_dir = os.environ.get('CONTEST_LOGS_REPORTS')
    if not raw_root_dir:
        handle_error(
            "CONFIGURATION ERROR",
            "The CONTEST_LOGS_REPORTS environment variable is not set.",
            "Please set this variable to point to the root directory that contains your 'Logs' and 'data' subdirectories."
        )
    
    root_dir = raw_root_dir.strip().strip('"').strip("'")
    
    data_dir = os.path.join(root_dir, 'data')
    if not os.path.isdir(data_dir):
        handle_error(
            "CONFIGURATION ERROR",
            "The required 'data' subdirectory was not found.",
            "Please ensure a 'data' directory exists inside your root directory.",
            path=data_dir
        )
    os.environ['CONTEST_DATA_DIR'] = data_dir
    
    reports_dir = os.path.join(root_dir, 'reports')
    logs_dir = os.path.join(root_dir, 'Logs')

    if unknown:
        handle_error("ARGUMENT ERROR", f"Unrecognized arguments: {' '.join(unknown)}", "Please check your spelling and refer to the usage guide.")

    if not args.log_filepaths:
        handle_error("ARGUMENT ERROR", "At least one log file path must be provided.", "Please provide the path to one or more Cabrillo log files relative to your 'Logs' directory.")

    full_log_paths = [os.path.join(logs_dir, path) for path in args.log_filepaths]
    for log_path in full_log_paths:
        if not os.path.isfile(log_path):
            handle_error("FILE NOT FOUND", "A specified log file could not be found on disk.", "Please verify that the file exists and that the path is correct.", path=log_path)

    if not args.report_id:
        handle_error("ARGUMENT ERROR", "The --report argument is required.", "Please specify which report to generate (e.g., --report summary).")

    report_id_lower = args.report_id.lower()
    if report_id_lower not in ['all', 'chart', 'text', 'plot'] and args.report_id not in AVAILABLE_REPORTS:
        handle_error("ARGUMENT ERROR", f"The report ID '{args.report_id}' was not found.", "Please choose a valid Report ID from the 'Available Reports' list below.")
        
    logging.info("\n--- Contest Log Analyzer ---")
    log_manager = LogManager()
    
    for path in full_log_paths:
        log_manager.load_log(path)
    
    report_kwargs = {
        'include_dupes': args.include_dupes,
        'mult_name': args.mult_name,
        'metric': args.metric,
        'debug_data': args.debug_data,
        'debug_mults': args.debug_mults
    }

    try:
        log_manager.finalize_loading()
        generator = ReportGenerator(logs=log_manager.get_logs(), root_output_dir=reports_dir)
        generator.run_reports(args.report_id, **report_kwargs)
    except ValueError as e:
        handle_error(
            "INITIALIZATION ERROR",
            str(e),
            "Ensure all logs are valid, from the same contest and event, and can be parsed correctly."
        )
    
    logging.info("\n--- Done ---")

if __name__ == '__main__':
    main()