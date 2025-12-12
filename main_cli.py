# main_cli.py
#
# Purpose: This is the main command-line interface (CLI) entry point for the
#          Contest Log Analytics. It now handles multiple log files and can
#          generate specific reports.
#
# Author: Gemini AI
# Date: 2025-12-04
# Version: 0.91.2-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# --- Revision History ---
# [0.91.2-Beta] - 2025-12-04
# - Added specific exception handling for Jinja2 PackageLoader errors
#   to guide users when the 'templates' directory is missing.
# [0.91.1-Beta] - 2025-12-04
# - Improved error handling for FileNotFoundError to distinguish between
#   missing input files and invalid output directory paths.
# [0.91.0-Beta] - 2025-10-09
# - Added `--wrtc <year>` CLI flag to enable WRTC scoring for IARU-HF logs.
# [0.90.5-Beta] - 2025-10-05
# - Modified `main` to pass the `debug_data` flag to `log_manager.finalize_loading`.
# --- Revision History ---
# [0.90.0-Beta] - 2025-10-01
# Set new baseline version for release.

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
    print("\nNote: Two environment variables must be set:")
    print("       - CONTEST_INPUT_DIR:  Root directory containing your 'Logs' and 'data' subdirectories.")
    print("      - CONTEST_REPORTS_DIR: Root directory where the 'reports' output folder will be created.")
    print("\nOptions:")
    print("  --verbose              Enable verbose status reporting.")
    print("  --include-dupes         Include duplicate QSOs in calculations.")
    print("  --mult-name <name>      Specify multiplier for reports (e.g., 'Countries', 'Zones').")
    print("  --metric <qsos|points>  Specify metric for difference plots (defaults to 'qsos').")
    print("  --cty <specifier>       Specify CTY file: 'before', 'after' (default), or filename (e.g., 'cty-3401.dat').")
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

    parser = CustomArgumentParser(description="Contest Log Analytics", add_help=False)
    
    parser.add_argument('log_filepaths', nargs='*', help="Relative paths to Cabrillo log files under the 'Logs' directory.")
    parser.add_argument('--report', '-r', dest='report_id', help="The ID of the report to generate, or 'all'.")
    parser.add_argument('--cty', default='after', help="Specify CTY file: 'before', 'after', or filename (e.g., 'cty-3401.dat').")
    parser.add_argument('--verbose', action='store_true', help="Enable verbose status reporting.")
    parser.add_argument('--include-dupes', action='store_true', help="Include duplicate QSOs in calculations.")
    parser.add_argument('--mult-name', dest='mult_name', help="Specify the multiplier name for relevant reports.")
    parser.add_argument('--metric', dest='metric', choices=['qsos', 'points'], default='qsos', help="Metric for difference plots.")
    parser.add_argument('--debug-data', action='store_true', help='If set, save the data source for visual reports to a text file.')
    parser.add_argument('--wrtc', dest='wrtc_year', type=int, help='Score IARU-HF logs using the rules for a specific WRTC year (e.g., 2026).')
    parser.add_argument('--debug-mults', action='store_true', help='Generate a debug file listing multipliers counted by summary reports.')
    
    args, unknown = parser.parse_known_args()

    setup_logging(args.verbose)

    # --- Read and Validate Environment Variables ---
    raw_input_dir = os.environ.get('CONTEST_INPUT_DIR')
    raw_reports_dir = os.environ.get('CONTEST_REPORTS_DIR')

    if not raw_input_dir or not raw_reports_dir:
        handle_error(
            "CONFIGURATION ERROR",
            "One or more required environment variables are not set.",
            "Please set both CONTEST_INPUT_DIR and CONTEST_REPORTS_DIR."
        )

    root_input_dir = raw_input_dir.strip().strip('"').strip("'")
    root_reports_dir = raw_reports_dir.strip().strip('"').strip("'")

    # --- OneDrive Check ---
    if 'onedrive' in root_reports_dir.lower():
        handle_error(
            "CONFIGURATION ERROR",
            "The reports directory cannot be located inside a OneDrive folder.",
            "Please set CONTEST_REPORTS_DIR to a local path (e.g., C:\\Users\\YourUser\\HamRadio\\CLA) to prevent file locking issues."
        )

    data_dir = os.path.join(root_input_dir, 'data')
    if not os.path.isdir(data_dir):
        handle_error(
            "CONFIGURATION ERROR",
            "The required 'data' subdirectory was not found in your input directory.",
            "Please ensure a 'data' directory exists inside your CONTEST_INPUT_DIR path.",
            path=data_dir
        )
    
    logs_dir = os.path.join(root_input_dir, 'Logs')
    
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
    if report_id_lower not in ['all', 'chart', 'text', 'plot', 'animation', 'html'] and args.report_id not in AVAILABLE_REPORTS:
        handle_error("ARGUMENT ERROR", f"The report ID '{args.report_id}' was not found.", "Please choose a valid Report ID from the 'Available Reports' list below.")
        
    try:
        logging.info("\n--- Contest Log Analytics ---")
        log_manager = LogManager()
        log_manager.load_log_batch(full_log_paths, root_input_dir, args.cty, args.wrtc_year)

        report_kwargs = {
            'include_dupes': args.include_dupes,
            'mult_name': args.mult_name,
            'metric': args.metric,
            'debug_data': args.debug_data,
            'debug_mults': args.debug_mults
        }

        log_manager.finalize_loading(root_reports_dir, debug_data=args.debug_data)
    
        generator = ReportGenerator(logs=log_manager.get_logs(), root_output_dir=root_reports_dir)
        generator.run_reports(args.report_id, **report_kwargs)
    except FileNotFoundError as e:
        if args.wrtc_year:
            handle_error(
                "CONFIGURATION ERROR",
                f"The ruleset for WRTC {args.wrtc_year} could not be found.",
                f"Ensure a 'wrtc_{args.wrtc_year}.json' definition file exists in the contest_definitions directory."
            )
        
        # Generic error handling to catch output directory issues as well as input file issues
        handle_error(
            "FILE NOT FOUND",
            f"A critical file or directory could not be found: {e}",
            "Ensure required input files (like cty.dat) exist, and that the output directory path is valid and writable."
        )
    except ValueError as e:
        if "PackageLoader" in str(e):
            handle_error(
                "CONFIGURATION ERROR",
                f"Missing template directory: {e}",
                "Ensure the 'contest_tools/templates' directory exists and contains the required .html files."
            )
        logging.exception(e)
        handle_error(
            "INITIALIZATION ERROR",
            str(e),
            "Ensure all logs are valid, from the same contest and event, and can be parsed correctly."
        )
    
    logging.info("\n--- Done ---")

if __name__ == '__main__':
    main()