# Contest Log Analyzer/test_code/header_scanner.py
#
# Purpose: A diagnostic script to scan Python files for header anomalies.
#          It identifies any .py files that contain non-comment, non-blank
#          lines before the first 'import' or 'from' statement.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-09-29
# Version: 1.0.0-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import argparse
from typing import List

def scan_file_for_header_anomaly(filepath: str) -> bool:
    """
    Checks a single Python file for executable code before the first import.

    Args:
        filepath (str): The path to the Python file.

    Returns:
        bool: True if an anomaly is found, False otherwise.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                stripped_line = line.strip()
                if not stripped_line:
                    continue  # Skip blank lines
                if stripped_line.startswith('#'):
                    continue  # Skip comment lines

                # If we find an import, the header is clean up to this point.
                if stripped_line.startswith('import ') or stripped_line.startswith('from '):
                    return False

                # If we find any other non-blank, non-comment line, it's an anomaly.
                return True
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return True # Treat read errors as anomalies
    
    return False # No anomalies found before end of file

def main():
    """Main function to parse arguments and run the scanner."""
    parser = argparse.ArgumentParser(
        description="Scan Python files for header anomalies (code before first import)."
    )
    parser.add_argument(
        'scan_directory',
        nargs='?',
        default='.',
        help="The root directory to start scanning from. Defaults to the current directory."
    )
    args = parser.parse_args()

    anomalous_files: List[str] = []
    scan_path = os.path.abspath(args.scan_directory)
    print(f"\nScanning for header anomalies in: {scan_path}\n")

    for root, dirs, files in os.walk(scan_path, topdown=True):
        # Exclude the 'test_code' directory from the scan
        if 'test_code' in dirs:
            dirs.remove('test_code')
            
        for name in files:
            if name.endswith('.py'):
                filepath = os.path.join(root, name)
                if scan_file_for_header_anomaly(filepath):
                    anomalous_files.append(filepath)

    if anomalous_files:
        print("--- ANOMALY REPORT ---")
        print("The following files contain non-comment, non-blank lines before the first import statement:")
        for filepath in sorted(anomalous_files):
            print(f" - {filepath}")
        print("\nScan complete. Please correct these files before proceeding.")
    else:
        print("--- SCAN COMPLETE ---")
        print("No header anomalies found.")

if __name__ == '__main__':
    main()