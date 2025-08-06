# Contest Log Analyzer/main_cli.py
#
# Purpose: This is the main command-line interface (CLI) entry point for the
#          Contest Log Analyzer. It now handles multiple log files and can
#          generate specific reports.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-05
# Version: 0.30.29-Beta
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
## [0.30.29-Beta] - 2025-08-05
### Changed
# - Updated the usage guide to include new report category options (chart, text, plot).
## [0.30.24-Beta] - 2025-08-05
# - No functional changes. Synchronizing version numbers.
## [0.30.0-Beta] - 2025-08-05
# - Initial release of Version 0.30.0-Beta.
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

    parser = CustomArgumentParser(description="Contest Log