# Contest Log Analyzer/run_regression_test.py
#
# Purpose: This script provides an automated regression test for the Contest Log
#          Analyzer. It archives the last known-good reports, runs a series of
#          pre-defined test cases from a batch file, and compares the new
#          output against the archived baseline to detect any regressions.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-09-09
# Version: 0.70.9-Beta
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
## [0.70.9-Beta] - 2025-09-09
### Changed
# - Refactored script to read environment variables in one location and
#   pass them as parameters, in compliance with Principle 15.
## [0.62.0-Beta] - 2025-09-08
### Changed
# - Updated script to use the new CONTEST_REPORTS_DIR environment variable.
## [0.39.0-Beta] - 2025-09-07
### Changed
# - Replaced the archiving logic with a robust "copy then delete"
#   strategy that includes an error handler to automatically remove
#   read-only attributes, solving failures caused by OneDrive/Git.
## [0.38.1-Beta] - 2025-09-07
### Fixed
# - Replaced shutil.move with os.rename and added a pre-emptive check
#   to prevent a race condition during the archiving step.
## [0.38.0-Beta] - 2025-09-06
### Added
# - Added content-aware comparison logic for _processed.csv files, which
#   sorts the data before comparing to prevent false positives.
# - Added content-aware comparison logic for .adi files, which parses
#   the file and compares the data structure to prevent false positives.
## [0.37.1-Beta] - 2025-09-04
### Fixed
# - Added a resilient retry loop to the archive function to handle
#   transient file locks from cloud sync services like OneDrive.
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
import time
import errno
import pandas as pd
import re
import json
import stat
from typing import List, Dict

def _handle_rmtree_readonly(func, path, exc_info):
    """
    Error handler for shutil.rmtree that handles read-only files and directories.
    """
    exc_type, exc_value, exc_tb = exc_info
    if isinstance(exc_value, PermissionError):
        # Remove the read-only attribute and retry the operation
        os.chmod(path, stat.S_IWRITE)
        func(path)
    else:
        raise

