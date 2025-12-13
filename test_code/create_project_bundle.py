# test_tools/create_project_bundle.py
# Version: 1.3.0

import os
import datetime
import fnmatch
import argparse

def create_project_bundle(manifest_file=None):
    # --- Configuration ---
    # Root directory of the project (relative to this script)
    # Assumes script is in 'test_tools/' and project root is one level up
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Specific files to include (relative to project root)
    include_files = [
        'main_cli.py',
        'run_regression_test.py',
        'AIAgentGuidance/AIAgentWorkflow.md',
        'Dockerfile',
        'docker-compose.yml',
        '.gitignore'
    ]

    # Directories to recursively include
    include_dirs = [
        'contest_tools',
        'Utils',
        'web_app'
    ]

    # Subdirectories to EXCLUDE within the included dirs
    exclude_dirs = [
        '__pycache__',
        '.git',
        '.idea',
        '.vscode',
        'reports', # Don't include output reports
        'Logs',    # Don't include input logs
        'data',    # Don't include large data files
        'tests'    # Don't include tests unless specified
    ]
    
    # Files to EXCLUDE (by extension or exact name)
    exclude_extensions = ['.pyc', '.png', '.jpg', '.pdf', '.zip']
    exclude_filenames = ['.DS_Store']
    
    # Patterns to EXCLUDE (Shell-style wildcards)
    exclude_patterns = ['*.zip', '*cty*.dat']

    # --- Argument Handling ---
    if manifest_file:
        output_filename = "manifest_bundle.txt"
        include_dirs = []  # Disable directory scanning when using manifest
        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                # Read files, stripping whitespace and ignoring empty lines
                include_files = [line.strip() for line in f if line.strip()]
            print(f"Loaded {len(include_files)} files from manifest: {manifest_file}")
        except Exception as e:
            print(f"Error reading manifest file: {e}")
            return
    else:
        output_filename = "project_bundle.txt"

    # --- Processing ---
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        file_count = 0
        
        # 1. Process specific files (Default list or Manifest list)
        for filename in include_files:
            filepath = os.path.join(project_root, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        outfile.write(f"--- FILE: {filename} ---\n")
                        outfile.write(content)
                        outfile.write("\n")
                        file_count += 1
                        print(f"Added: {filename}")
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
            else:
                print(f"Warning: Specific file not found: {filename}")

        # 2. Process directories (Skipped if manifest is used)
        for dirname in include_dirs:
            dirpath = os.path.join(project_root, dirname)
            if not os.path.exists(dirpath):
                print(f"Warning: Directory not found: {dirname}")
                continue

            for root, dirs, files in os.walk(dirpath):
                # Modify dirs in-place to skip excluded directories
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                
                for file in files:
                    if any(file.endswith(ext) for ext in exclude_extensions):
                        continue
                    if file in exclude_filenames:
                        continue
                        
                    if any(fnmatch.fnmatch(file, pattern) for pattern in exclude_patterns):
                        continue
                        
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, project_root)
                    
                    try:
                        with open(full_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            outfile.write(f"--- FILE: {rel_path} ---\n")
                            outfile.write(content)
                            outfile.write("\n")
                            file_count += 1
                            print(f"Added: {rel_path}")
                    except UnicodeDecodeError:
                        print(f"Skipping binary file: {rel_path}")
                    except Exception as e:
                        print(f"Error reading {rel_path}: {e}")

    # Prepend Metadata
    with open(output_filename, 'r', encoding='utf-8') as f:
        existing_content = f.read()
        
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(f"# --- METADATA: FILE_COUNT={file_count} ---\n")
        f.write(existing_content)

    print(f"\nSuccessfully created '{output_filename}' with {file_count} files.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a project bundle from a manifest or defaults.")
    parser.add_argument("--manifest", help="Path to a manifest file containing a list of files to include.")
    args = parser.parse_args()
    
    create_project_bundle(manifest_file=args.manifest)