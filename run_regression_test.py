# Contest Log Analyzer/run_regression_test.py
#
# Purpose: This script provides an automated regression test for the Contest Log
#          Analyzer. It archives the last known-good reports, runs a series of
#          pre-defined test cases from a batch file, and compares the new
#          output against the archived baseline to detect any regressions.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-16
# Version: 0.37.0-Beta
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
## [0.37.0-Beta] - 2025-08-16
### Added
# - Initial release of the automated regression test script.

import os
import sys
import argparse
import datetime
import subprocess
import shutil
import difflib

def get_report_dirs():
    """Gets and validates the root, reports, and data directories."""
    root_env = os.environ.get('CONTEST_LOGS_REPORTS')
    if not root_env:
        print("FATAL: CONTEST_LOGS_REPORTS environment variable is not set. Exiting.")
        sys.exit(1)
    
    root_dir = root_env.strip().strip('"').strip("'")
    reports_dir = os.path.join(root_dir, 'reports')
    
    return root_dir, reports_dir

def archive_baseline_reports(reports_dir: str) -> str:
    """Renames the existing reports directory to create a timestamped archive."""
    if not os.path.exists(reports_dir):
        print(f"INFO: No existing reports directory found at '{reports_dir}'. Baseline will be empty.")
        return ""
        
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
    archive_dir = f"{reports_dir}_{timestamp}"
    
    try:
        shutil.move(reports_dir, archive_dir)
        print(f"SUCCESS: Archived existing reports to '{archive_dir}'")
        return archive_dir
    except Exception as e:
        print(f"FATAL: Could not archive reports directory: {e}")
        sys.exit(1)

def compare_outputs(new_items: set, reports_dir: str, archive_dir: str, ignore_whitespace: bool) -> list:
    """Compares new files against the baseline and returns a list of failures."""
    failures = []
    
    for item_path in sorted(list(new_items)):
        relative_path = os.path.relpath(item_path, reports_dir)
        baseline_path = os.path.join(archive_dir, relative_path)

        if not os.path.exists(baseline_path):
            if item_path.endswith(('.png', '.mp4', '.txt')):
                failures.append(f"Missing Baseline: {relative_path}")
            continue

        if item_path.endswith('.txt'):
            try:
                with open(item_path, 'r', encoding='utf-8') as f_new:
                    lines_new = f_new.readlines()
                with open(baseline_path, 'r', encoding='utf-8') as f_base:
                    lines_base = f_base.readlines()

                if ignore_whitespace:
                    lines_new = [" ".join(line.split()) + '\n' for line in lines_new]
                    lines_base = [" ".join(line.split()) + '\n' for line in lines_base]

                diff = list(difflib.unified_diff(
                    lines_base, lines_new,
                    fromfile=f'a/{relative_path}', tofile=f'b/{relative_path}'
                ))

                if diff:
                    failures.append(f"File: {relative_path}\n" + "".join(diff))
            except Exception as e:
                failures.append(f"File: {relative_path}\nERROR during diff: {e}")
                
    return failures

def main():
    parser = argparse.ArgumentParser(description="Run regression tests for the Contest Log Analyzer.")
    parser.add_argument(
        "--nowhitespace",
        action="store_true",
        help="Ignore all whitespace differences in text file comparisons."
    )
    args = parser.parse_args()

    root_dir, reports_dir = get_report_dirs()
    
    # 1. Archive existing reports
    print("\n--- Step 1: Archiving Baseline Reports ---")
    archive_dir = archive_baseline_reports(reports_dir)
    if not archive_dir:
        # Create an empty dir so baseline checks don't fail with FileNotFoundError
        archive_dir = os.path.join(root_dir, "reports_baseline_empty")
        os.makedirs(archive_dir, exist_ok=True)


    # 2. Run tests and capture output
    print("\n--- Step 2: Running Test Cases ---")
    test_batch_file = 'regressiontest.bat'
    if not os.path.exists(test_batch_file):
        print(f"FATAL: '{test_batch_file}' not found in the current directory. Exiting.")
        sys.exit(1)

    # Ensure the new reports directory exists for the log file
    os.makedirs(reports_dir, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
    run_log_filename = f"TestRun_{timestamp}.txt"
    run_log_filepath = os.path.join(reports_dir, run_log_filename)

    with open(run_log_filepath, 'w', encoding='utf-8') as run_log:
        with open(test_batch_file, 'r', encoding='utf-8') as batch_file:
            commands = [line for line in batch_file if line.strip() and not line.strip().startswith('#')]

        for i, command in enumerate(commands):
            command = command.strip()
            print(f"Running [{i+1}/{len(commands)}]: {command}")
            run_log.write(f"\n--- Running Command {i+1}: {command} ---\n")
            run_log.flush()

            # The core "run-scan-compare" logic
            files_before = set(os.path.join(r, f) for r, _, fs in os.walk(reports_dir) for f in fs)
            
            try:
                subprocess.run(command, shell=True, check=True, text=True, stdout=run_log, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                print(f"  ERROR: Command failed with exit code {e.returncode}. See '{run_log_filename}' for details.")
            
            files_after = set(os.path.join(r, f) for r, _, fs in os.walk(reports_dir) for f in fs)
            new_files = files_after - files_before
            
            failures = compare_outputs(new_files, reports_dir, archive_dir, args.nowhitespace)

            # 3. Report results for this command
            if not failures:
                print(f"  -> Passed\n")
            else:
                print(f"  -> FAILED\n")
                print(f"--- FAILED: {command} ---")
                for failure in failures:
                    print(failure)
                    print("---")

    print(f"\n--- Regression Test Complete ---")
    print(f"Full test execution log saved to: {run_log_filepath}")

if __name__ == '__main__':
    main()