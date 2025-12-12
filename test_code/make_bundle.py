# Contest Log Analytics/test_code/create_project_bundle.py
#
# Purpose: This utility traverses a directory to find all relevant project
#          files and consolidates them into a single text file. By default,
#          it bundles source code (.py, .json), but can be switched to
#          bundle documentation files (.md, .txt) via a command-line flag.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-02
# Version: 0.33.0-Beta
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

## [0.33.0-Beta] - 2025-08-12
### Changed
# - Refactored argument parsing to support mutually exclusive --code, --data,
#   and --doc bundle types.
# - The script now prints a help message and exits if no bundle type is specified.

## [0.32.0-Beta] - 2025-08-12
### Changed
# Modified the script bundle .md files when the optional --txt argument is 
# provided to avoid .txt files from reports.

## [0.26.2-Beta] - 2025-08-02
### Changed
# - Modified the script to start its file search from the current working
#   directory ('.') instead of the parent directory of the script.

## [0.26.1-Beta] - 2025-08-02
### Added
# - Added an optional '--txt' command-line argument to bundle .md and .txt
#   files instead of the default .py and .json files.

## [1.0.0] - 2025-07-25
# - Initial release of the project bundling script.

import os
import argparse
from typing import Tuple

def create_project_bundle(root_dir: str, output_file: str, file_extensions: Tuple[str, ...]):
    """
    Traverses a directory to find all files with specified extensions and
    consolidates them into a single text file with descriptive headers.

    Args:
        root_dir (str): The path to the root directory of the project.
        output_file (str): The name of the text file to be created.
        file_extensions (Tuple[str, ...]): A tuple of file extensions to include.
    """
    # Define a unique header format that's easy to parse
    header_template = "--- FILE: {file_path} ---\n"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as bundle_file:
            # Walk through the directory tree starting from the root
            for dirpath, _, filenames in os.walk(root_dir):
                # Sort filenames to ensure a consistent order
                for filename in sorted(filenames):
                    if filename.endswith(file_extensions):
                        file_path = os.path.join(dirpath, filename)
                        
                        # Create a relative path to keep the output clean
                        relative_path = os.path.relpath(file_path, root_dir)
                        
                        # Write the unique header to the bundle
                        bundle_file.write(header_template.format(file_path=relative_path.replace('\\', '/')))
                        
                        # Write the content of the file
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f_in:
                                content = f_in.read()
                                bundle_file.write(content)
                                # Add a newline to separate file content from the next header
                                bundle_file.write('\n')
                        except Exception as e:
                            bundle_file.write(f"*** ERROR READING FILE: {e} ***\n")
                            
        print(f"Successfully created project bundle: '{output_file}'")

    except IOError as e:
        print(f"Error: Could not write to output file '{output_file}'. Reason: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    # --- Command-Line Argument Parsing ---
    parser = argparse.ArgumentParser(
        description="Create a bundle of project files. Specify one bundle type."
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "--code",
        action="store_true",
        help="Bundle code files (.py, .json)."
    )
    group.add_argument(
        "--data",
        action="store_true",
        help="Bundle data files (.dat)."
    )
    group.add_argument(
        "--doc",
        action="store_true",
        help="Bundle documentation files (.md)."
    )

    args = parser.parse_args()

    # --- Determine which files to bundle ---
    ready_to_bundle = True
    if args.code:
        extensions_to_bundle = ('.py', '.json')
        output_filename = 'code_bundle.txt'
        print("Bundling code files (.py, .json)...")
    elif args.data:
        extensions_to_bundle = ('.dat',)
        output_filename = 'data_bundle.txt'
        print("Bundling data files (.dat)...")
    elif args.doc:
        extensions_to_bundle = ('.md',)
        output_filename = 'doc_bundle.txt'
        print("Bundling documentation files (.md)...")
    else:
        ready_to_bundle = False
        print("No bundle type specified. Please use one of: --code, --data, or --doc.")

    # --- Create the bundle if an option was selected ---
    if ready_to_bundle:
        # Set the root directory to the current working directory.
        project_directory = '.'
        create_project_bundle(project_directory, output_filename, extensions_to_bundle)