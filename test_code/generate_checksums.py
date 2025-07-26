# Contest Log Analyzer/test_code/generate_checksums.py
#
# Purpose: This utility calculates and displays the SHA-256 checksum for all
#          .py and .json files within the Contest Log Analyzer project,
#          excluding the 'test_code' directory itself. This is used to
#          verify that file versions are consistent.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-26
# Version: 1.0.0
#
# Copyright (c) 2025 Mark Bailey, KD4D
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)

import os
import hashlib

def calculate_sha256(filepath):
    """Calculates the SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            # Read and update hash in chunks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except IOError as e:
        return f"Error reading file: {e}"

def main():
    """
    Main function to walk the project directory and generate checksums.
    """
    print("--- Contest Log Analyzer File Checksums (SHA-256) ---")
    
    # The script is in 'test_code', so the project root is the parent directory.
    script_path = os.path.realpath(__file__)
    test_code_dir = os.path.dirname(script_path)
    project_root = os.path.dirname(test_code_dir)

    print(f"Scanning project root: {project_root}\n")

    file_hashes = []

    for root, dirs, files in os.walk(project_root):
        # Exclude the test_code directory from the search
        if os.path.basename(root) == 'test_code':
            continue
            
        # Also exclude __pycache__ directories
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')

        for filename in sorted(files):
            if filename.endswith(".py") or filename.endswith(".json"):
                full_path = os.path.join(root, filename)
                relative_path = os.path.relpath(full_path, project_root).replace('\\', '/')
                
                file_hash = calculate_sha256(full_path)
                file_hashes.append((relative_path, file_hash))

    # Print the results in a formatted table
    if file_hashes:
        # Find the longest path for alignment
        max_path_len = max(len(path) for path, h in file_hashes)
        
        print(f"{'File Path':<{max_path_len}}   {'SHA-256 Checksum'}")
        print(f"{'-' * max_path_len}   {'-' * 64}")
        
        for path, h in file_hashes:
            print(f"{path:<{max_path_len}}   {h}")
    else:
        print("No Python or JSON files found to checksum.")

if __name__ == "__main__":
    main()