def _parse_adif_for_comparison(filepath: str) -> List[Dict[str, str]]:
    """Parses an ADIF file into a sorted list of dictionaries for comparison."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception:
        return []

    header_end_match = re.search(r'<EOH>', content, re.IGNORECASE)
    records_content = content[header_end_match.end():] if header_end_match else content
    qso_records = re.split(r'<EOR>', records_content, flags=re.IGNORECASE)
    
    all_qsos_data = []
    adif_tag_pattern = re.compile(r'<([A-Z0-9_]+):\d+>([^<]*)', re.IGNORECASE)

    for record_str in qso_records:
        if record_str.strip():
            # Sort tags alphabetically within each record for a canonical representation
            qso_data = dict(sorted(adif_tag_pattern.findall(record_str.upper())))
            if qso_data:
                all_qsos_data.append(qso_data)
    
    # Sort all QSOs by TIME_ON and CALL to ensure a canonical order for the entire file
    return sorted(all_qsos_data, key=lambda x: (x.get('TIME_ON', ''), x.get('CALL', '')))

def get_report_dirs(root_reports_dir: str):
    """Gets and validates the root reports directory."""
    root_env = root_reports_dir
    if not root_env:
        print("FATAL: CONTEST_REPORTS_DIR environment variable is not set. Exiting.")
        sys.exit(1)
    
    root_dir = root_env.strip().strip('"').strip("'")
    reports_dir = os.path.join(root_dir, 'reports')
    
    return root_dir, reports_dir

def archive_baseline_reports(reports_dir: str) -> str:
    """Archives the existing reports directory using a resilient copy-then-delete strategy."""
    if not os.path.exists(reports_dir):
        print(f"INFO: No existing reports directory found at '{reports_dir}'. Baseline will be empty.")
        return ""
        
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
    archive_dir_final = f"{reports_dir}_{timestamp}"
    archive_dir_tmp = f"{archive_dir_final}.tmp"

    # --- Pre-emptive check for inconsistent state ---
    if os.path.exists(archive_dir_final) or os.path.exists(archive_dir_tmp):
        print(f"FATAL: A final or temporary archive directory already exists.")
        print("       This indicates a previous run failed. Please manually clean up the directory.")
        sys.exit(1)

    # --- Phase 1: Robust Copy to Temporary Directory ---
    print(f"Step 1: Copying source to temporary directory '{os.path.basename(archive_dir_tmp)}'...")
    copy_success = False
    for i in range(10): # Retry for up to 10 seconds
        try:
            shutil.copytree(reports_dir, archive_dir_tmp)
            copy_success = True
            print(" -> Copy successful.")
            break
        except FileExistsError:
            print(f"  - Cleaning up partial temporary directory...")
            shutil.rmtree(archive_dir_tmp, onerror=_handle_rmtree_readonly)
            time.sleep(1)
        except OSError as e:
            if e.errno == errno.EACCES: # Permission denied
                print(f"  - Copy failed (Access Denied). Retrying in 1 second...")
                time.sleep(1)
            else:
                print(f"FATAL: An unhandled OS error occurred during copy: {e}")
                sys.exit(1)
        except Exception as e:
            print(f"FATAL: An unexpected error occurred during copy: {e}")
            sys.exit(1)
            
    if not copy_success:
        print("FATAL: Could not copy source directory after multiple retries. Aborting.")
        sys.exit(1)
        
    # --- Phase 2: Atomic Rename ---
    print(f"Step 2: Renaming temporary directory to final destination...")
    try:
        os.rename(archive_dir_tmp, archive_dir_final)
        print(f" -> Rename successful. Archive is now at: {os.path.basename(archive_dir_final)}")
    except Exception as e:
        print(f"FATAL: Could not rename temporary directory: {e}")
        print(f"       The original data is safe, and a complete copy exists at '{archive_dir_tmp}'")
        sys.exit(1)
        
    # --- Phase 3: Resilient Delete of Original ---
    print(f"Step 3: Deleting original source directory '{os.path.basename(reports_dir)}'...")
    try:
        shutil.rmtree(reports_dir, onerror=_handle_rmtree_readonly)
        print(" -> Deletion successful.")
    except Exception as e:
        print(f"WARNING: An unexpected error occurred during delete: {e}")
        print(f"WARNING: Failed to delete '{reports_dir}'. Please remove it manually.")
    
    return archive_dir_final


def compare_outputs(new_items: set, reports_dir: str, archive_dir: str, ignore_whitespace: bool) -> list:
    """Compares new files against the baseline and returns a list of failures."""
    failures = []
    
    for item_path in sorted(list(new_items)):
        relative_path = os.path.relpath(item_path, reports_dir)
        baseline_path = os.path.join(archive_dir, relative_path)

        if not os.path.exists(baseline_path):
            if item_path.endswith(('.png', '.mp4', '.txt', '.adi', '_processed.csv')):
                failures.append(f"Missing Baseline: {relative_path}")
            continue

        if item_path.endswith('_processed.csv'):
            try:
                df_new = pd.read_csv(item_path, dtype=str).fillna('')
                df_base = pd.read_csv(baseline_path, dtype=str).fillna('')
                
                sort_keys = ['Datetime', 'Call']
                if not all(k in df_new.columns for k in sort_keys):
                    sort_keys = [k for k in sort_keys if k in df_new.columns]
                
                df_new = df_new.sort_values(by=sort_keys).reset_index(drop=True)
                df_base = df_base.sort_values(by=sort_keys).reset_index(drop=True)

                if not df_new.equals(df_base):
                    diff = list(difflib.unified_diff(
                        df_base.to_string().splitlines(keepends=True),
                        df_new.to_string().splitlines(keepends=True),
                        fromfile=f'a/{relative_path}', tofile=f'b/{relative_path}'
                    ))
                    failures.append(f"File: {relative_path}\n" + "".join(diff))
            except Exception as e:
                failures.append(f"File: {relative_path}\nERROR during CSV diff: {e}")

        elif item_path.endswith('.adi'):
            try:
                qsos_new = _parse_adif_for_comparison(item_path)
                qsos_base = _parse_adif_for_comparison(baseline_path)

                if qsos_new != qsos_base:
                    str_new = json.dumps(qsos_new, indent=2)
                    str_base = json.dumps(qsos_base, indent=2)
                    diff = list(difflib.unified_diff(
                        str_base.splitlines(keepends=True), str_new.splitlines(keepends=True),
                        fromfile=f'a/{relative_path}', tofile=f'b/{relative_path}'
                    ))
                    failures.append(f"File: {relative_path}\n" + "".join(diff))
            except Exception as e:
                failures.append(f"File: {relative_path}\nERROR during ADIF diff: {e}")

        elif item_path.endswith('.txt'):
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

    root_reports_dir_env = os.environ.get('CONTEST_REPORTS_DIR')
    if not root_reports_dir_env:
        print("FATAL: CONTEST_REPORTS_DIR environment variable is not set. Exiting.")
        sys.exit(1)

    root_dir, reports_dir = get_report_dirs(root_reports_dir_env)
    
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