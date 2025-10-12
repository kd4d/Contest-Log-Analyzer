#!/usr/bin/env python3
#
# create_project_bundle.py
#
# A utility script to bundle project files into a single text file for easy
# submission to an AI model.
#
# Version: 0.91.0-Beta
# Date: 2025-10-10
#
# --- Revision History ---
# [0.91.0-Beta] - 2025-10-10
# - Amended get_docs_files to include the root Readme.md in the documentation
#   bundle.
# [1.0.2-Beta] - 2025-09-28
# - Updated get_data_files to use os.walk to correctly find files in
#   subdirectories.
# [1.0.1-Beta] - 2025-09-28
# - Fixed a bug where --txt and --data flags failed to find their
#   respective directories. The script now correctly uses the
#   CONTEST_INPUT_DIR environment variable as the base path, per project
#   architecture standards.
# [1.0.0-Beta] - 2025-09-28
# - Added a metadata header to the bundle output to include a file count,
#   improving the robustness of the AI's initialization protocol.
#

import os
import argparse


def create_bundle(file_paths, bundle_file_path):
    """Creates a bundle file from a list of file paths."""
    with open(bundle_file_path, "w", encoding="utf-8") as bundle_file:
        file_count = len(file_paths)
        bundle_file.write(f"# --- METADATA: FILE_COUNT={file_count} ---\n")
        for file_path in file_paths:
            relative_path = os.path.relpath(file_path, ".").replace("\\", "/")
            bundle_file.write(f"--- FILE: {relative_path} ---\n")
            with open(file_path, "r", encoding="utf-8") as f:
                bundle_file.write(f.read())
            bundle_file.write("\n")
    print(f"Created bundle: {bundle_file_path}")


def get_project_files():
    """Returns a list of all .py and .json files in the project."""
    project_files = []
    for root, _, files in os.walk("."):
        if "test_code" in root or "CONTEST_LOGS_REPORTS" in root:
            continue
        for file in files:
            if file.endswith((".py", ".json")):
                project_files.append(os.path.join(root, file))
    return project_files


def get_docs_files():
    """Returns a list of Readme.md and all .md files in the Docs/ directory."""
    docs_files = []
    docs_dir = "Docs"
    if os.path.isdir(docs_dir):
        for file in os.listdir(docs_dir):
            if file.endswith(".md"):
                docs_files.append(os.path.join(docs_dir, file))
    if os.path.isfile("Readme.md"):
        docs_files.append("Readme.md")
    return docs_files


def get_data_files():
    """Returns a list of all .dat files in the data/ directory."""
    data_files = []
    in_dir = os.environ.get('CONTEST_INPUT_DIR')
    data_dir = os.path.join(in_dir, "data")
    if os.path.isdir(data_dir):
        for root, _, files in os.walk(data_dir):
            for file in files:
                if file.endswith(".dat") and not file.startswith("cty"):
                    data_files.append(os.path.join(root, file))
    return data_files


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Bundle project files into a single text file."
    )
    parser.add_argument(
        "--txt", action="store_true", help="Bundle documentation files (.md)."
    )
    parser.add_argument(
        "--data", action="store_true", help="Bundle data files (.dat)."
    )
    args = parser.parse_args()

    if args.txt:
        files_to_bundle = get_docs_files()
        bundle_name = "documentation_bundle.txt"
    elif args.data:
        files_to_bundle = get_data_files()
        bundle_name = "data_bundle.txt"
    else:
        files_to_bundle = get_project_files()
        bundle_name = "project_bundle.txt"

    if files_to_bundle:
        create_bundle(files_to_bundle, bundle_name)
    else:
        print(f"No files found to create {bundle_name}.")


if __name__ == "__main__":
    main()