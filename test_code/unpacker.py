# unpacker.py
import os
import re
import argparse

def unpack_project_bundle(bundle_file: str, output_dir: str = '.'):
    """
    Parses a bundled text file and recreates the original directory and file structure.

    Args:
        bundle_file (str): The path to the input bundle text file.
        output_dir (str): The root directory where files will be unpacked.
    """
    try:
        with open(bundle_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Bundle file not found at '{bundle_file}'")
        return
    except Exception as e:
        print(f"Error reading bundle file: {e}")
        return

    # A regex pattern to find the file headers and capture the path
    header_pattern = r'--- FILE: (.*?) ---'
    
    # Split the bundle by the header. This results in a list where the
    # content for a file is the item *after* its header.
    parts = re.split(header_pattern, content)
    
    # The text *before the first header* is in parts[0], so we start the loop at index 1.
    # The paths are at odd indices (1, 3, 5, ...) and content is at even indices (2, 4, 6, ...)
    if len(parts) < 3:
        print("Error: No valid file headers and content found in the bundle.")
        return

    file_paths = parts[1::2]
    file_contents = parts[2::2]

    for relative_path, file_content in zip(file_paths, file_contents):
        # Clean up the path and content
        relative_path = relative_path.strip()
        # The bundler adds a newline before and after the content of each file.
        # We strip leading/trailing whitespace to restore the original content.
        file_content = file_content.strip()

        # Create the full path for the output file
        output_path = os.path.join(output_dir, relative_path)
        
        # Ensure the directory structure exists
        dir_name = os.path.dirname(output_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        
        try:
            with open(output_path, 'w', encoding='utf-8', newline='\n') as f_out:
                f_out.write(file_content)
            print(f"Created: {output_path}")
        except Exception as e:
            print(f"Error writing file '{output_path}': {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Unpack a project bundle created with the '--- FILE: ... ---' format."
    )
    parser.add_argument(
        "bundle_file", 
        help="The path to the project bundle file (e.g., 'bundle.txt')."
    )
    parser.add_argument(
        "-o", "--output_dir", 
        default='unpacked_project', 
        help="The directory to unpack the files into (defaults to './unpacked_project')."
    )
    
    args = parser.parse_args()
    
    print(f"Unpacking '{args.bundle_file}' into directory '{args.output_dir}'...")
    unpack_project_bundle(args.bundle_file, args.output_dir)
    print("...Done.")