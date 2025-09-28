import argparse
import os
import json
import requests
import zipfile
import io

# --- Constants ---
INDEX_FILENAME = "cty_index.json"
DATA_SUBDIR = "Data"
CTY_SUBDIR = "CTY"
USER_AGENT = "CTYFileDownloader/1.0 (Python)"

def get_cty_dat_file(zip_name: str, cty_data_path: str) -> str | None:
    """
    Ensures a specific cty.dat file is cached locally and returns its path.

    This function performs the following steps:
    1. Looks up the zip_name in the index to find its URL and final path.
    2. Checks if the .dat file already exists at that path. If so, returns it.
    3. If not, downloads the .zip file from the URL.
    4. Extracts the 'cty.dat' member from the zip archive in memory.
    5. Saves the extracted content to the correct year-specific directory.
    6. Returns the full path to the newly created file.

    Args:
        zip_name (str): The name of the zip file (e.g., 'cty-3531.zip').
        cty_data_path (str): The absolute path to the '.../Data/CTY' directory.

    Returns:
        An absolute path to the cty.dat file, or None if an error occurs.
    """
    index_path = os.path.join(cty_data_path, INDEX_FILENAME)

    # --- 1. Find the file's metadata in the index ---
    if not os.path.exists(index_path):
        print(f"Error: Index file not found at {index_path}")
        return None

    with open(index_path, 'r') as f:
        cty_index = json.load(f)

    file_entry = next((item for item in cty_index if item['zip_name'] == zip_name), None)

    if not file_entry:
        print(f"Error: Could not find '{zip_name}' in the index file.")
        return None

    local_dat_path = file_entry['local_path']
    download_url = file_entry['url']

    # --- 2. Check if the file is already cached ---
    if os.path.exists(local_dat_path):
        print(f"File is already cached.\nPath: {local_dat_path}")
        return local_dat_path

    print(f"File not found in cache. Starting download for '{zip_name}'.")

    # --- 3. Download the zip file ---
    try:
        print(f"Downloading from: {download_url}")
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(download_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: Download failed. {e}")
        return None

    # --- 4. Extract cty.dat from the zip file ---
    try:
        with zipfile.ZipFile(io.BytesIO(response.content)) as thezip:
            # The file we want is always named 'cty.dat' inside the archive
            dat_content = thezip.read('cty.dat')
        print("Successfully extracted 'cty.dat' from archive.")
    except (zipfile.BadZipFile, KeyError):
        print("Error: Failed to extract 'cty.dat' from the downloaded zip file.")
        return None
        
    # --- 5. Place the cty.dat file into the correct directory ---
    try:
        # Ensure the destination directory (e.g., .../CTY/2025/) exists
        os.makedirs(os.path.dirname(local_dat_path), exist_ok=True)
        
        with open(local_dat_path, 'wb') as f:
            f.write(dat_content)
        print(f"File successfully saved.\nPath: {local_dat_path}")
    except IOError as e:
        print(f"Error: Could not write file to disk. {e}")
        return None

    return local_dat_path

def main():
    """ Main function to parse arguments and run the fetcher. """
    parser = argparse.ArgumentParser(
        description="Downloads a specific cty.dat file using a pre-built index."
    )
    parser.add_argument(
        "filename",
        help="The name of the .zip file to fetch (e.g., 'cty-3531.zip')."
    )
    args = parser.parse_args()

    contest_input_dir = os.getenv("CONTEST_INPUT_DIR")
    if not contest_input_dir:
        raise EnvironmentError("Error: CONTEST_INPUT_DIR environment variable is not set.")

    cty_data_path = os.path.join(contest_input_dir, DATA_SUBDIR, CTY_SUBDIR)

    # Run the main function and print the result
    get_cty_dat_file(args.filename, cty_data_path)

if __name__ == "__main__":
    main()