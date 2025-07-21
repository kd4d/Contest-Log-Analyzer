# Contest Log Analyzer/main_cli.py
#
# Purpose: This is the main command-line interface (CLI) entry point for the
#          Contest Log Analyzer. It now handles multiple log files and can
#          generate specific reports.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-21
# Version: 0.11.0-Beta
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

## [0.11.0-Beta] - 2025-07-21
### Changed
# - Modified to handle reports that save their own files. The main script
#   now prints the summary message returned by the report's generate() method.
# - Report output is now saved to a structured directory:
#   reports_output/YYYY/ContestName/
# - The year is determined from the first QSO of the first log processed.

## [0.10.0-Beta] - 2025-07-21
# - Integrated new LogManager and reports packages.
# - Added '--report <id|all>' command-line argument to generate reports.

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
    include_dupes = '--include-dupes' in sys.argv
    if include_dupes:
        sys.argv.remove('--include-dupes')

    if len(sys.argv) < 3 or sys.argv[1] != '--report':
        print("\nUsage: python main_cli.py --report <ReportID|all> <LogFilePath1> [<LogFilePath2>...] [--include-dupes]")
        print("\nExample: python main_cli.py --report summary k3lr.log --include-dupes")
        
        if AVAILABLE_REPORTS:
            print("\nAvailable reports:")
            for report_id, report_class in AVAILABLE_REPORTS.items():
                print(f"  - {report_id}: {report_class.report_name.fget(None)}")
        else:
            print("\nNo reports found.")
            
        sys.exit(1)

    report_id = sys.argv[2]
    log_filepaths = sys.argv[3:]

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
            reports_to_run = AVAILABLE_REPORTS.values()
        else:
            reports_to_run = [AVAILABLE_REPORTS[report_id]]
        
        # --- Define Output Directory Structure ---
        first_log = logs[0]
        contest_name = first_log.get_metadata().get('ContestName', 'UnknownContest').replace(' ', '_')
        
        first_qso_date = first_log.get_processed_data()['Date'].iloc[0]
        year = first_qso_date.split('-')[0] if first_qso_date else "UnknownYear"

        output_dir = os.path.join("reports_output", year, contest_name)
        
        # Generate the selected reports
        for ReportClass in reports_to_run:
            report_instance = ReportClass(logs)
            print(f"\nGenerating report: '{report_instance.report_name}'...")
            result = report_instance.generate(output_path=output_dir, include_dupes=include_dupes)

            # --- Output ---
            if report_instance.report_type == 'text':
                # The report now saves its own file(s) and returns a summary message.
                print(result)
            elif report_instance.report_type == 'plot':
                print(f"\nPlot(s) generated. See '{output_dir}/' directory.")

        print("\n--- Done ---")

    except Exception as e:
        print(f"\nAn unexpected critical error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
