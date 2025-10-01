# Contest Log Analyzer/test_code/header_updater.py
#
# Purpose: A utility script to standardize the headers of all Python files
#          in a target directory. It requires either a --check (dry run)
#          or --update (execute) argument.
#
# Author: Gemini AI
# Date: 2025-09-30
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
import re
import difflib
from typing import List, Optional, Tuple

# --- Configuration ---
NEW_VERSION = "0.90.0-Beta"
NEW_DATE = "2025-09-30"
NEW_AUTHOR = "Gemini AI"

def extract_file_components(filepath: str) -> Optional[Tuple[str, List[str], str, str, str, List[str], List[str]]]:
    """
    Reads a Python file and splits it into its constituent header parts and the code body.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"ERROR: Could not read file {filepath}: {e}")
        return None

    # --- Isolate Code Body ---
    body_start_index = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Header ends at first import, from, or non-comment assignment statement
        if stripped.startswith('import ') or stripped.startswith('from ') or ('=' in stripped and not stripped.startswith('#')):
            body_start_index = i
            break
            
    if body_start_index == -1:
        body_start_index = len(lines)

    body_lines = lines[body_start_index:]
    header_lines = lines[:body_start_index]
    
    # --- Extract Header Components ---
    original_path_comment = ""
    purpose_lines: List[str] = []
    copyright_str = ""
    license_lines: List[str] = []
    contact_str = ""

    in_purpose = False
    in_license = False
    metadata_pattern = re.compile(r'^\s*#\s*([A-Za-z]+):\s*')

    # **BUG FIX**: Explicitly find the copyright line first, as it has a unique format.
    for line in header_lines:
        if '# Copyright' in line:
            copyright_str = line
            break

    for line in header_lines:
        stripped = line.strip()

        if not original_path_comment and stripped.startswith('#') and ('/' in stripped or '\\' in stripped):
            original_path_comment = line
            continue

        match = metadata_pattern.match(stripped)
        tag = match.group(1).lower() if match else None

        if tag == 'purpose':
            in_purpose = True
            in_license = False
        elif tag:
            in_purpose = False
            in_license = False
            # Copyright is now handled above, so it's excluded here.
            if tag == 'contact':
                contact_str = line
            elif tag == 'license':
                in_license = True

        if in_purpose:
            purpose_lines.append(line)
        elif in_license:
            license_lines.append(line)
            
    return original_path_comment, purpose_lines, copyright_str, "".join(license_lines), contact_str, body_lines, lines

def generate_new_content(filepath: str, project_root: str) -> Optional[str]:
    """Generates the proposed new content for a file but does not write it."""
    components = extract_file_components(filepath)
    if components is None:
        return None
        
    original_path_comment, purpose_lines, copyright_str, license_str, contact_str, body_lines, _ = components

    if not original_path_comment:
        relative_path = os.path.relpath(filepath, project_root).replace('\\', '/')
        original_path_comment = f"# Contest Log Analyzer/{relative_path}\n"

    new_header_lines = [
        original_path_comment,
        "#\n"
    ]
    new_header_lines.extend(purpose_lines)
    new_header_lines.append("\n" if purpose_lines else "")
    new_header_lines.extend([
        f"# Author: {NEW_AUTHOR}\n",
        contact_str,
        f"# Date: {NEW_DATE}\n",
        f"# Version: {NEW_VERSION}\n",
        "#\n",
        copyright_str,
        "#\n",
        license_str,
        "\n" if license_str else "",
        "# --- Revision History ---\n",
        f"## [{NEW_VERSION}] - {NEW_DATE}\n",
        "# - Wiped revision history and set new baseline version for release.\n"
    ])

    new_header_lines = [line for line in new_header_lines if line]
    return "".join(new_header_lines) + "".join(body_lines)

def check_file_header(filepath: str, project_root: str):
    """Generates and prints a diff without modifying the file."""
    print(f"\n--- Checking: {os.path.basename(filepath)} ---")
    new_content = generate_new_content(filepath, project_root)
    if not new_content:
        return

    components = extract_file_components(filepath)
    if not components: return
    original_lines = components[6]

    diff = list(difflib.unified_diff(
        original_lines,
        new_content.splitlines(keepends=True),
        fromfile=f"a/{os.path.basename(filepath)}",
        tofile=f"b/{os.path.basename(filepath)}",
        n=3
    ))

    if not diff:
        print("No changes needed.")
    else:
        print("".join(diff))

def update_file_header(filepath: str, project_root: str) -> bool:
    """Reads a file, replaces its header, and writes it back."""
    new_content = generate_new_content(filepath, project_root)
    if not new_content:
        return False

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except Exception as e:
        print(f"ERROR: Could not write to file {filepath}: {e}")
        return False

def main():
    """Main function to run the header updater script."""
    parser = argparse.ArgumentParser(
        description="Standardize Python file headers in a specified directory."
    )
    parser.add_argument(
        'target_directory',
        nargs='?',
        default='.',
        help="The directory to scan for .py files. Defaults to the current directory."
    )
    
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        '--check',
        action='store_true',
        help="Perform a dry run. Show diffs but do not modify files."
    )
    mode_group.add_argument(
        '--update',
        action='store_true',
        help="Apply changes and modify files."
    )
    args = parser.parse_args()

    target_path = os.path.abspath(args.target_directory)
    project_root = os.path.abspath('.')

    if not os.path.isdir(target_path):
        print(f"ERROR: Target directory not found: {target_path}")
        return

    files_to_process = []
    script_name = os.path.basename(__file__)
    for item in os.listdir(target_path):
        if item.endswith('.py') and item != script_name:
            filepath = os.path.join(target_path, item)
            if os.path.isfile(filepath):
                files_to_process.append(filepath)

    if not files_to_process:
        print(f"\nNo Python files found to process in: {target_path}")
        return

    if args.check:
        print(f"\nPerforming DRY RUN in: {target_path}")
        for fp in files_to_process:
            check_file_header(fp, project_root)
        print("\n--- DRY RUN COMPLETE ---")
        print("No files were modified. Run with --update to apply changes.")

    elif args.update:
        print(f"\nUpdating headers in: {target_path}")
        updated_files = []
        for fp in files_to_process:
            if update_file_header(fp, project_root):
                updated_files.append(os.path.basename(fp))

        if updated_files:
            print("\n--- UPDATE COMPLETE ---")
            print(f"Successfully updated {len(updated_files)} files:")
            for filename in sorted(updated_files):
                print(f" - {filename}")
        else:
            print("\n--- UPDATE COMPLETE ---")
            print("No files were modified.")

if __name__ == '__main__':
    main()