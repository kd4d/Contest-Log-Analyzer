import sys
import os

def replace_non_breaking_spaces(filepath):
    """
    Reads a file, replaces all non-breaking spaces (U+00A0)
    with regular spaces (U+0020), and overwrites the file.

    Args:
        filepath (str): The path to the file to process.
    """
    # The non-breaking space character in Unicode
    nbsp = '\u00a0'
    # The regular space character
    space = ' '

    try:
        # Read the original content of the file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if the character is present before modifying
        if nbsp in content:
            # Perform the replacement
            new_content = content.replace(nbsp, space)

            # Write the modified content back to the file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"Success: Replaced non-breaking spaces in '{filepath}'")
        else:
            print(f"Info: No non-breaking spaces found in '{filepath}'. File not modified.")

    except FileNotFoundError:
        print(f"Error: File not found at '{filepath}'")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Check if a file path was provided as a command-line argument
    if len(sys.argv) != 2:
        print("Usage: python replace_nbsp.py <file_path>")
        sys.exit(1)

    file_to_process = sys.argv[1]
    
    # Check if the provided path is a valid file
    if not os.path.isfile(file_to_process):
        print(f"Error: The path '{file_to_process}' is not a valid file.")
        sys.exit(1)
        
    replace_non_breaking_spaces(file_to_process)