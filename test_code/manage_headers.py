# manage_headers.py
import argparse
import re
import difflib
from pathlib import Path
from datetime import date

# --- 1. CONFIGURATION ---
TARGET_DIRECTORY = Path("./")
NEW_VERSION = "0.90.0-Beta"
NEW_AUTHOR = "Gemini AI"
METADATA_KEYS = {"Author", "Date", "Version", "Copyright", "License", "Contact"}

def get_header_and_code(lines):
    """Splits a file's lines into header and code blocks."""
    first_code_line_index = -1
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if stripped_line and not stripped_line.startswith('#'):
            first_code_line_index = i
            break

    if first_code_line_index == -1:
        return lines, []

    header_lines = lines[:first_code_line_index]
    code_block = "".join(lines[first_code_line_index:])
    return header_lines, code_block

def extract_purpose_block(header_lines):
    """
    Finds the purpose block anywhere in the header and extracts it.
    The block starts with '# Purpose:' and ends at a blank comment
    line that is followed by a metadata line.
    """
    start_index = -1
    # Find the start of the block by looking for the # Purpose: tag
    for i, line in enumerate(header_lines):
        if line.strip().lower().startswith("# purpose:"):
            start_index = i
            break

    # If no purpose tag is found, return the default
    if start_index == -1:
        return ["# Purpose: [Description of the script's purpose]"]

    # Find the end of the block
    end_index = -1
    for i in range(start_index + 1, len(header_lines)):
        stripped_line = header_lines[i].strip()
        # The block ends with a blank comment line...
        if stripped_line == "#":
            # ...that is followed by a known metadata tag.
            if (i + 1) < len(header_lines):
                next_line = header_lines[i+1].strip()
                if next_line.startswith("#") and ":" in next_line:
                    key = next_line.split(':', 1)[0][1:].strip()
                    if key in METADATA_KEYS:
                        end_index = i
                        break
    
    # If a valid end was found, slice the header to get the block
    if end_index != -1:
        return [line.rstrip() for line in header_lines[start_index:end_index]]
    
    # If no specific end was found, assume it runs to the revision history
    purpose_block = []
    for line in header_lines[start_index:]:
        if "--- Revision History ---" in line:
            break
        purpose_block.append(line.rstrip())
    return purpose_block


def generate_expected_header(file_path, current_date, original_header_lines):
    """Programmatically generates the full text of the compliant header."""
    # Part 1: Filename
    expected_path = file_path.relative_to(TARGET_DIRECTORY.parent)
    clean_path = str(expected_path).replace('\\', '/')
    first_line = f"# {clean_path}"
    
    # Part 2: Purpose Block (extracted from anywhere in the original header)
    purpose_block_lines = extract_purpose_block(original_header_lines)

    # Part 3: Static metadata with the full Copyright and License block
    metadata_lines = [
        f"# Author: {NEW_AUTHOR}",
        f"# Date: {current_date}",
        f"# Version: {NEW_VERSION}",
        "#",
        "# Copyright (c) 2025 Mark Bailey, KD4D",
        "# Contact: kd4d@kd4d.org",
        "#",
        "# License: Mozilla Public License, v. 2.0",
        "#          (https://www.mozilla.org/MPL/2.0/)",
        "#",
        "# This Source Code Form is subject to the terms of the Mozilla Public",
        "# License, v. 2.0. If a copy of the MPL was not distributed with this",
        "# file, You can obtain one at http://mozilla.org/MPL/2.0/.",
    ]

    # Part 4: Revision History
    revision_history_lines = [
        "# --- Revision History ---",
        f"# [{NEW_VERSION}] - {current_date}",
        "# Set new baseline version for release."
    ]

    # Assemble all parts in the correct, standardized order
    header_parts = (
        [first_line, "#"] +
        purpose_block_lines +
        ["#"] +
        metadata_lines +
        revision_history_lines
    )
    
    return "\n".join(header_parts)

def check_file_header(file_path, current_date):
    """Checks for compliance and returns headers for diffing if needed."""
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return [f"Could not read file: {e}"], None

    header_lines, code_block = get_header_and_code(lines)
    if not code_block:
        return [], None
    
    expected_header_str = generate_expected_header(file_path, current_date, header_lines)
    actual_header_str = "\n".join([line.rstrip() for line in header_lines])
    
    if actual_header_str != expected_header_str:
        issues.append("Header does not match the standard template.")
        return issues, (actual_header_str, expected_header_str)

    return [], None

def update_file_header(file_path, current_date):
    """Replaces the header, preserving and reordering the multi-line 'Purpose' block."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        header_lines, code_block = get_header_and_code(lines)
        if not code_block:
            print(f"Skipping '{file_path}': No executable code found.")
            return

        new_header = generate_expected_header(file_path, current_date, header_lines)
        new_content = new_header + "\n\n" + code_block.strip() + "\n"
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(new_content)
        print(f"Updated: {file_path}")

    except Exception as e:
        print(f"Error processing '{file_path}': {e}")

def main():
    parser = argparse.ArgumentParser(description="A tool to standardize Python file headers.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="Check headers and show a diff.")
    group.add_argument("--update", action="store_true", help="Replace headers with the new standard.")
    args = parser.parse_args()

    # Find all python files
    all_python_files = list(TARGET_DIRECTORY.rglob("*.py"))
    
    # --- Define paths to exclude ---
    script_path = Path(__file__).resolve()
    excluded_dir_path = (TARGET_DIRECTORY / "test_code").resolve()
    
    # --- Filter out excluded paths ---
    python_files = [
        p for p in all_python_files
        if p.resolve() != script_path and excluded_dir_path not in p.resolve().parents
    ]

    print(f"Found {len(python_files)} Python files to process.")
    
    current_date = date.today().strftime("%Y-%m-%d")

    if args.check:
        print("\n--- CHECK MODE ---")
        all_compliant = True
        for file in python_files:
            issues, headers_for_diff = check_file_header(file, current_date)
            if issues:
                all_compliant = False
                print(f"\n Mismatches in '{file}':")
                for issue in issues:
                    print(f"  - {issue}")
                
                if headers_for_diff:
                    print("  --- Header Diff ---")
                    actual, expected = headers_for_diff
                    diff = difflib.context_diff(
                        actual.splitlines(),
                        expected.splitlines(),
                        fromfile='Original',
                        tofile='Proposed',
                    )
                    for line in diff:
                        print(f"  {line}")
        
        if all_compliant:
            print("\nSuccess: All files are compliant!")
        else:
            print(f"\nFound issues in one or more files.")

    elif args.update:
        print("\n--- UPDATE MODE ---")
        confirm = input("This will overwrite all headers. Are you sure? (y/n): ")
        if confirm.lower() != 'y':
            print("Update cancelled.")
            return
        for file in python_files:
            update_file_header(file, current_date)
        print("\nUpdate process complete.")

if __name__ == "__main__":
    main()