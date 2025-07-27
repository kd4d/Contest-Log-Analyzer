import os

def create_project_bundle(root_dir: str, output_file: str):
    """
    Traverses a directory to find all .py and .json files and consolidates
    them into a single text file with descriptive headers.

    Args:
        root_dir (str): The path to the root directory of the project.
        output_file (str): The name of the text file to be created.
    """
    # Define a unique header format that's easy to parse
    header_template = "--- FILE: {file_path} ---\n"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as bundle_file:
            # Walk through the directory tree starting from the root
            for dirpath, _, filenames in os.walk(root_dir):
                # Sort filenames to ensure a consistent order
                for filename in sorted(filenames):
                    if filename.endswith(('.py', '.json')):
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
    # Set the root directory to the current working directory
    # You can change this to a specific path if needed
    project_directory = '.' 
    output_filename = 'project_bundle.txt'
    create_project_bundle(project_directory, output_filename)
